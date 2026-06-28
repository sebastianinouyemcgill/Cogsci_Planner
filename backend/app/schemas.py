from pydantic import BaseModel

class CourseCreate(BaseModel):
    code: str
    title: str

class CourseOut(BaseModel):
    id: int
    code: str
    title: str

    class Config:
        from_attributes = True