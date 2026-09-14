"""
ATHLETIX — Data Models: Scouting, Leaderboard & Verification Schemas
backend/app/models/scouting.py

Pydantic schemas governing athletic rankings, scout shortlisting, and verification workflows.

Models Included:
- LeaderboardEntry: Formatted ranking metrics for athletes across exercises and sports categories.
- VerifyRequest / VerificationResponseItem: Official direct verification endorsement schemas.
- VerificationReviewRequest / VerificationRequestItem: Multi-step athlete proof verification and admin approval workflow.
- ShortlistRequest / ShortlistResponseItem: Scouting bookmarks created by talent scouts and sports officials.
"""

from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)


# ─── Leaderboard Schemas ──────────────────────────────────────────────────────
class LeaderboardEntry(BaseModel):
    """
    Individual ranked entry displayed on the regional and global leaderboards.
    """
    sport: str
    exercise: str
    athlete_id: str
    athlete_name: str
    athlete_location: str | None = None
    score: float
    rep_count: int | None = None
    assessed_at: str
    rank: int
    is_verified: bool = False


# ─── Official Direct Verification Schemas ─────────────────────────────────────
class VerifyRequest(BaseModel):
    """
    Direct verification payload submitted by authorized sports officials.
    """
    athlete_id: str
    video_id: str
    exercise: str

    @field_validator(
        "athlete_id",
        "video_id",
        "exercise",
    )
    @classmethod
    def verification_fields_not_empty(
        cls,
        value: str,
    ) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be blank.")
        return cleaned


class VerificationResponseItem(BaseModel):
    """
    Confirmation response for an approved official verification record.
    """
    id: str
    athlete_id: str
    official_id: str
    video_id: str
    exercise: str
    verified_at: str


# ─── Athlete Verification Request Workflow Schemas ────────────────────────────
VerificationRequestStatus = Literal[
    "pending",
    "approved",
    "rejected",
]

VerificationReviewStatus = Literal[
    "approved",
    "rejected",
]


class VerificationReviewRequest(BaseModel):
    """
    Review action payload used by administrators to approve or reject athlete badge claims.
    """
    status: VerificationReviewStatus
    review_note: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator("review_note")
    @classmethod
    def clean_review_note(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def validate_review_decision(self):
        if self.status == "rejected" and (self.review_note is None or len(self.review_note) < 3):
            raise ValueError("A rejection reason of at least 3 characters is required.")
        return self


class VerificationRequestItem(BaseModel):
    """
    Data model representing an athlete's formal verification claim and submitted proofs.
    """
    id: str
    athlete_id: str
    video_id: str
    exercise: str
    details: str
    document_paths: list[str]
    status: VerificationRequestStatus
    reviewed_by: str | None = None
    review_note: str | None = None
    created_at: str
    updated_at: str
    reviewed_at: str | None = None


class VerificationDocumentItem(BaseModel):
    """
    Signed, time-limited document download URL for reviewing supporting verification files.
    """
    path: str
    signed_url: str
    expires_in: int


# ─── Talent Scout Shortlist Schemas ───────────────────────────────────────────
class ShortlistRequest(BaseModel):
    """
    Payload for talent scouts bookmarking an athlete for regional/national trials.
    """
    athlete_id: str
    sport: Literal[
        "powerlifting",
        "calisthenics",
    ]

    @field_validator("athlete_id")
    @classmethod
    def athlete_id_not_empty(
        cls,
        value: str,
    ) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Athlete ID cannot be blank.")
        return cleaned


class ShortlistResponseItem(BaseModel):
    """
    Shortlisted athlete summary record returned to officials.
    """
    id: str
    official_id: str
    athlete_id: str
    sport: str
    created_at: str
    athlete: dict | None = None