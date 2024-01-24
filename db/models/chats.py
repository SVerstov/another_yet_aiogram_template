from sqlalchemy import DateTime, text, Integer, BigInteger, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column as mc
from datetime import datetime, date
from db.base import Base
from utils.enums import ChatType


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mc(Integer, primary_key=True)
    tg_id: Mapped[int] = mc(BigInteger, unique=True, index=True)

    title: Mapped[str]
    username: Mapped[str]
    type: Mapped[str] = mc(Enum(ChatType))

    last_active_at: Mapped[date] = mc(Date, default=datetime.today())
    registered_at: Mapped[datetime] = mc(
        DateTime,
        default=datetime.now(),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"Chat({self.title}, id={self.id}, tg_id={self.tg_id})"
