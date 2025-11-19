from pydantic import BaseModel, Field


class CredentialsSchema(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")
