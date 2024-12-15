from pydantic import BaseModel, HttpUrl, ValidationError
from typing import Optional


class JobPosting(BaseModel):
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    job_link: Optional[HttpUrl] = None

class JobSearchInput(BaseModel):
    job: str
    location: str

    def build_url(self) -> str:
        """Generate the Indeed job search URL dynamically."""
        base_url = "https://www.indeed.com/jobs"
        query_params = f"?q={self.job}&l={self.location}"
        return f"{base_url}{query_params}"