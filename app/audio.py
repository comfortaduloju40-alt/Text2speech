"""
Audio pipeline: splits long text into TTS-safe chunks, synthesizes each
chunk via the active engine, concatenates them, applies speed
adjustment, and converts to the user's chosen format — all via ffmpeg.

ffmpeg must be installed on the host (handled in the Dockerfile for
Railway; install separately for local dev).
"""

import os
import re
import shutil
import subprocess
import tempfile
import uuid

from app.logger import get_logger
from app.tts.base import TTSEngine

logger = get_logger(__name__)


def chunk_text(text: str, max_len: int = 800) -> list[str]:
    """
    Splits text into chunks under max_len characters, breaking on
    sentence boundaries where possible. Falls back to a hard split for
    single sentences longer than max_len (rare, but possible with no
    punctuation).
    """
    text = text.strip()
    if len(text) <= max_len:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(sentence) > max_len:
            if current:
                chunks.append(current.strip())
                current = ""
            for i in range(0, len(sentence), max_len):
                chunks.append(sentence[i : i + max_len].strip())
            continue

        if len(current) + len(sentence) + 1 <= max_len:
            current = f"{current} {sentence}".strip()
        else:
            chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return [c for c in chunks if c]


def _build_atempo_filter(speed: float) -> str | None:
    """
    ffmpeg's atempo filter only accepts 0.5-2.0 per instance, so speeds
    outside that range need multiple atempo filters chained together.
    """
    if speed == 1.0:
        return None

    filters = []
    remaining = speed
    while remaining > 2.0:
        filters.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        filters.append("atempo=0.5")
        remaining /= 0.5
    filters.append(f"atempo={remaining:.3f}")
    return ",".join(filters)


def synthesize_speech(
    engine: TTSEngine,
    text: str,
    voice_id: str,
    language_code: str,
    speed: float,
    output_format: str,
) -> tuple[str, str]:
    """
    Runs the full pipeline and returns (final_audio_path, tmp_dir).
    Caller is responsible for calling cleanup_dir(tmp_dir) when done
    (use a try/finally — see app/handlers/tts.py).

    This function is synchronous/blocking (network calls + subprocess),
    so callers running inside an async handler should wrap it in
    asyncio.to_thread().
    """
    tmp_dir = tempfile.mkdtemp(prefix="tts_")
    chunks = chunk_text(text)
    part_paths = []

    try:
        for i, chunk in enumerate(chunks):
            audio_bytes = engine.synthesize(chunk, voice_id, language_code)
            part_path = os.path.join(tmp_dir, f"part_{i}.{engine.native_format}")
            with open(part_path, "wb") as f:
                f.write(audio_bytes)
            part_paths.append(part_path)

        if len(part_paths) == 1:
            concat_path = part_paths[0]
        else:
            concat_path = os.path.join(tmp_dir, f"concat.{engine.native_format}")
            list_file = os.path.join(tmp_dir, "concat_list.txt")
            with open(list_file, "w") as f:
                for p in part_paths:
                    f.write(f"file '{p}'\n")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", concat_path],
                check=True,
                capture_output=True,
            )

        final_path = os.path.join(tmp_dir, f"output_{uuid.uuid4().hex[:8]}.{output_format}")
        cmd = ["ffmpeg", "-y", "-i", concat_path]

        atempo_filter = _build_atempo_filter(speed)
        if atempo_filter:
            cmd += ["-filter:a", atempo_filter]

        cmd += [final_path]
        subprocess.run(cmd, check=True, capture_output=True)

        return final_path, tmp_dir

    except subprocess.CalledProcessError as e:
        logger.error("ffmpeg failed: %s", e.stderr.decode(errors="replace") if e.stderr else e)
        cleanup_dir(tmp_dir)
        raise
    except Exception:
        cleanup_dir(tmp_dir)
        raise


def cleanup_dir(tmp_dir: str) -> None:
    """Deletes a temp directory and everything in it. Never raises."""
    shutil.rmtree(tmp_dir, ignore_errors=True)
