from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from custom_filters import SourceChat
import models
import logging

logger = logging.getLogger(__name__)


async def copy_message_to_target_chats(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if not SourceChat().filter(update):
        return

    if not all(
        [
            x in update.effective_message.caption.lower()
            for x in ("dext", "screener", "trending", "buy")
        ]
    ):
        return

    source_chat_id = update.effective_chat.id

    with models.session_scope() as s:
        message_copies = (
            s.query(models.MessageCopy)
            .filter(models.MessageCopy.source_chat_id == source_chat_id)
            .all()
        )
        # Copy message to all target chats
        for message_copy in message_copies:
            text = "\n".join(
                update.effective_message.caption_html.split("\n")[:-1]
                + [
                    f"<a href='{message_copy.dext_url}'>DexT</a> | <a href='{message_copy.screener_url}'>Screener</a> | <a href='{message_copy.trending_url}'>Trending</a> | <a href='{message_copy.buy_url}'>Buy</a>"
                ]
            )
            await context.bot.send_photo(
                chat_id=message_copy.target_chat_id,
                photo=update.effective_message.photo[-1],
                caption=text,
            )


copy_message_handler = MessageHandler(
    filters=filters.CAPTION,
    callback=copy_message_to_target_chats,
)
