from enum import IntEnum

from sqlalchemy import Column, Integer, String

from settings import Base, engine, session


class Role(IntEnum):
    ADMINISTRATOR = 0
    PROFESSOR = 1
    STUDENT = 2
    INVIGILATOR = 3


ROLES = [role.name.lower() for role in Role]


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Integer, nullable=False)

    def __repr__(self):
        return "<User(id=%d, name='%s', role='%s')>" % (
            self.id,
            self.name,
            self.roleName,
        )

    @property
    def roleName(self):
        return Role(self.role).name.lower()

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
        user = cls(name=name, password=password, role=Role[role.upper()])
        session.add(user)
        session.commit()
        return user

    @classmethod
    def bulkCreate(cls, usersData):
        for name, password, role in usersData:
            session.add(cls(name=name, password=password, role=Role[role.upper()]))
        session.commit()


Base.metadata.create_all(engine)
