import datetime

from sqlalchemy import Column, Date, Integer, LargeBinary, String, func
from sqlalchemy.orm import deferred, undefer

import utils
from settings import Base, engine, session


class ResolutionSheet(Base):
    __tablename__ = "resolution_sheets"
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    course = Column(String, nullable=False)
    pdf = deferred(Column(LargeBinary, nullable=False))

    def __repr__(self):
        return f"<ResolutionSheet(id={self.id}, exam_id={self.exam_id}, date='{self.date}', course='{self.course}')>"

    @staticmethod
    def validate(exam_id, date, course, sheets_num):
        if type(exam_id) is not int or exam_id < 1:
            return f"invalid exam id '{exam_id}'"

        if type(date) is not str or not date:
            return "date is wrong or empty"

        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            return f"invalid date '{date}' (expected YYYY-MM-DD)"

        if type(course) is not str or not course.strip():
            return "course is wrong or empty"

        if type(sheets_num) is not int or sheets_num < 1:
            return f"invalid number of sheets '{sheets_num}'"

        return None

    @classmethod
    def exams(cls):
        return (
            session.query(cls.exam_id, cls.date, cls.course, func.count(cls.id))
            .group_by(cls.exam_id, cls.date, cls.course)
            .order_by(cls.exam_id)
            .all()
        )

    @classmethod
    def for_exam(cls, exam_id):
        return (
            session.query(cls)
            .options(undefer(cls.pdf))
            .filter(cls.exam_id == exam_id)
            .order_by(cls.id)
            .all()
        )

    @classmethod
    def is_printed(cls, exam_id):
        return session.query(cls).filter(cls.exam_id == exam_id).first() is not None

    @classmethod
    def bulk_create(cls, exam_id, date, course, sheets_num):
        date = datetime.date.fromisoformat(date)
        title = f"{course} - {date}"

        sheets = []
        for _ in range(sheets_num):
            sheets.append(cls(exam_id=exam_id, date=date, course=course, pdf=b""))

        session.add_all(sheets)
        session.flush()

        sheet_ids = []
        for sheet in sheets:
            sheet.pdf = utils.make_sheet_pdf(sheet.id, title)
            sheet_ids.append(sheet.id)

        session.commit()

        return sheet_ids


Base.metadata.create_all(engine)
