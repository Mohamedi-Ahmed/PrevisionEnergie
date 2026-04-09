from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    database: str
