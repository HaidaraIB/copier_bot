import models


class SourceChat:
    """Filter to check if a message is from a source chat configured for message copying"""

    def filter(self, chat_id: int):
        with models.session_scope() as s:
            message_copies = (
                s.query(models.MessageCopy)
                .filter(models.MessageCopy.source_chat_id == chat_id)
                .all()
            )
            return len(message_copies) > 0
