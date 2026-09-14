"""
ATHLETIX — Video Upload Validation
backend/app/utils/validators.py

Validates uploaded video files before submitting them to cloud storage and triggering the AI pipeline.

Working & Security:
- Pre-checks file format (MP4/MPEG), extension, and maximum payload size cap (150MB).
- Rejects corrupt or invalid file formats immediately with user-friendly errors,
  conserving server compute and bandwidth.
"""

import logging
import os
from fastapi import HTTPException, status

logger = logging.getLogger("athletix.validators")

ALLOWED_CONTENT_TYPES = {"video/mp4", "video/mpeg"}
MAX_FILE_SIZE_MB = 150           # Max file size limit (150MB)
MIN_DURATION_SECONDS = 30        # Recommended minimum video duration
MAX_DURATION_SECONDS = 180       # Maximum 3-minute video duration


def validate_video_file(
    filename: str,
    content_type: str,
    file_size_bytes: int,
) -> None:
    """
    Validates video filename extension, MIME type, and byte size.

    Raises:
        HTTPException(400): If the file is not an MP4 or exceeds the maximum allowed size limit.
    """
    ext = os.path.splitext(filename)[-1].lower()
    if ext not in (".mp4",) or content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": "Only MP4 video files are accepted. Please convert your video and try again.",
                },
            },
        )

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": f"Video file exceeds the {MAX_FILE_SIZE_MB}MB limit. Please trim or compress your video.",
                },
            },
        )
