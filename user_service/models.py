from sqlalchemy import Column, Integer, String

from settings import Base, engine, session

ROLES = ["administrator", "professor", "student", "invigilator"]


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

    def __repr__(self):
        return "<User(id=%d, name='%s', role='%s')>" % (self.id, self.name, self.role)

    @staticmethod
    def validate(name, password, role):
        if not name:
            return "name is empty"
        if not password:
            return "password is empty"
        if role not in ROLES:
            return "invalid role '%s' (must be one of: %s)" % (role, ", ".join(ROLES))
        return None

    @classmethod
    def all(cls):
        return session.query(cls).order_by(cls.id).all()

    @classmethod
    def create(cls, name, password, role):
        user = cls(name=name, password=password, role=role)
        session.add(user)
        session.commit()
        return user

    @classmethod
    def bulkCreate(cls, usersData):
        for name, password, role in usersData:
            session.add(cls(name=name, password=password, role=role))
        session.commit()


Base.metadata.create_all(engine)
