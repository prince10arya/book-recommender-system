"""
preprocessing_service/app/schemas/preprocess_schema.py
--------------------------------------------------------
Pydantic validation models for the Preprocessing Service.

These extend or re-export the shared models with additional validators
and OpenAPI metadata where needed.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class PreprocessRequest(BaseModel):
    """
    Optional request body for POST /preprocess.

    All fields are optional — the pipeline can be triggered with a plain
    empty POST. Clients may supply overrides for advanced use cases.
    """

    force: bool = Field(
        default=False,
        description="Force re-run even if artifacts already exist.",
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class UploadResponse(BaseModel):
    """Response returned by POST /upload after a successful CSV upload."""

    success: bool
    filename: str
    rows: int = Field(..., ge=0, description="Number of rows in the uploaded CSV.")
    size_kb: int = Field(..., ge=0, description="File size in kilobytes.")
    message: str


class PreprocessStatus(BaseModel):
    """Current state of preprocessing artifacts on the shared volume."""

    cleaned_csv_exists: bool
    tagged_txt_exists: bool
    row_count: int | None = Field(
        default=None, description="Row count of cleaned CSV (null when not yet created)."
    )
    message: str


class PreprocessResponse(BaseModel):
    """Result returned by POST /preprocess after the ETL pipeline completes."""

    success: bool
    rows_processed: int = Field(..., ge=0)
    rows_after_clean: int = Field(..., ge=0)
    message: str

    @field_validator("rows_after_clean")
    @classmethod
    def rows_after_must_not_exceed_input(cls, v: int, info) -> int:
        raw = info.data.get("rows_processed")
        if raw is not None and v > raw:
            raise ValueError("rows_after_clean cannot exceed rows_processed")
        return v
