import pytest
from fastapi.testclient import TestClient

from main import app, students_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    """Ensure each test starts with a clean in-memory database."""
    students_db.clear()
    yield
    students_db.clear()


SAMPLE_STUDENT = {
    "id": 1,
    "name": "Alice Rahman",
    "department": "CSE",
    "semester": 4,
    "cgpa": 3.75,
}


def test_create_student_success():
    response = client.post("/students", json=SAMPLE_STUDENT)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Alice Rahman"

def test_create_student_duplicate_id_fails():
    """Invalid scenario 1: creating a student with an id that already exists."""
    client.post("/students", json=SAMPLE_STUDENT)
    response = client.post("/students", json=SAMPLE_STUDENT)
    assert response.status_code == 400


def test_create_student_invalid_cgpa_fails():
    """Invalid scenario 2: cgpa outside the allowed 0.0-4.0 range."""
    bad_student = {**SAMPLE_STUDENT, "id": 2, "cgpa": 5.5}
    response = client.post("/students", json=bad_student)
    assert response.status_code == 422


def test_create_student_invalid_semester_fails():
    """Invalid scenario 3 (bonus): semester value of 0 or negative is invalid."""
    bad_student = {**SAMPLE_STUDENT, "id": 3, "semester": -1}
    response = client.post("/students", json=bad_student)
    assert response.status_code == 422


def test_create_student_missing_field_fails():
    """Invalid scenario 4 (bonus): required field missing from the payload."""
    incomplete = {"id": 4, "name": "No Department"}
    response = client.post("/students", json=incomplete)
    assert response.status_code == 422


def test_get_all_students_success():
    client.post("/students", json=SAMPLE_STUDENT)
    response = client.get("/students")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_all_students_empty():
    response = client.get("/students")
    assert response.status_code == 200
    assert response.json() == []


def test_get_student_success():
    client.post("/students", json=SAMPLE_STUDENT)
    response = client.get("/students/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice Rahman"


def test_get_student_not_found_fails():
    response = client.get("/students/999")
    assert response.status_code == 404

def test_update_student_success():
    client.post("/students", json=SAMPLE_STUDENT)
    response = client.put("/students/1", json={"cgpa": 3.95, "semester": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["cgpa"] == 3.95
    assert data["semester"] == 5
    # Unchanged fields should remain the same
    assert data["name"] == "Alice Rahman"

def test_update_student_not_found_fails():
    response = client.put("/students/999", json={"cgpa": 3.5})
    assert response.status_code == 404

def test_update_student_invalid_data_fails():
    client.post("/students", json=SAMPLE_STUDENT)
    response = client.put("/students/1", json={"cgpa": -1.0})
    assert response.status_code == 422

def test_delete_student_success():
    client.post("/students", json=SAMPLE_STUDENT)
    response = client.delete("/students/1")
    assert response.status_code == 200
    # Confirm it's actually gone
    follow_up = client.get("/students/1")
    assert follow_up.status_code == 404


def test_delete_student_not_found_fails():
    response = client.delete("/students/999")
    assert response.status_code == 404