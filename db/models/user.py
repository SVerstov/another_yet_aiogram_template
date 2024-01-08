from sqlalchemy import DateTime, text, Integer, BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column as mc
from datetime import datetime
from db.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mc(Integer, primary_key=True)
    tg_id: Mapped[int] = mc(BigInteger, unique=True, index=True)

    username: Mapped[str | None]
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    phone: Mapped[str | None]

    last_seen = Mapped[datetime]
    registered_at: Mapped[datetime] = mc(
        DateTime,
        default=datetime.now(),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    is_admin = mc(Boolean, default=False, nullable=False)
    is_bot_blocked = mc(Boolean, default=False, nullable=False)
    is_blocked = mc(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        res = f"User(id={self.id}, tg_id={self.tg_id}"

        if self.username:
            res += f", username=@{self.username}"
        if self.first_name:
            res += f" {self.first_name}"
        if self.last_name:
            res += f" {self.last_name}"
        return res + ")"
