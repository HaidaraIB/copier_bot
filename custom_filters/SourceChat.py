from telegram import Update
from telegram.ext.filters import BaseFilter
import models


class SourceChat(BaseFilter):
    """Filter to check if a message is from a source chat configured for message copying"""

    def filter(self, update: Update):
        try:
            chat_id = update.effective_chat.id
            with models.session_scope() as s:
                message_copies = (
                    s.query(models.MessageCopy)
                    .filter(models.MessageCopy.source_chat_id == chat_id)
                    .all()
                )
                return len(message_copies) > 0
        except:
            return False
