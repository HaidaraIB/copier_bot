from telethon.tl.patched import Message
from telethon import events
from TeleClientSingleton import TeleBotSingleton, TeleClientSingleton
from custom_filters import SourceChat
import models
import logging

logger = logging.getLogger(__name__)


async def copy_message_to_target_chats(event: events.NewMessage.Event):
    if not SourceChat().filter(event.chat_id):
        return

    msg: Message = event.message

    if not all(
        [
            x in msg.text.lower()
            for x in ("dext", "screener", "trending", "buy")
        ]
    ):
        return


    with models.session_scope() as s:
        message_copies = (
            s.query(models.MessageCopy)
            .filter(models.MessageCopy.source_chat_id == event.chat_id)
            .all()
        )
        # Copy message to all target chats
        for message_copy in message_copies:
            text = "\n".join(
                msg.text.split("\n")[:-1]
                + [
                    f"<a href='{message_copy.dext_url}'>DexT</a> | <a href='{message_copy.screener_url}'>Screener</a> | <a href='{message_copy.trending_url}'>Trending</a> | <a href='{message_copy.buy_url}'>Buy</a>"
                ]
            )
            await TeleBotSingleton().send_file(
                entity=message_copy.target_chat_id,
                file=event.message.media,
                caption=text,
                parse_mode="html",
            )
