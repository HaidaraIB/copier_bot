from telethon.tl.patched import Message
from custom_filters import SourceChat
from bot.functions import send_to_target_chats
import tempfile


async def copy_message_to_target_chats(event):
    if not SourceChat().filter(event.chat_id):
        return

    msg: Message = event.message

    if not all(x in msg.text.lower() for x in ("dext", "screener", "trending", "buy")):
        return

    # Download media to a temporary file (if any)
    temp_path = None
    if msg.media:
        # Create a temp directory & let telethon put the right filename
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = await msg.download_media(file=tmpdir)
            # Telethon returns full file path including original filename

            await send_to_target_chats(msg, temp_path)
            # After this block ends, temp directory is deleted automatically
    else:
        await send_to_target_chats(msg, None)
