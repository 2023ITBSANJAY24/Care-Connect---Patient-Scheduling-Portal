from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
    password: str
    role: str

@dataclass
class Doctor:
    id: int
    name: str
    specialization: str
    experience: str
    email: str

@dataclass
class Appointment:
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    date: str
    time: str
    symptoms: str
    status: str
