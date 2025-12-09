from telethon.tl.patched import Message
from TeleClientSingleton import TeleBotSingleton
import models


async def send_to_target_chats(msg: Message, temp_path):
    with models.session_scope() as s:
        message_copies = (
            s.query(models.MessageCopy)
            .filter(models.MessageCopy.source_chat_id == msg.chat_id)
            .all()
        )

    for message_copy in message_copies:

        text = "\n".join(
            msg.text.split("\n")[:-1]
            + [
                f"[DexT]({message_copy.dext_url}) | "
                f"[Screener]({message_copy.screener_url}) | "
                f"[Trending]({message_copy.trending_url}) | "
                f"[Buy]({message_copy.buy_url})"
            ]
        )

        if temp_path:
            await TeleBotSingleton().send_file(
                entity=message_copy.target_chat_id,
                file=temp_path,  # Correct filename + type preserved
                caption=text,
            )
        else:
            await TeleBotSingleton().send_message(
                entity=message_copy.target_chat_id,
                message=text,
            )
