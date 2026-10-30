from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    and_,
    func,
)
from sqlalchemy.orm import deferred, relationship

from settings import MAX_GRADE, QUESTIONS, Base, engine, session


class ProfessorAssignment(Base):
    __tablename__ = "professor_assignments"
    exam_id = Column(Integer, primary_key=True)
    question_number = Column(Integer, primary_key=True)
    professor_id = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<ProfessorAssignment(exam_id={self.exam_id}, question_number={self.question_number}, professor_id={self.professor_id})>"

    @staticmethod
    def validate(exam_id, question_number, professor_id):
        if exam_id is None or exam_id < 1:
            return "invalid exam id"

        if question_number not in range(1, QUESTIONS + 1):
            return f"question number must be between 1 and {QUESTIONS}"

        if professor_id is None or professor_id < 1:
            return "invalid professor id"

        return None

    @classmethod
    def all(cls):
        return session.query(cls).order_by(cls.exam_id, cls.question_number).all()

    @classmethod
    def get(cls, exam_id, question_number):
        return session.get(cls, (exam_id, question_number))

    @classmethod
    def assign(cls, exam_id, question_number, professor_id):
        assignment = cls(
            exam_id=exam_id, question_number=question_number, professor_id=professor_id
        )

        session.add(assignment)
        session.commit()

        return assignment


class ExamCorrectionPdf(Base):
    __tablename__ = "exam_correction_pdfs"
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, nullable=False)
    pdf = deferred(Column(LargeBinary, nullable=False))

    corrections = relationship(
        "QuestionCorrection",
        back_populates="exam_pdf",
        order_by="QuestionCorrection.id",
    )

    def __repr__(self):
        return f"<ExamCorrectionPdf(id={self.id}, exam_id={self.exam_id})>"

    @staticmethod
    def validate(exam_id):
        if exam_id is None or exam_id < 1:
            return "invalid exam id"

        return None

    @classmethod
    def all(cls):
        return session.query(cls).order_by(cls.id).all()

    @classmethod
    def get(cls, exam_pdf_id):
        return session.get(cls, exam_pdf_id)

    @classmethod
    def create(cls, exam_id, pdf, pages):
        exam_pdf = cls(exam_id=exam_id, pdf=pdf)
        for sheet_id, question_number, image in pages:
            exam_pdf.corrections.append(
                QuestionCorrection(
                    sheet_id=sheet_id, question_number=question_number, image=image
                )
            )

        session.add(exam_pdf)
        session.commit()

        return exam_pdf


class QuestionCorrection(Base):
    __tablename__ = "question_corrections"
    id = Column(Integer, primary_key=True)
    exam_pdf_id = Column(Integer, ForeignKey("exam_correction_pdfs.id"), nullable=False)
    sheet_id = Column(Integer, nullable=False)
    question_number = Column(Integer, nullable=False)
    image = deferred(Column(LargeBinary, nullable=False))
    evaluated = Column(Boolean, nullable=False, default=False)
    grade = Column(Float)

    exam_pdf = relationship("ExamCorrectionPdf", back_populates="corrections")

    def __repr__(self):
        return f"<QuestionCorrection(id={self.id}, sheet_id={self.sheet_id}, question_number={self.question_number})>"

    @staticmethod
    def validate_grade(grade):
        if grade is None or not 0 <= grade <= MAX_GRADE:
            return f"grade must be a number between 0 and {MAX_GRADE}"

        return None

    @classmethod
    def get(cls, correction_id):
        return session.get(cls, correction_id)

    @classmethod
    def list_with_professor(cls, evaluated):
        return (
            session.query(cls, ProfessorAssignment.professor_id)
            .join(cls.exam_pdf)
            .outerjoin(
                ProfessorAssignment,
                and_(
                    ProfessorAssignment.exam_id == ExamCorrectionPdf.exam_id,
                    ProfessorAssignment.question_number == cls.question_number,
                ),
            )
            .filter(cls.evaluated == evaluated)
            .order_by(ExamCorrectionPdf.exam_id, cls.question_number, cls.id)
            .all()
        )

    @classmethod
    def uploaded_sheets(cls, sheet_ids):
        rows = (
            session.query(cls.sheet_id).filter(cls.sheet_id.in_(sheet_ids)).distinct()
        )

        uploaded = []
        for row in rows:
            uploaded.append(row.sheet_id)

        return sorted(uploaded)

    @classmethod
    def sheets(cls):
        return (
            session.query(
                cls.sheet_id,
                ExamCorrectionPdf.exam_id,
                func.count(cls.grade),
                func.sum(cls.grade),
            )
            .join(cls.exam_pdf)
            .group_by(cls.sheet_id, ExamCorrectionPdf.exam_id)
            .order_by(cls.sheet_id)
            .all()
        )

    @classmethod
    def for_sheet(cls, sheet_id):
        return (
            session.query(cls)
            .filter(cls.sheet_id == sheet_id)
            .order_by(cls.question_number)
            .all()
        )

    def correct(self, grade):
        self.grade = grade
        self.evaluated = True

        session.commit()


Base.metadata.create_all(engine)
