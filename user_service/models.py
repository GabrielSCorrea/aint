from enum import IntEnum

from sqlalchemy import Column, Integer, String

from settings import Base, engine, session


class Role(IntEnum):
    ADMINISTRATOR = 0
    PROFESSOR = 1
    STUDENT = 2
    INVIGILATOR = 3


ROLES = []
for role in Role:
    ROLES.append(role.name.lower())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', role='{self.role_name}')>"

    @property
    def role_name(self):
        return Role(self.role).name.lower()

    @staticmethod
    def validate(name, password, role):
        if not name:
            return "name is empty"
        if not password:
            return "password is empty"
        if role not in ROLES:
            return f"invalid role '{role}' (must be one of: {', '.join(ROLES)})"

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
    def bulk_create(cls, users_data):
        for name, password, role in users_data:
            session.add(cls(name=name, password=password, role=Role[role.upper()]))
        session.commit()


Base.metadata.create_all(engine)
