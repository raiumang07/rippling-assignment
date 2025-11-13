
import os
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, create_engine, event)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session

# Database setup
DATABASE_URL = "sqlite:///./boostly.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Models
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    credits_to_give = Column(Integer, default=100)
    credits_received = Column(Integer, default=0)
    monthly_sending_limit = Column(Integer, default=100)
    last_credit_reset = Column(DateTime, default=datetime.utcnow)

    sent_recognitions = relationship("Recognition", foreign_keys="[Recognition.sender_id]", back_populates="sender")
    received_recognitions = relationship("Recognition", foreign_keys="[Recognition.receiver_id]", back_populates="receiver")

class Recognition(Base):
    __tablename__ = "recognitions"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("students.id"))
    receiver_id = Column(Integer, ForeignKey("students.id"))
    credits = Column(Integer)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship("Student", foreign_keys=[sender_id], back_populates="sent_recognitions")
    receiver = relationship("Student", foreign_keys=[receiver_id], back_populates="received_recognitions")
    endorsements = relationship("Endorsement", back_populates="recognition")

class Endorsement(Base):
    __tablename__ = "endorsements"
    id = Column(Integer, primary_key=True, index=True)
    recognition_id = Column(Integer, ForeignKey("recognitions.id"))
    endorser_id = Column(Integer, ForeignKey("students.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

    recognition = relationship("Recognition", back_populates="endorsements")
    endorser = relationship("Student")

class Redemption(Base):
    __tablename__ = "redemptions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    credits = Column(Integer)
    voucher_value = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student")


Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class StudentBase(BaseModel):
    name: str

class StudentCreate(StudentBase):
    pass

class StudentSchema(StudentBase):
    id: int
    credits_to_give: int
    credits_received: int

    class Config:
        orm_mode = True

class RecognitionBase(BaseModel):
    receiver_id: int
    credits: int
    message: str

class RecognitionCreate(RecognitionBase):
    sender_id: int

class RecognitionSchema(RecognitionBase):
    id: int
    sender_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class EndorsementBase(BaseModel):
    recognition_id: int
    endorser_id: int

class EndorsementCreate(EndorsementBase):
    pass


@app.get("/")
def read_root():
    return {"message": "Welcome to Boostly!"}

# Placeholder for student creation for testing
@app.post("/students/", response_model=StudentSchema)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(name=student.name)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get("/students/{student_id}", response_model=StudentSchema)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/recognitions/", response_model=RecognitionSchema)
def create_recognition(recognition: RecognitionCreate, db: Session = Depends(get_db)):
    sender = db.query(Student).filter(Student.id == recognition.sender_id).first()
    receiver = db.query(Student).filter(Student.id == recognition.receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="Sender or receiver not found")

    if sender.id == receiver.id:
        raise HTTPException(status_code=400, detail="Cannot send recognition to yourself")

    if sender.credits_to_give < recognition.credits:
        raise HTTPException(status_code=400, detail="Insufficient credits to give")

    if sender.monthly_sending_limit < recognition.credits:
        raise HTTPException(status_code=400, detail="Exceeds monthly sending limit")

    sender.credits_to_give -= recognition.credits
    sender.monthly_sending_limit -= recognition.credits
    receiver.credits_received += recognition.credits

    db_recognition = Recognition(**recognition.dict())
    db.add(db_recognition)
    db.commit()
    db.refresh(db_recognition)
    return db_recognition

@app.post("/recognitions/{recognition_id}/endorse", response_model=EndorsementSchema)
def endorse_recognition(recognition_id: int, endorsement: EndorsementBody, db: Session = Depends(get_db)):
    recognition = db.query(Recognition).filter(Recognition.id == recognition_id).first()
    if not recognition:
        raise HTTPException(status_code=404, detail="Recognition not found")

    endorser = db.query(Student).filter(Student.id == endorsement.endorser_id).first()
    if not endorser:
        raise HTTPException(status_code=404, detail="Endorser not found")

    existing_endorsement = db.query(Endorsement).filter(
        Endorsement.recognition_id == recognition_id,
        Endorsement.endorser_id == endorsement.endorser_id
    ).first()

    if existing_endorsement:
        raise HTTPException(status_code=400, detail="You have already endorsed this recognition")

    db_endorsement = Endorsement(recognition_id=recognition_id, endorser_id=endorsement.endorser_id)
    db.add(db_endorsement)
    db.commit()
    db.refresh(db_endorsement)
    return db_endorsement

class RedemptionBase(BaseModel):
    student_id: int
    credits: int

class RedemptionCreate(RedemptionBase):
    pass

class RedemptionSchema(RedemptionBase):
    id: int
    voucher_value: float
    timestamp: datetime

    class Config:
        orm_mode = True


class Redemption(Base):
    __tablename__ = "redemptions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    credits = Column(Integer)
    voucher_value = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student")


@app.post("/redemptions/", response_model=RedemptionSchema)
def create_redemption(redemption: RedemptionCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == redemption.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.credits_received < redemption.credits:
        raise HTTPException(status_code=400, detail="Insufficient received credits to redeem")

    student.credits_received -= redemption.credits
    voucher_value = redemption.credits * 5  # ₹5 per credit

    db_redemption = Redemption(
        student_id=redemption.student_id,
        credits=redemption.credits,
        voucher_value=voucher_value
    )
    db.add(db_redemption)
    db.commit()
    db.refresh(db_redemption)
    return db_redemption

@app.post("/students/reset-credits")
def reset_credits(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    for student in students:
        carry_over = min(student.credits_to_give, 50)
        student.credits_to_give = 100 + carry_over
        student.monthly_sending_limit = 100
        student.last_credit_reset = datetime.utcnow()
    db.commit()
    return {"message": "Credits reset for all students."}

class LeaderboardEntry(BaseModel):
    student_id: int
    name: str
    total_credits_received: int
    total_recognitions_received: int
    total_endorsements_received: int

@app.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    students = db.query(Student).order_by(
        Student.credits_received.desc(),
        Student.id.asc()
    ).limit(limit).all()

    leaderboard = []
    for student in students:
        total_recognitions_received = len(student.received_recognitions)
        total_endorsements_received = sum(len(rec.endorsements) for rec in student.received_recognitions)

        leaderboard.append(LeaderboardEntry(
            student_id=student.id,
            name=student.name,
            total_credits_received=student.credits_received,
            total_recognitions_received=total_recognitions_received,
            total_endorsements_received=total_endorsements_received,
        ))
    return leaderboard
