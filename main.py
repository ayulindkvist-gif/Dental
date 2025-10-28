"""
DentalCare App - FastAPI Backend
Демонстрационный API для системы управления стоматологической клиникой
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
from models import (
    DoctorWithSchedule, DoctorSpecialization,
    AppointmentCreate, AppointmentResponse, AppointmentStatus, AppointmentUpdate, AppointmentComplete,
    MedicalResultCreate, MedicalResultResponse, ResultType,
    SuccessResponse, ErrorResponse, PatientBase, PatientHistoryResponse,
    NotificationResponse, NotificationType,
    ServiceResponse,
    ReviewCreate, ReviewResponse,
    DoctorStatisticsResponse
)

# Инициализация приложения
app = FastAPI(
    title="DentalCare App API",
    description="REST API для мобильного приложения сети стоматологических клиник",
    version="1.0.0"
)

# CORS middleware для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== In-Memory Storage (Заглушки) ==========

# Тестовые данные - врачи
MOCK_DOCTORS = {
    1: {
        "id": 1,
        "first_name": "Анна",
        "last_name": "Иванова",
        "specialization": DoctorSpecialization.ORTHODONTIST,
        "experience_years": 8,
        "photo_url": "https://example.com/doctors/1.jpg",
        "rating": 4.8,
        "reviews_count": 45
    },
    2: {
        "id": 2,
        "first_name": "Дмитрий",
        "last_name": "Петров",
        "specialization": DoctorSpecialization.SURGEON,
        "experience_years": 12,
        "photo_url": "https://example.com/doctors/2.jpg",
        "rating": 4.9,
        "reviews_count": 78
    },
    3: {
        "id": 3,
        "first_name": "Елена",
        "last_name": "Смирнова",
        "specialization": DoctorSpecialization.THERAPIST,
        "experience_years": 5,
        "photo_url": "https://example.com/doctors/3.jpg",
        "rating": 4.7,
        "reviews_count": 32
    },
    4: {
        "id": 4,
        "first_name": "Михаил",
        "last_name": "Козлов",
        "specialization": DoctorSpecialization.PERIODONTIST,
        "experience_years": 10,
        "photo_url": "https://example.com/doctors/4.jpg",
        "rating": 4.6,
        "reviews_count": 56
    }
}

# Тестовые данные - пациенты
MOCK_PATIENTS = {
    1: {
        "id": 1,
        "first_name": "Иван",
        "last_name": "Сидоров",
        "phone": "+79161234567",
        "email": "ivan@example.com",
        "birth_date": "1990-05-15"
    },
    2: {
        "id": 2,
        "first_name": "Мария",
        "last_name": "Федорова",
        "phone": "+79167654321",
        "email": "maria@example.com",
        "birth_date": "1985-08-22"
    }
}

# Тестовые данные - записи на приём
MOCK_APPOINTMENTS = {
    1: {
        "id": 1,
        "patient_id": 1,
        "patient_name": "Иван Сидоров",
        "doctor_id": 1,
        "doctor_name": "Анна Иванова",
        "appointment_time": datetime.now() - timedelta(days=1),  # Вчера
        "service_type": "Консультация ортодонта",
        "status": AppointmentStatus.CONFIRMED,
        "notes": "Первичная консультация",
        "diagnosis": None,
        "treatment": None,
        "recommendations": None,
        "created_at": datetime.now() - timedelta(days=2),
        "updated_at": datetime.now() - timedelta(days=1)
    },
    2: {
        "id": 2,
        "patient_id": 1,
        "patient_name": "Иван Сидоров",
        "doctor_id": 2,
        "doctor_name": "Дмитрий Петров",
        "appointment_time": datetime(2025, 11, 5, 14, 30),
        "service_type": "Удаление зуба мудрости",
        "status": AppointmentStatus.PENDING,
        "notes": None,
        "diagnosis": None,
        "treatment": None,
        "recommendations": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
}

# Тестовые данные - результаты обследований
MOCK_RESULTS = {
    1: {
        "id": 1,
        "patient_id": 1,
        "doctor_id": 1,
        "doctor_name": "Анна Иванова",
        "result_type": ResultType.XRAY,
        "title": "Панорамный снимок",
        "description": "Общее состояние зубов удовлетворительное",
        "file_url": "https://s3.example.com/results/xray_001.jpg",
        "created_at": datetime.now() - timedelta(days=5)
    },
    2: {
        "id": 2,
        "patient_id": 1,
        "doctor_id": 1,
        "doctor_name": "Анна Иванова",
        "result_type": ResultType.PHOTO,
        "title": "Фото прикуса",
        "description": "Для планирования ортодонтического лечения",
        "file_url": "https://s3.example.com/results/photo_001.jpg",
        "created_at": datetime.now() - timedelta(days=5)
    }
}

# Тестовые данные - услуги клиники
MOCK_SERVICES = {
    1: {
        "id": 1,
        "name": "Консультация ортодонта",
        "description": "Первичная консультация специалиста по исправлению прикуса",
        "price": 1500.0,
        "duration_minutes": 30,
        "specialization": DoctorSpecialization.ORTHODONTIST
    },
    2: {
        "id": 2,
        "name": "Установка брекет-системы",
        "description": "Установка металлических или керамических брекетов",
        "price": 45000.0,
        "duration_minutes": 120,
        "specialization": DoctorSpecialization.ORTHODONTIST
    },
    3: {
        "id": 3,
        "name": "Лечение кариеса",
        "description": "Пломбирование одного зуба композитным материалом",
        "price": 3500.0,
        "duration_minutes": 60,
        "specialization": DoctorSpecialization.THERAPIST
    },
    4: {
        "id": 4,
        "name": "Удаление зуба",
        "description": "Простое удаление зуба под местной анестезией",
        "price": 2500.0,
        "duration_minutes": 30,
        "specialization": DoctorSpecialization.SURGEON
    },
    5: {
        "id": 5,
        "name": "Профессиональная чистка зубов",
        "description": "Ультразвуковая чистка + Air Flow",
        "price": 4000.0,
        "duration_minutes": 45,
        "specialization": DoctorSpecialization.THERAPIST
    },
    6: {
        "id": 6,
        "name": "Лечение пародонтита",
        "description": "Комплексное лечение заболеваний пародонта",
        "price": 8000.0,
        "duration_minutes": 90,
        "specialization": DoctorSpecialization.PERIODONTIST
    }
}

# Тестовые данные - отзывы
MOCK_REVIEWS = {
    1: {
        "id": 1,
        "patient_id": 1,
        "patient_name": "Иван Сидоров",
        "doctor_id": 1,
        "appointment_id": 1,
        "rating": 5,
        "comment": "Отличный врач! Профессионально и безболезненно установили брекеты.",
        "created_at": datetime.now() - timedelta(days=3)
    },
    2: {
        "id": 2,
        "patient_id": 2,
        "patient_name": "Мария Федорова",
        "doctor_id": 2,
        "appointment_id": 3,
        "rating": 5,
        "comment": "Очень доволен удалением зуба мудрости. Быстро и аккуратно.",
        "created_at": datetime.now() - timedelta(days=1)
    }
}

# Тестовые данные - уведомления
MOCK_NOTIFICATIONS = {
    1: {
        "id": 1,
        "user_id": 1,
        "notification_type": NotificationType.APPOINTMENT_CONFIRMED,
        "title": "Запись подтверждена",
        "message": "Ваша запись к врачу Анна Иванова на 28.10.2025 10:00 подтверждена",
        "is_read": True,
        "related_id": 1,
        "created_at": datetime.now() - timedelta(days=2)
    },
    2: {
        "id": 2,
        "user_id": 1,
        "notification_type": NotificationType.RESULT_UPLOADED,
        "title": "Загружен результат обследования",
        "message": "Доктор Анна Иванова загрузил результат: Панорамный снимок",
        "is_read": False,
        "related_id": 1,
        "created_at": datetime.now() - timedelta(hours=5)
    },
    3: {
        "id": 3,
        "user_id": 1,
        "notification_type": NotificationType.APPOINTMENT_REMINDER,
        "title": "Напоминание о приёме",
        "message": "Напоминаем о приёме к врачу Дмитрий Петров завтра в 14:30",
        "is_read": False,
        "related_id": 2,
        "created_at": datetime.now() - timedelta(hours=1)
    }
}

# Счетчики для генерации ID
appointment_counter = 3
result_counter = 3
review_counter = 3
notification_counter = 4


# ========== Helper Functions ==========

def validate_appointment_time(appointment_time: datetime) -> None:
    """
    Валидация времени записи
    
    Проверяет:
    - Время не в прошлом
    - Время в рабочие часы (9:00-18:00)
    - Время не в выходные (суббота, воскресенье)
    """
    now = datetime.now()
    
    # Проверка: не в прошлом
    if appointment_time < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя записаться на время в прошлом"
        )
    
    # Проверка: рабочие часы (9:00-18:00)
    if appointment_time.hour < 9 or appointment_time.hour >= 18:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Запись возможна только в рабочее время (9:00-18:00)"
        )
    
    # Проверка: не выходные дни
    if appointment_time.weekday() >= 5:  # 5=суббота, 6=воскресенье
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Клиника не работает в выходные дни"
        )
    
    # Проверка: минуты должны быть :00 или :30
    if appointment_time.minute not in [0, 30]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Запись возможна только на :00 или :30 минут"
        )


def generate_time_slots(doctor_id: int, days_ahead: int = 7) -> List[datetime]:
    """Генерирует доступные временные слоты для врача"""
    slots = []
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    for day in range(1, days_ahead + 1):
        current_date = base_date + timedelta(days=day)
        
        # Пропускаем выходные
        if current_date.weekday() >= 5:
            continue
        
        # Рабочие часы: 9:00 - 18:00, слоты по 30 минут
        for hour in range(9, 18):
            for minute in [0, 30]:
                slot_time = current_date.replace(hour=hour, minute=minute)
                # Проверяем, не занят ли слот
                is_booked = any(
                    apt["doctor_id"] == doctor_id and 
                    apt["appointment_time"] == slot_time and
                    apt["status"] not in [AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CANCELLED_BY_CLINIC]
                    for apt in MOCK_APPOINTMENTS.values()
                )
                if not is_booked:
                    slots.append(slot_time)
    
    return slots[:10]  # Возвращаем первые 10 доступных слотов


# ========== API Endpoints ==========

@app.get("/", tags=["General"])
async def root():
    """Корневой эндпоинт - информация об API"""
    return {
        "message": "DentalCare App API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "doctors": "/api/doctors",
            "appointments": "/api/appointments",
            "results": "/api/results",
            "patients": "/api/patients"
        }
    }


# ========== 1. GET /api/doctors - Получить список врачей ==========

@app.get(
    "/api/doctors",
    response_model=List[DoctorWithSchedule],
    tags=["Doctors"],
    summary="Получить список врачей"
)
async def get_doctors(
    specialization: Optional[DoctorSpecialization] = None,
    include_schedule: bool = False
):
    """
    Получить список врачей с возможностью фильтрации по специализации.
    
    - **specialization**: Фильтр по специализации (опционально)
    - **include_schedule**: Включить доступные слоты расписания
    """
    doctors = list(MOCK_DOCTORS.values())
    
    # Фильтрация по специализации
    if specialization:
        doctors = [d for d in doctors if d["specialization"] == specialization]
    
    # Добавление расписания
    if include_schedule:
        for doctor in doctors:
            doctor["available_slots"] = generate_time_slots(doctor["id"])
    else:
        for doctor in doctors:
            doctor["available_slots"] = []
    
    return doctors


# ========== 2. GET /api/appointments - Получить записи ==========

@app.get(
    "/api/appointments",
    response_model=List[AppointmentResponse],
    tags=["Appointments"],
    summary="Получить список записей"
)
async def get_appointments(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[AppointmentStatus] = None
):
    """
    Получить список записей на приём с возможностью фильтрации.
    
    - **patient_id**: ID пациента (для просмотра своих записей)
    - **doctor_id**: ID врача (для просмотра расписания врача)
    - **status**: Статус записи
    """
    appointments = list(MOCK_APPOINTMENTS.values())
    
    # Фильтрация
    if patient_id:
        appointments = [a for a in appointments if a["patient_id"] == patient_id]
    if doctor_id:
        appointments = [a for a in appointments if a["doctor_id"] == doctor_id]
    if status:
        appointments = [a for a in appointments if a["status"] == status]
    
    # Сортировка по времени приёма
    appointments.sort(key=lambda x: x["appointment_time"])
    
    return appointments


# ========== 3. POST /api/appointments - Создать запись ==========

@app.post(
    "/api/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Appointments"],
    summary="Создать новую запись на приём"
)
async def create_appointment(appointment_data: AppointmentCreate):
    """
    Создать новую запись на приём к врачу.
    
    Пациент создает запись, которая получает статус "Ожидает подтверждения".
    Регистратура должна подтвердить запись.
    """
    global appointment_counter
    
    # Валидация: проверка существования пациента
    if appointment_data.patient_id not in MOCK_PATIENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пациент с ID {appointment_data.patient_id} не найден"
        )
    
    # Валидация: проверка существования врача
    if appointment_data.doctor_id not in MOCK_DOCTORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Врач с ID {appointment_data.doctor_id} не найден"
        )
    
    # Валидация: проверка времени записи
    validate_appointment_time(appointment_data.appointment_time)
    
    # Валидация: проверка доступности слота
    is_slot_available = all(
        apt["doctor_id"] != appointment_data.doctor_id or
        apt["appointment_time"] != appointment_data.appointment_time or
        apt["status"] in [AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CANCELLED_BY_CLINIC]
        for apt in MOCK_APPOINTMENTS.values()
    )
    
    if not is_slot_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Выбранное время уже занято"
        )
    
    # Создание новой записи
    patient = MOCK_PATIENTS[appointment_data.patient_id]
    doctor = MOCK_DOCTORS[appointment_data.doctor_id]
    
    new_appointment = {
        "id": appointment_counter,
        "patient_id": appointment_data.patient_id,
        "patient_name": f"{patient['first_name']} {patient['last_name']}",
        "doctor_id": appointment_data.doctor_id,
        "doctor_name": f"{doctor['first_name']} {doctor['last_name']}",
        "appointment_time": appointment_data.appointment_time,
        "service_type": appointment_data.service_type,
        "status": AppointmentStatus.PENDING,  # Ожидает подтверждения
        "notes": appointment_data.notes,
        "diagnosis": None,
        "treatment": None,
        "recommendations": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    MOCK_APPOINTMENTS[appointment_counter] = new_appointment
    appointment_counter += 1
    
    return new_appointment


# ========== 4. PUT /api/appointments/{appointment_id}/confirm - Подтвердить запись ==========

@app.put(
    "/api/appointments/{appointment_id}/confirm",
    response_model=AppointmentResponse,
    tags=["Appointments"],
    summary="Подтвердить запись на приём (Администратор)"
)
async def confirm_appointment(appointment_id: int):
    """
    Подтвердить запись на приём.
    
    Используется администратором/регистратурой для подтверждения заявки пациента.
    После подтверждения пациент получает уведомление.
    """
    if appointment_id not in MOCK_APPOINTMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись с ID {appointment_id} не найдена"
        )
    
    appointment = MOCK_APPOINTMENTS[appointment_id]
    
    if appointment["status"] != AppointmentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Запись уже имеет статус '{appointment['status']}'"
        )
    
    # Подтверждаем запись
    appointment["status"] = AppointmentStatus.CONFIRMED
    appointment["updated_at"] = datetime.now()
    
    # В реальной системе здесь отправляется push-уведомление пациенту
    
    return appointment


# ========== 5. DELETE /api/appointments/{appointment_id} - Отменить запись ==========

@app.delete(
    "/api/appointments/{appointment_id}",
    response_model=SuccessResponse,
    tags=["Appointments"],
    summary="Отменить запись на приём"
)
async def cancel_appointment(
    appointment_id: int,
    cancelled_by: str = "patient"  # "patient" или "clinic"
):
    """
    Отменить запись на приём.
    
    Пациент может отменить запись не позднее чем за 24 часа до приёма.
    
    - **appointment_id**: ID записи
    - **cancelled_by**: Кто отменяет запись (patient/clinic)
    """
    if appointment_id not in MOCK_APPOINTMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись с ID {appointment_id} не найдена"
        )
    
    appointment = MOCK_APPOINTMENTS[appointment_id]
    
    # Проверка: можно ли отменить
    if appointment["status"] in [AppointmentStatus.COMPLETED, 
                                  AppointmentStatus.CANCELLED_BY_PATIENT,
                                  AppointmentStatus.CANCELLED_BY_CLINIC]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Эту запись невозможно отменить"
        )
    
    # Проверка: за 24 часа до приёма
    time_until_appointment = appointment["appointment_time"] - datetime.now()
    if cancelled_by == "patient" and time_until_appointment < timedelta(hours=24):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отмена возможна не позднее чем за 24 часа до приёма"
        )
    
    # Отменяем запись
    if cancelled_by == "patient":
        appointment["status"] = AppointmentStatus.CANCELLED_BY_PATIENT
    else:
        appointment["status"] = AppointmentStatus.CANCELLED_BY_CLINIC
    
    appointment["updated_at"] = datetime.now()
    
    # В реальной системе здесь отправляется уведомление врачу/пациенту
    
    return SuccessResponse(
        success=True,
        message="Запись успешно отменена",
        data={"appointment_id": appointment_id, "cancelled_by": cancelled_by}
    )


# ========== 6. GET /api/results/{patient_id} - Получить результаты обследований ==========

@app.get(
    "/api/results/{patient_id}",
    response_model=List[MedicalResultResponse],
    tags=["Medical Results"],
    summary="Получить результаты обследований пациента"
)
async def get_medical_results(
    patient_id: int,
    result_type: Optional[ResultType] = None
):
    """
    Получить список результатов обследований для конкретного пациента.
    
    - **patient_id**: ID пациента
    - **result_type**: Фильтр по типу результата (опционально)
    """
    if patient_id not in MOCK_PATIENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пациент с ID {patient_id} не найден"
        )
    
    # Фильтрация результатов
    results = [r for r in MOCK_RESULTS.values() if r["patient_id"] == patient_id]
    
    if result_type:
        results = [r for r in results if r["result_type"] == result_type]
    
    # Сортировка по дате создания (новые сверху)
    results.sort(key=lambda x: x["created_at"], reverse=True)
    
    return results


# ========== 7. POST /api/results - Загрузить результат обследования ==========

@app.post(
    "/api/results",
    response_model=MedicalResultResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Medical Results"],
    summary="Загрузить результат обследования (Врач)"
)
async def upload_medical_result(result_data: MedicalResultCreate):
    """
    Загрузить новый результат обследования для пациента.
    
    Используется врачом после проведения обследования.
    После загрузки пациент получает уведомление.
    """
    global result_counter
    
    # Валидация
    if result_data.patient_id not in MOCK_PATIENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пациент с ID {result_data.patient_id} не найден"
        )
    
    if result_data.doctor_id not in MOCK_DOCTORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Врач с ID {result_data.doctor_id} не найден"
        )
    
    doctor = MOCK_DOCTORS[result_data.doctor_id]
    
    # Создание нового результата
    new_result = {
        "id": result_counter,
        "patient_id": result_data.patient_id,
        "doctor_id": result_data.doctor_id,
        "doctor_name": f"{doctor['first_name']} {doctor['last_name']}",
        "result_type": result_data.result_type,
        "title": result_data.title,
        "description": result_data.description,
        "file_url": result_data.file_url,
        "created_at": datetime.now()
    }
    
    MOCK_RESULTS[result_counter] = new_result
    result_counter += 1
    
    # В реальной системе здесь отправляется уведомление пациенту
    
    return new_result


# ========== 8. GET /api/patients/{patient_id} - Получить информацию о пациенте ==========

@app.get(
    "/api/patients/{patient_id}",
    response_model=PatientBase,
    tags=["Patients"],
    summary="Получить информацию о пациенте"
)
async def get_patient(patient_id: int):
    """
    Получить подробную информацию о пациенте.
    
    Используется врачом для просмотра карточки пациента.
    """
    if patient_id not in MOCK_PATIENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пациент с ID {patient_id} не найден"
        )
    
    return MOCK_PATIENTS[patient_id]


# ========== 9. PATCH /api/appointments/{appointment_id}/complete - Завершить приём ==========

@app.patch(
    "/api/appointments/{appointment_id}/complete",
    response_model=AppointmentResponse,
    tags=["Appointments"],
    summary="Завершить приём и добавить заключение (Врач)"
)
async def complete_appointment(appointment_id: int, completion_data: AppointmentComplete):
    """
    Отметить приём как проведённый и добавить медицинское заключение.
    
    Используется врачом после проведения приёма для:
    - Изменения статуса на "Проведён"
    - Добавления диагноза
    - Описания проведённого лечения
    - Рекомендаций пациенту
    
    **User Story:** Как врач, я хочу отмечать приём как проведённый, 
    чтобы закрыть запись и обновить статус в системе.
    """
    if appointment_id not in MOCK_APPOINTMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись с ID {appointment_id} не найдена"
        )
    
    appointment = MOCK_APPOINTMENTS[appointment_id]
    
    # Проверка: приём должен быть подтверждён
    if appointment["status"] != AppointmentStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Можно завершить только подтверждённый приём. Текущий статус: {appointment['status']}"
        )
    
    # Проверка: время приёма должно быть в прошлом или сейчас
    if appointment["appointment_time"] > datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя завершить приём, который ещё не наступил"
        )
    
    # Обновляем запись
    appointment["status"] = AppointmentStatus.COMPLETED
    appointment["diagnosis"] = completion_data.diagnosis
    appointment["treatment"] = completion_data.treatment
    appointment["recommendations"] = completion_data.recommendations
    if completion_data.notes:
        appointment["notes"] = completion_data.notes
    appointment["updated_at"] = datetime.now()
    
    # В реальной системе здесь отправляется уведомление пациенту
    
    return appointment


# ========== 10. PATCH /api/appointments/{appointment_id}/reschedule - Перенести запись ==========

@app.patch(
    "/api/appointments/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
    tags=["Appointments"],
    summary="Перенести запись на другое время (Администратор)"
)
async def reschedule_appointment(appointment_id: int, new_time: datetime):
    """
    Перенести запись на другое время.
    
    Используется администратором для изменения времени записи.
    При переносе пациент и врач получают уведомление.
    
    **Acceptance Criteria:**
    - Новое время валидируется (не в прошлом, рабочие часы)
    - Новый слот должен быть свободен
    - Отправляется уведомление об изменении
    """
    if appointment_id not in MOCK_APPOINTMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись с ID {appointment_id} не найдена"
        )
    
    appointment = MOCK_APPOINTMENTS[appointment_id]
    
    # Проверка: нельзя переносить завершённые или отменённые записи
    if appointment["status"] in [AppointmentStatus.COMPLETED, 
                                  AppointmentStatus.CANCELLED_BY_PATIENT,
                                  AppointmentStatus.CANCELLED_BY_CLINIC]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Нельзя перенести запись со статусом '{appointment['status']}'"
        )
    
    # Валидация нового времени
    validate_appointment_time(new_time)
    
    # Проверка: новый слот должен быть свободен
    is_slot_available = all(
        (apt_id == appointment_id) or  # Исключаем текущую запись
        (apt["doctor_id"] != appointment["doctor_id"]) or
        (apt["appointment_time"] != new_time) or
        (apt["status"] in [AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CANCELLED_BY_CLINIC])
        for apt_id, apt in MOCK_APPOINTMENTS.items()
    )
    
    if not is_slot_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Новое время уже занято"
        )
    
    # Переносим запись
    old_time = appointment["appointment_time"]
    appointment["appointment_time"] = new_time
    appointment["updated_at"] = datetime.now()
    
    # В реальной системе здесь отправляется уведомление пациенту и врачу
    
    return appointment


# ========== 11. GET /api/patients/{patient_id}/history - История пациента ==========

@app.get(
    "/api/patients/{patient_id}/history",
    response_model=PatientHistoryResponse,
    tags=["Patients"],
    summary="Получить полную историю пациента"
)
async def get_patient_history(patient_id: int):
    """
    Получить полную историю пациента: приёмы и результаты обследований.
    
    Используется врачом для просмотра:
    - Личных данных пациента
    - Всех приёмов (прошедших и будущих)
    - Всех результатов обследований
    - Статистики посещений
    
    **User Story:** Как врач, я хочу открывать карточку пациента, 
    чтобы ознакомиться с его историей посещений и результатами обследований.
    """
    if patient_id not in MOCK_PATIENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пациент с ID {patient_id} не найден"
        )
    
    # Получаем данные пациента
    patient = MOCK_PATIENTS[patient_id]
    
    # Получаем все приёмы пациента
    appointments = [
        apt for apt in MOCK_APPOINTMENTS.values() 
        if apt["patient_id"] == patient_id
    ]
    appointments.sort(key=lambda x: x["appointment_time"], reverse=True)
    
    # Получаем все результаты обследований
    results = [
        res for res in MOCK_RESULTS.values() 
        if res["patient_id"] == patient_id
    ]
    results.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Вычисляем статистику
    now = datetime.now()
    total_appointments = len(appointments)
    completed_appointments = sum(
        1 for apt in appointments 
        if apt["status"] == AppointmentStatus.COMPLETED
    )
    upcoming_appointments = sum(
        1 for apt in appointments 
        if apt["appointment_time"] > now and 
        apt["status"] in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
    )
    
    return {
        "patient": patient,
        "appointments": appointments,
        "medical_results": results,
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "upcoming_appointments": upcoming_appointments
    }


# ========== BONUS: Статистика ==========

@app.get(
    "/api/stats",
    tags=["Statistics"],
    summary="Получить статистику системы"
)
async def get_stats():
    """
    Получить общую статистику системы (для демонстрации).
    """
    total_appointments = len(MOCK_APPOINTMENTS)
    pending_appointments = sum(
        1 for a in MOCK_APPOINTMENTS.values() 
        if a["status"] == AppointmentStatus.PENDING
    )
    confirmed_appointments = sum(
        1 for a in MOCK_APPOINTMENTS.values() 
        if a["status"] == AppointmentStatus.CONFIRMED
    )
    
    return {
        "total_doctors": len(MOCK_DOCTORS),
        "total_patients": len(MOCK_PATIENTS),
        "total_appointments": total_appointments,
        "pending_appointments": pending_appointments,
        "confirmed_appointments": confirmed_appointments,
        "total_results": len(MOCK_RESULTS)
    }


# ========== 12. GET /api/notifications/{user_id} - Получить уведомления ==========

@app.get(
    "/api/notifications/{user_id}",
    response_model=List[NotificationResponse],
    tags=["Notifications"],
    summary="Получить уведомления пользователя"
)
async def get_notifications(
    user_id: int,
    unread_only: bool = False
):
    """
    Получить список уведомлений для пользователя.
    
    **User Story:** Как пациент, я хочу получать уведомления о предстоящем приёме,
    чтобы не забыть о визите к стоматологу.
    
    **Типы уведомлений:**
    - Подтверждение записи
    - Напоминание о приёме (за 24 часа)
    - Отмена приёма
    - Перенос приёма
    - Загрузка результата обследования
    - Завершение приёма
    
    - **user_id**: ID пользователя (пациента или врача)
    - **unread_only**: Показать только непрочитанные (по умолчанию false)
    """
    # Получаем все уведомления пользователя
    notifications = [
        notif for notif in MOCK_NOTIFICATIONS.values()
        if notif["user_id"] == user_id
    ]
    
    # Фильтр только непрочитанные
    if unread_only:
        notifications = [n for n in notifications if not n["is_read"]]
    
    # Сортировка по дате (новые сверху)
    notifications.sort(key=lambda x: x["created_at"], reverse=True)
    
    return notifications


# ========== 13. GET /api/services - Получить прайс-лист услуг ==========

@app.get(
    "/api/services",
    response_model=List[ServiceResponse],
    tags=["Services"],
    summary="Получить прайс-лист услуг клиники"
)
async def get_services(specialization: Optional[DoctorSpecialization] = None):
    """
    Получить список услуг клиники с ценами.
    
    **Назначение:** Предоставить пациентам информацию о доступных услугах и ценах
    для планирования лечения.
    
    - **specialization**: Фильтр по специализации врача (опционально)
    """
    services = list(MOCK_SERVICES.values())
    
    # Фильтрация по специализации
    if specialization:
        services = [s for s in services if s["specialization"] == specialization]
    
    # Сортировка по цене
    services.sort(key=lambda x: x["price"])
    
    return services


# ========== 14. POST /api/reviews - Оставить отзыв о приёме ==========

@app.post(
    "/api/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Reviews"],
    summary="Оставить отзыв о приёме"
)
async def create_review(review_data: ReviewCreate):
    """
    Оставить отзыв о приёме и оценить работу врача.
    
    После завершённого приёма пациент может оставить отзыв и оценку.
    Оценка влияет на общий рейтинг врача.
    
    **Validation:**
    - Приём должен существовать и быть завершённым
    - Пациент должен быть участником приёма
    - Можно оставить только один отзыв на приём
    """
    global review_counter
    
    # Валидация: проверка существования приёма
    if review_data.appointment_id not in MOCK_APPOINTMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Приём с ID {review_data.appointment_id} не найден"
        )
    
    appointment = MOCK_APPOINTMENTS[review_data.appointment_id]
    
    # Проверка: приём должен быть завершён
    if appointment["status"] != AppointmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отзыв можно оставить только для завершённого приёма"
        )
    
    # Проверка: пациент должен быть участником приёма
    if appointment["patient_id"] != review_data.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы не можете оставить отзыв для чужого приёма"
        )
    
    # Проверка: уже есть отзыв на этот приём
    existing_review = any(
        r["appointment_id"] == review_data.appointment_id
        for r in MOCK_REVIEWS.values()
    )
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже оставили отзыв для этого приёма"
        )
    
    patient = MOCK_PATIENTS[review_data.patient_id]
    
    # Создание отзыва
    new_review = {
        "id": review_counter,
        "patient_id": review_data.patient_id,
        "patient_name": f"{patient['first_name']} {patient['last_name']}",
        "doctor_id": review_data.doctor_id,
        "appointment_id": review_data.appointment_id,
        "rating": review_data.rating,
        "comment": review_data.comment,
        "created_at": datetime.now()
    }
    
    MOCK_REVIEWS[review_counter] = new_review
    review_counter += 1
    
    # Обновляем рейтинг врача (в реальной системе пересчитываем среднее)
    doctor = MOCK_DOCTORS[review_data.doctor_id]
    doctor["reviews_count"] = doctor.get("reviews_count", 0) + 1
    
    return new_review


# ========== 15. GET /api/doctors/{doctor_id}/statistics - Статистика врача ==========

@app.get(
    "/api/doctors/{doctor_id}/statistics",
    response_model=DoctorStatisticsResponse,
    tags=["Doctors"],
    summary="Получить статистику работы врача"
)
async def get_doctor_statistics(doctor_id: int):
    """
    Получить подробную статистику работы врача.
    
    **Используется:**
    - Врачом для просмотра своих показателей
    - Администратором для анализа эффективности
    - Пациентами для выбора врача
    
    **Показатели:**
    - Количество приёмов (всего, завершённых, предстоящих, отменённых)
    - Средний рейтинг
    - Количество отзывов
    - Количество уникальных пациентов
    """
    if doctor_id not in MOCK_DOCTORS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Врач с ID {doctor_id} не найден"
        )
    
    doctor = MOCK_DOCTORS[doctor_id]
    
    # Получаем все приёмы врача
    doctor_appointments = [
        apt for apt in MOCK_APPOINTMENTS.values()
        if apt["doctor_id"] == doctor_id
    ]
    
    now = datetime.now()
    
    # Вычисляем статистику
    total_appointments = len(doctor_appointments)
    completed_appointments = sum(
        1 for apt in doctor_appointments
        if apt["status"] == AppointmentStatus.COMPLETED
    )
    upcoming_appointments = sum(
        1 for apt in doctor_appointments
        if apt["appointment_time"] > now and
        apt["status"] in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
    )
    cancelled_appointments = sum(
        1 for apt in doctor_appointments
        if apt["status"] in [AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CANCELLED_BY_CLINIC]
    )
    
    # Уникальные пациенты
    unique_patients = len(set(apt["patient_id"] for apt in doctor_appointments))
    
    # Рейтинг
    doctor_reviews = [r for r in MOCK_REVIEWS.values() if r["doctor_id"] == doctor_id]
    average_rating = None
    if doctor_reviews:
        average_rating = round(sum(r["rating"] for r in doctor_reviews) / len(doctor_reviews), 2)
    
    return {
        "doctor_id": doctor_id,
        "doctor_name": f"{doctor['first_name']} {doctor['last_name']}",
        "total_appointments": total_appointments,
        "completed_appointments": completed_appointments,
        "upcoming_appointments": upcoming_appointments,
        "cancelled_appointments": cancelled_appointments,
        "average_rating": average_rating or doctor.get("rating"),
        "total_reviews": len(doctor_reviews),
        "patients_served": unique_patients
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

