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
    # the (examId, questionNumber) pair is the primary key:
    # each question of an exam is corrected by a single professor
    examId = Column(Integer, primary_key=True)
    questionNumber = Column(Integer, primary_key=True)
    professorId = Column(Integer, nullable=False)

    def __repr__(self):
        return "<ProfessorAssignment(examId=%d, questionNumber=%d, professorId=%d)>" % (
            self.examId,
            self.questionNumber,
            self.professorId,
        )

    @staticmethod
    def validate(examId, questionNumber, professorId):
        if examId is None or examId < 1:
            return "invalid exam id"
        if questionNumber not in range(1, QUESTIONS + 1):
            return "question number must be between 1 and %d" % QUESTIONS
        if professorId is None or professorId < 1:
            return "invalid professor id"
        return None

    @classmethod
    def all(cls):
        return session.query(cls).order_by(cls.examId, cls.questionNumber).all()

    @classmethod
    def assign(cls, examId, questionNumber, professorId):
        # merge inserts the assignment, or replaces the professor if it exists
        assignment = session.merge(
            cls(examId=examId, questionNumber=questionNumber, professorId=professorId)
        )
        session.commit()
        return assignment


class ExamCorrectionPdf(Base):
    __tablename__ = "exam_correction_pdfs"
    id = Column(Integer, primary_key=True)
    examId = Column(Integer, nullable=False)
    pdf = deferred(Column(LargeBinary, nullable=False))

    corrections = relationship(
        "QuestionCorrection",
        back_populates="examPdf",
        order_by="QuestionCorrection.id",
    )

    def __repr__(self):
        return "<ExamCorrectionPdf(id=%d, examId=%d)>" % (self.id, self.examId)

    @staticmethod
    def validate(examId):
        if examId is None or examId < 1:
            return "invalid exam id"
        return None

    @classmethod
    def all(cls):
        return session.query(cls).order_by(cls.id).all()

    @classmethod
    def get(cls, examPdfId):
        return session.get(cls, examPdfId)

    @classmethod
    def create(cls, examId, pdf, pages):
        # pages: (sheetId, questionNumber, image) tuples from utils.splitScan
        examPdf = cls(examId=examId, pdf=pdf)
        for sheetId, questionNumber, image in pages:
            examPdf.corrections.append(
                QuestionCorrection(
                    sheetId=sheetId, questionNumber=questionNumber, image=image
                )
            )
        session.add(examPdf)
        session.commit()
        return examPdf


class QuestionCorrection(Base):
    __tablename__ = "question_corrections"
    id = Column(Integer, primary_key=True)
    examPdfId = Column(Integer, ForeignKey("exam_correction_pdfs.id"), nullable=False)
    # read from the page's QR code: identifies the resolution sheet, not the student
    sheetId = Column(Integer, nullable=False)
    questionNumber = Column(Integer, nullable=False)
    # PNG of the page with its QR codes covered
    image = deferred(Column(LargeBinary, nullable=False))
    evaluated = Column(Boolean, nullable=False, default=False)
    grade = Column(Float)

    examPdf = relationship("ExamCorrectionPdf", back_populates="corrections")

    def __repr__(self):
        return "<QuestionCorrection(id=%d, sheetId=%d, questionNumber=%d)>" % (
            self.id,
            self.sheetId,
            self.questionNumber,
        )

    @staticmethod
    def validateGrade(grade):
        # "not a <= g <= b" also rejects nan and inf
        if grade is None or not 0 <= grade <= MAX_GRADE:
            return "grade must be a number between 0 and %d" % MAX_GRADE
        return None

    @classmethod
    def get(cls, correctionId):
        return session.get(cls, correctionId)

    @classmethod
    def listWithProfessor(cls, evaluated):
        # (correction, professorId) pairs, professorId is None if unassigned
        return (
            session.query(cls, ProfessorAssignment.professorId)
            .join(cls.examPdf)
            .outerjoin(
                ProfessorAssignment,
                and_(
                    ProfessorAssignment.examId == ExamCorrectionPdf.examId,
                    ProfessorAssignment.questionNumber == cls.questionNumber,
                ),
            )
            .filter(cls.evaluated == evaluated)
            .order_by(ExamCorrectionPdf.examId, cls.questionNumber, cls.id)
            .all()
        )

    @classmethod
    def uploadedSheets(cls, sheetIds):
        rows = session.query(cls.sheetId).filter(cls.sheetId.in_(sheetIds)).distinct()
        return sorted(row.sheetId for row in rows)

    @classmethod
    def sheets(cls):
        # one row per sheet: (sheetId, examId, corrected questions, total grade)
        # count(grade) only counts the graded questions
        return (
            session.query(
                cls.sheetId,
                ExamCorrectionPdf.examId,
                func.count(cls.grade),
                func.sum(cls.grade),
            )
            .join(cls.examPdf)
            .group_by(cls.sheetId, ExamCorrectionPdf.examId)
            .order_by(cls.sheetId)
            .all()
        )

    @classmethod
    def forSheet(cls, sheetId):
        return (
            session.query(cls)
            .filter(cls.sheetId == sheetId)
            .order_by(cls.questionNumber)
            .all()
        )

    def correct(self, grade):
        self.grade = grade
        self.evaluated = True
        session.commit()


Base.metadata.create_all(engine)
