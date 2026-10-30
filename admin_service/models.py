import datetime

from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from settings import Base, engine, session


class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    course = Column(String, nullable=False)

    enrollments = relationship(
        "Enrollment", back_populates="exam", order_by="Enrollment.student_id"
    )

    def __repr__(self):
        return f"<Exam(id={self.id}, date='{self.date}', course='{self.course}')>"

    @staticmethod
    def validate(date, course):
        if not date:
            return "date is empty"

        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            return f"invalid date '{date}' (expected YYYY-MM-DD)"

        if not course:
            return "course is empty"

        return None

    @classmethod
    def all(cls):
        return session.query(cls).order_by(cls.id).all()

    @classmethod
    def get(cls, exam_id):
        return session.get(cls, exam_id)

    @classmethod
    def create(cls, date, course):
        exam = cls(date=datetime.date.fromisoformat(date), course=course)

        session.add(exam)
        session.commit()

        return exam


class Enrollment(Base):
    __tablename__ = "enrollments"
    exam_id = Column(Integer, ForeignKey("exams.id"), primary_key=True)
    student_id = Column(Integer, primary_key=True)

    exam = relationship("Exam", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment(exam_id={self.exam_id}, student_id={self.student_id})>"

    @classmethod
    def all(cls):
        return session.query(cls).order_by(cls.exam_id, cls.student_id).all()

    @classmethod
    def bulk_create(cls, exam_id, student_ids):
        new_ids = []
        existing = session.query(cls).filter(cls.exam_id == exam_id)

        enrolled = []
        for enrollment in existing:
            enrolled.append(enrollment.student_id)

        for student_id in student_ids:
            if student_id not in enrolled:
                session.add(cls(exam_id=exam_id, student_id=student_id))
                enrolled.append(student_id)
                new_ids.append(student_id)

        session.commit()

        return new_ids


Base.metadata.create_all(engine)
