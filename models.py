from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from database_connection import engine
class Base(DeclarativeBase):
    pass

class RoleBasedUser(Base):
    __tablename__='rolebaseduser'
    id:Mapped[int]= mapped_column(primary_key=True)
    username:Mapped[str]= mapped_column(unique=True)
    password:Mapped[str]
    email:Mapped[str] = mapped_column(nullable=True)
    role:Mapped[str] = mapped_column(default="user")
    
# Base.metadata.create_all(bind=engine)
    
