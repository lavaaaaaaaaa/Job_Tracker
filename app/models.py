from enum import Enum
from pydantic import BaseModel, Field

class StatusEnum(str, Enum):
    offer = "Offer"
    interview = "Interview"
    applied = "Applied"
    rejected = "Rejected"
    assessment = "Assessment"
    ghosted = "Ghosted"

class Job(BaseModel):
    company:str = Field(..., min_length = 1, max_length = 100)
    role:str = Field(..., min_length = 1, max_length = 100)
    status:StatusEnum = Field(..., description = "Current stage of the candidate")
    location: str | None = None
    work_mode: str | None = None
    job_url: str | None = None
    salary: str | None = None

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

    
