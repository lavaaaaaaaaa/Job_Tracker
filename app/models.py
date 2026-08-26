from pydantic import BaseModel
class Job(BaseModel):
    company:str
    role:str
    status:str
    location: str | None = None
    work_mode: str | None = None
    job_url: str | None = None
    salary: str | None = None

    