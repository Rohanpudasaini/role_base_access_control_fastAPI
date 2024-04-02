from sqlalchemy import ForeignKey, ARRAY, String
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from enum import Enum

class RoleEnum(str,Enum):
    user = 'user'
    admin = 'admin'
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__='users'
    id:Mapped[int]= mapped_column(primary_key=True)
    username:Mapped[str]= mapped_column(unique=True)
    password:Mapped[str]
    email:Mapped[str] = mapped_column(nullable=True)
    role_id:Mapped[int] = mapped_column(ForeignKey('roles.id'))
    roles = relationship('Role',back_populates='users')
    
class Role(Base):
    __tablename__='roles'
    id:Mapped[int] = mapped_column(primary_key=True)
    role:Mapped[str] = mapped_column(default=RoleEnum.user)
    permission = mapped_column(ARRAY(String),default=['home'])
    users = relationship('User', back_populates='roles')

