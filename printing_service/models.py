import datetime

from sqlalchemy import Column, Date, Integer, LargeBinary, String, func
from sqlalchemy.orm import deferred, undefer

import utils
from settings import Base, engine, session


class ResolutionSheet(Base):
    __tablename__ = "resolution_sheets"
    id = Column(Integer, primary_key=True)
    examId = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    course = Column(String, nullable=False)
    pdf = deferred(Column(LargeBinary, nullable=False))

    def __repr__(self):
        return f"<ResolutionSheet(id={self.id}, examId={self.examId}, date='{self.date}', course='{self.course}')>"

    @staticmethod
    def validate(examId, date, course, sheetsNum):
        if type(examId) is not int or examId < 1:
            return f"invalid exam id '{examId}'"

        if type(date) is not str or not date:
            return "date is wrong or empty"

        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            return f"invalid date '{date}' (expected YYYY-MM-DD)"

        if type(course) is not str or not course.strip():
            return "course is wrong or empty"

        if type(sheetsNum) is not int or sheetsNum < 1:
            return f"invalid number of sheets '{sheetsNum}'"

        return None

    @classmethod
    def exams(cls):
        return (
            session.query(cls.examId, cls.date, cls.course, func.count(cls.id))
            .group_by(cls.examId, cls.date, cls.course)
            .order_by(cls.examId)
            .all()
        )

    @classmethod
    def forExam(cls, examId):
        return (
            session.query(cls)
            .options(undefer(cls.pdf))
            .filter(cls.examId == examId)
            .order_by(cls.id)
            .all()
        )

    @classmethod
    def isPrinted(cls, examId):
        return session.query(cls).filter(cls.examId == examId).first() is not None

    @classmethod
    def bulkCreate(cls, examId, date, course, sheetsNum):
        date = datetime.date.fromisoformat(date)
        title = f"{course} - {date}"

        sheets = []
        for _ in range(sheetsNum):
            sheets.append(cls(examId=examId, date=date, course=course, pdf=b""))

        session.add_all(sheets)
        session.flush()

        sheetIds = []
        for sheet in sheets:
            sheet.pdf = utils.makeSheetPdf(sheet.id, title)
            sheetIds.append(sheet.id)

        session.commit()

        return sheetIds


Base.metadata.create_all(engine)
