import sqlalchemy as sa
from models.DB import Base
from datetime import datetime
from models.Language import Language


class MessageCopy(Base):
    __tablename__ = "message_copies"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    source_chat_id = sa.Column(sa.BigInteger, nullable=False)
    source_chat_title = sa.Column(sa.String, nullable=False)
    target_chat_id = sa.Column(sa.BigInteger, nullable=False)
    target_chat_title = sa.Column(sa.String, nullable=False)

    token_name = sa.Column(sa.String, nullable=False)
    dext_url = sa.Column(sa.String, nullable=False)
    screener_url = sa.Column(sa.String, nullable=False)
    buy_url = sa.Column(sa.String, nullable=False)
    trending_url = sa.Column(sa.String, nullable=False)

    created_at = sa.Column(sa.DateTime, default=datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.now, onupdate=datetime.now)

    def stringify(self, lang: Language):
        if lang == Language.ARABIC:
            return (
                f"المحادثة المصدر: <b>{self.source_chat_title}</b>\n"
                f"المحادثة الهدف: <b>{self.target_chat_title}</b>\n"
                f"اسم الرمز المميز: <b>{self.token_name}</b>"
            )
        else:
            return (
                f"Source Chat: <b>{self.source_chat_title}</b>\n"
                f"Target Chat: <b>{self.target_chat_title}</b>\n"
                f"Token Name: <b>{self.token_name}</b>"
            )

    def __str__(self):
        return (
            f"Source Chat: <b>{self.source_chat_title}</b>\n"
            f"Target Chat: <b>{self.target_chat_title}</b>\n"
            f"Token Name: <b>{self.token_name}</b>"
        )

    def __repr__(self):
        return f"MessageCopy(id={self.id}, source_chat_id={self.source_chat_id}, target_chat_id={self.target_chat_id}, token_name={self.token_name})"
