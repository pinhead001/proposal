from pydantic import BaseModel, Field, field_validator
from app.core.config import MAX_RFP_LENGTH


class PipelineRequest(BaseModel):
    rfp_text: str = Field(..., min_length=1, description="The RFP text to respond to")
    proposal_texts: list[str] | None = Field(
        None, description="Past proposal texts for style analysis (optional if proposals were uploaded)"
    )

    @field_validator("rfp_text")
    @classmethod
    def validate_rfp_length(cls, v):
        if len(v) > MAX_RFP_LENGTH:
            raise ValueError(f"RFP text exceeds maximum length of {MAX_RFP_LENGTH:,} characters")
        return v


class SectionResponse(BaseModel):
    title: str
    content: str


class PipelineResponse(BaseModel):
    sections: list[SectionResponse]


class ExportRequest(BaseModel):
    sections: list[SectionResponse] = Field(
        ..., min_length=1, description="Proposal sections to export"
    )


class UploadResponse(BaseModel):
    message: str
    file_count: int
    extracted_texts: list[str]


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
