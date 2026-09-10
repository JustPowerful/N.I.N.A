from app.db.basemodel import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from typing import Optional
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # start_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # end_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    