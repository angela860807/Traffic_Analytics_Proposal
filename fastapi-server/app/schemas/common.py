from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    detail: str = Field(examples=["image must be jpeg or png"])


class FieldError(BaseModel):
    field: str
    reason: str


class ApiErrorResponse(BaseModel):
    timestamp: AwareDatetime
    status: int = Field(ge=400, le=599)
    code: str
    message: str
    request_id: str = Field(alias="requestId")
    field_errors: list[FieldError] = Field(
        default_factory=list,
        alias="fieldErrors",
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")
