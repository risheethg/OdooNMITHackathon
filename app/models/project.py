from pydantic import BaseModel, Field, field_validator

class Project(BaseModel):
    project_id = str()
    project_name = str()