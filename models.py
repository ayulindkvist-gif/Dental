"""
Pydantic модели данных для DentalCare App API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AppointmentStatus(str, Enum):
    """Статусы записи на приём"""
    PENDING = "pending"  # Ожидает подтверждения
    CONFIRMED = "confirmed"  # Подтверждена
    COMPLETED = "completed"  # Проведена
    CANCELLED_BY_PATIENT = "cancelled_by_patient"  # Отменена пациентом
    CANCELLED_BY_CLINIC = "cancelled_by_clinic"  # Отменена клиникой


class DoctorSpecialization(str, Enum):
    """Специализации врачей"""
    ORTHODONTIST = "orthodontist"  # Ортодонт
    SURGEON = "surgeon"  # Хирург
    THERAPIST = "therapist"  # Терапевт
    PERIODONTIST = "periodontist"  # Пародонтолог
    ORTHOPEDIST = "orthopedist"  # Ортопед


class ResultType(str, Enum):
    """Типы результатов обследований"""
    XRAY = "xray"  # Рентген
    CT = "ct"  # КТ
    PHOTO = "photo"  # Фото
    CONCLUSION = "conclusion"  # Заключение


# ========== Doctor Models ==========

class DoctorBase(BaseModel):
    """Базовая модель врача"""
    id: int
    first_name: str
    last_name: str
    specialization: DoctorSpecialization
    experience_years: int
    photo_url: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5, description="Рейтинг врача от 0 до 5")
    reviews_count: Optional[int] = Field(None, ge=0, description="Количество отзывов")


class DoctorWithSchedule(DoctorBase):
    """Врач с доступными слотами расписания"""
    available_slots: List[datetime] = []


# ========== Patient Models ==========

class PatientBase(BaseModel):
    """Базовая модель пациента"""
    id: int
    first_name: str
    last_name: str
    phone: str
    email: Optional[str] = None
    birth_date: Optional[str] = None


# ========== Appointment Models ==========

class AppointmentCreate(BaseModel):
    """Модель для создания записи на приём"""
    patient_id: int
    doctor_id: int
    appointment_time: datetime
    service_type: str = Field(..., example="Консультация ортодонта")
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Модель ответа с информацией о записи"""
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    doctor_name: str
    appointment_time: datetime
    service_type: str
    status: AppointmentStatus
    notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    recommendations: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AppointmentUpdate(BaseModel):
    """Модель для обновления записи"""
    status: Optional[AppointmentStatus] = None
    appointment_time: Optional[datetime] = None
    notes: Optional[str] = None


class AppointmentComplete(BaseModel):
    """Модель для завершения приёма врачом"""
    diagnosis: Optional[str] = Field(None, example="Кариес 36 зуба")
    treatment: Optional[str] = Field(None, example="Пломбирование композитным материалом")
    recommendations: Optional[str] = Field(None, example="Контрольный осмотр через 6 месяцев")
    notes: Optional[str] = None


# ========== Medical Results Models ==========

class MedicalResultCreate(BaseModel):
    """Модель для создания результата обследования"""
    patient_id: int
    doctor_id: int
    result_type: ResultType
    title: str = Field(..., example="Панорамный снимок")
    description: Optional[str] = None
    file_url: str = Field(..., example="https://s3.example.com/results/12345.jpg")


class MedicalResultResponse(BaseModel):
    """Модель ответа с результатом обследования"""
    id: int
    patient_id: int
    doctor_id: int
    doctor_name: str
    result_type: ResultType
    title: str
    description: Optional[str] = None
    file_url: str
    created_at: datetime


# ========== Service Models ==========

class ServiceResponse(BaseModel):
    """Модель услуги клиники"""
    id: int
    name: str
    description: Optional[str] = None
    price: float = Field(..., ge=0, description="Цена услуги в рублях")
    duration_minutes: int = Field(..., ge=0, description="Длительность процедуры в минутах")
    specialization: Optional[DoctorSpecialization] = None


# ========== Review Models ==========

class ReviewCreate(BaseModel):
    """Модель для создания отзыва"""
    patient_id: int
    doctor_id: int
    appointment_id: int
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    """Модель отзыва"""
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    appointment_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime


# ========== Notification Models ==========

class NotificationType(str, Enum):
    """Типы уведомлений"""
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    APPOINTMENT_REMINDER = "appointment_reminder"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_RESCHEDULED = "appointment_rescheduled"
    RESULT_UPLOADED = "result_uploaded"
    APPOINTMENT_COMPLETED = "appointment_completed"


class NotificationResponse(BaseModel):
    """Модель уведомления"""
    id: int
    user_id: int
    notification_type: NotificationType
    title: str
    message: str
    is_read: bool = False
    related_id: Optional[int] = None  # ID связанной записи/результата
    created_at: datetime


# ========== Response Models ==========

class SuccessResponse(BaseModel):
    """Стандартный успешный ответ"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Стандартный ответ с ошибкой"""
    success: bool = False
    error: str
    details: Optional[str] = None


# ========== Patient History Models ==========

class PatientHistoryResponse(BaseModel):
    """Полная история пациента"""
    patient: PatientBase
    appointments: List[AppointmentResponse] = []
    medical_results: List[MedicalResultResponse] = []
    total_appointments: int = 0
    completed_appointments: int = 0
    upcoming_appointments: int = 0


# ========== Doctor Statistics Models ==========

class DoctorStatisticsResponse(BaseModel):
    """Статистика работы врача"""
    doctor_id: int
    doctor_name: str
    total_appointments: int = 0
    completed_appointments: int = 0
    upcoming_appointments: int = 0
    cancelled_appointments: int = 0
    average_rating: Optional[float] = None
    total_reviews: int = 0
    patients_served: int = 0  # Уникальных пациентов

