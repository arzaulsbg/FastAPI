from pydantic import BaseModel, Field, EmailStr, field_validator


# Schema for creating a student
class StudentCreate(BaseModel):
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=3, max_length=30)
    age: int = Field(..., ge=10, le=100)
    department: str = Field(..., min_length=3, max_length=30)
    semester: str = Field(..., min_length=3, max_length=30)
    email: str
    marks: float = Field(..., ge=0, le=100)
    city: str = Field(..., min_length=3, max_length=30)

    @field_validator("name", "department", "semester", "city")
    @classmethod
    def clean_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value


# Schema for PUT (complete update)
class StudentUpdate(BaseModel):
    name: str = Field(..., min_length=3, max_length=30)
    age: int = Field(..., ge=10, le=100)
    department: str = Field(..., min_length=3, max_length=30)
    semester: str = Field(..., min_length=3, max_length=30)
    email: str
    marks: float = Field(..., ge=0, le=100)
    city: str = Field(..., min_length=3, max_length=30)

    @field_validator("name", "department", "semester", "city")
    @classmethod
    def clean_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value


# Schema for PATCH (partial update)
class StudentPatch(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=30)
    age: int | None = Field(None, ge=10, le=100)
    department: str | None = Field(None, min_length=3, max_length=30)
    semester: str | None = Field(None, min_length=3, max_length=30)
    email: str | None = None
    marks: float | None = Field(None, ge=0, le=100)
    city: str | None = Field(None, min_length=3, max_length=30)

    @field_validator("name", "department", "semester", "city")
    @classmethod
    def clean_text(cls, value):
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Field cannot be empty")
        return value


# Schema for response
class StudentResponse(BaseModel):
    id: int
    name: str
    age: int
    department: str
    semester: str
    email: str
    marks: float
    city: str