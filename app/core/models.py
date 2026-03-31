from pydantic import BaseModel, Field


class PipelineRequest(BaseModel):
    rfp_text: str = Field(..., min_length=1, description="The RFP text to respond to")
    proposal_texts: list[str] | None = Field(
        None, description="Past proposal texts for style analysis (optional if proposals were uploaded)"
    )


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
