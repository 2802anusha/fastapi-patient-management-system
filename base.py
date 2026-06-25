from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Annotated, Literal, Optional
from fastapi.params import Body
import json

app = FastAPI()


# -----------------------------
# Patient Model
# -----------------------------
class Patient(BaseModel):
    name: str
    city: str
    age: int
    gender: Literal['male', 'female', 'other']
    height: float
    weight: float


class PatientUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Literal['male', 'female', 'other']] = None
    height: Optional[float] = None
    weight: Optional[float] = None


# -----------------------------
# Helper Functions
# -----------------------------
def load_data():
    try:
        with open("patients.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)


def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 2)


def bmi_verdict(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():
    return {"message": "Patient Management API Running"}


# -----------------------------
# View Patients (with Search)
# -----------------------------
@app.get("/view")
def view(
    name: Optional[str] = Query(
        default=None,
        description="Search patient by name"
    )
):
    data = load_data()

    # Return all patients if no search query
    if not name:
        return data

    # Search by patient name (case-insensitive)
    filtered_data = {
        patient_id: patient
        for patient_id, patient in data.items()
        if name.lower() in patient["name"].lower()
    }

    return filtered_data
# -----------------------------
# Dashboard Analytics
# -----------------------------
@app.get("/dashboard")
def dashboard():
    data = load_data()

    if not data:
        raise HTTPException(status_code=404, detail="No patient data found.")

    bmi_values = [patient["bmi"] for patient in data.values()]

    total_patients = len(data)
    average_bmi = round(sum(bmi_values) / total_patients, 2)
    highest_bmi = max(bmi_values)
    lowest_bmi = min(bmi_values)

    return {
        "total_patients": total_patients,
        "average_bmi": average_bmi,
        "highest_bmi": highest_bmi,
        "lowest_bmi": lowest_bmi
    }


# -----------------------------
# Create Patient
# -----------------------------
@app.post("/create")
def create_patient(
    id: Annotated[str, Body(embed=True)],
    patient: Patient
):
    data = load_data()

    if id in data:
        raise HTTPException(status_code=400, detail="Patient already exists.")

    bmi = calculate_bmi(patient.weight, patient.height)

    data[id] = {
        **patient.model_dump(),
        "bmi": bmi,
        "verdict": bmi_verdict(bmi)
    }

    save_data(data)

    return {"message": "Patient created successfully."}


# -----------------------------
# Update Patient
# -----------------------------
@app.put("/edit/{patient_id}")
def update_patient(patient_id: str, patient: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found.")

    stored_patient = data[patient_id]

    update_data = patient.model_dump(exclude_unset=True)

    stored_patient.update(update_data)

    bmi = calculate_bmi(
        stored_patient["weight"],
        stored_patient["height"]
    )

    stored_patient["bmi"] = bmi
    stored_patient["verdict"] = bmi_verdict(bmi)

    data[patient_id] = stored_patient

    save_data(data)

    return {"message": "Patient updated successfully."}


# -----------------------------
# Delete Patient
# -----------------------------
@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found.")

    del data[patient_id]

    save_data(data)

    return {"message": "Patient deleted successfully."}