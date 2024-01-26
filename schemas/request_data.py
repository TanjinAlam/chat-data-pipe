from pydantic import BaseModel, Field

class request_data(BaseModel):
    text: str = Field(..., description="text")
    id: str = Field(..., description="id")