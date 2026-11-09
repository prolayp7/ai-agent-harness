from sqlalchemy import String, Text, DateTime, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app.core.database import Base

class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    goal: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50))
    final_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    steps: Mapped[list["AgentStepDB"]] = relationship(back_populates="run", cascade="all, delete-orphan")

class AgentStepDB(Base):
    __tablename__ = "agent_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("agent_runs.id"))
    step_number: Mapped[int] = mapped_column(Integer)
    thought: Mapped[str] = mapped_column(Text)
    action_tool: Mapped[str | None] = mapped_column(String(100), nullable=True)
    action_args: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    observation: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)

    run: Mapped["AgentRun"] = relationship(back_populates="steps")