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
        "Enrollment", back_populates="exam", order_by="Enrollment.studentId"
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
    def get(cls, examId):
        return session.get(cls, examId)

    @classmethod
    def create(cls, date, course):
        exam = cls(date=datetime.date.fromisoformat(date), course=course)

        session.add(exam)
        session.commit()

        return exam


class Enrollment(Base):
    __tablename__ = "enrollments"
    examId = Column(Integer, ForeignKey("exams.id"), primary_key=True)
    studentId = Column(Integer, primary_key=True)

    exam = relationship("Exam", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment(examId={self.examId}, studentId={self.studentId})>"

    @classmethod
    def all(cls):
        return session.query(cls).order_by(cls.examId, cls.studentId).all()

    @classmethod
    def bulkCreate(cls, examId, studentIds):
        newIds = []
        existing = session.query(cls).filter(cls.examId == examId)

        enrolled = []
        for enrollment in existing:
            enrolled.append(enrollment.studentId)

        for studentId in studentIds:
            if studentId not in enrolled:
                session.add(cls(examId=examId, studentId=studentId))
                enrolled.append(studentId)
                newIds.append(studentId)

        session.commit()

        return newIds


Base.metadata.create_all(engine)
