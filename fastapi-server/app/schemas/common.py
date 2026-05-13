from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    detail: str = Field(examples=["image must be jpeg or png"])