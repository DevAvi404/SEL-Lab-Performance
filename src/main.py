from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Student Management API",
    description="A simple CRUD API for managing student records",
    version="1.0.0",
)

class Student(BaseModel):
    id: int
    name: str
    department: str
    semester: int = Field(..., gt=0, le=12, description="Semester must be between 1 and 12")
    cgpa: float = Field(..., ge=0.0, le=4.0, description="CGPA must be between 0.0 and 4.0")


class StudentUpdate(BaseModel):
    """All fields optional, used for partial updates via PUT."""
    name: Optional[str] = None
    department: Optional[str] = None
    semester: Optional[int] = Field(None, gt=0, le=12)
    cgpa: Optional[float] = Field(None, ge=0.0, le=4.0)

students_db: Dict[int, Student] = {}

@app.get("/")
def root():
    return {"message": "Welcome to the Student Management API"}


@app.get("/students", response_model=List[Student])
def get_all_students():
    """Return every student currently stored."""
    return list(students_db.values())


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    """Return a single student by id, or 404 if not found."""
    student = students_db.get(student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student


@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
def create_student(student: Student):
    """Create a new student. Fails if the id is already taken."""
    if student.id in students_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with id {student.id} already exists",
        )
    students_db[student.id] = student
    return student


@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, update: StudentUpdate):
    """Update an existing student's fields. Fails with 404 if not found."""
    existing = students_db.get(student_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    update_data = update.model_dump(exclude_unset=True)
    updated_student = existing.model_copy(update=update_data)
    students_db[student_id] = updated_student
    return updated_student


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: int):
    """Delete a student by id. Fails with 404 if not found."""
    if student_id not in students_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    del students_db[student_id]
    return {"message": f"Student {student_id} deleted successfully"}