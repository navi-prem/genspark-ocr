from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from dataclasses import dataclass


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

@dataclass
class FileTable(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    blob_key: Mapped[str] = mapped_column(unique=True, nullable=False)
    file_type: Mapped[str] = mapped_column(
        Enum("kb", "rag", name="file_type_enum"), nullable=False
    )
    res_key: Mapped[str]=mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("completed", "pending", "none",name="status_type"), nullable=False
    )
