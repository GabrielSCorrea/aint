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
    # deferred: only loaded when .pdf is accessed, so listings skip the blobs
    pdf = deferred(Column(LargeBinary, nullable=False))

    def __repr__(self):
        return "<ResolutionSheet(id=%d, examId=%d, date='%s', course='%s')>" % (
            self.id,
            self.examId,
            self.date,
            self.course,
        )

    @staticmethod
    def validate(examId, date, course, sheetsNum):
        # arguments arrive over XML-RPC, so their types are not guaranteed
        if not isinstance(examId, int) or examId < 1:
            return "invalid exam id '%s'" % examId
        if not isinstance(date, str) or not date:
            return "date is empty"
        try:
            datetime.date.fromisoformat(date)
        except ValueError:
            return "invalid date '%s' (expected YYYY-MM-DD)" % date
        if not isinstance(course, str) or not course.strip():
            return "course is empty"
        if not isinstance(sheetsNum, int) or sheetsNum < 1:
            return "invalid number of sheets '%s'" % sheetsNum
        return None

    @classmethod
    def exams(cls):
        # one row per exam: (examId, date, course, sheetsNum)
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
        title = "%s - %s" % (course, date)
        # empty pdf placeholder: the QR value is the sheet id,
        # which only exists after the rows are flushed
        sheets = [
            cls(examId=examId, date=date, course=course, pdf=b"")
            for _ in range(sheetsNum)
        ]
        session.add_all(sheets)
        session.flush()
        for sheet in sheets:
            sheet.pdf = utils.makeSheetPdf(sheet.id, title)
        session.commit()
        return [sheet.id for sheet in sheets]


Base.metadata.create_all(engine)
