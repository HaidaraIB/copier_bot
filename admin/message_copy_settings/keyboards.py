from telegram import InlineKeyboardButton
from common.lang_dicts import BUTTONS
import models


def build_message_copy_settings_keyboard(
    lang: models.Language = models.Language.ARABIC,
):
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["add_message_copy"],
                callback_data="add_message_copy",
            ),
            InlineKeyboardButton(
                text=BUTTONS[lang]["remove_message_copy"],
                callback_data="remove_message_copy",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["show_message_copies"],
                callback_data="show_message_copies",
            ),
            InlineKeyboardButton(
                text=BUTTONS[lang]["edit_message_copy"],
                callback_data="edit_message_copy",
            ),
        ],
    ]
    return keyboard


def build_edit_message_copy_keyboard(lang: models.Language = models.Language.ARABIC):
    keyboard = [
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["edit_source_chat"],
                callback_data="edit_source_chat",
            ),
            InlineKeyboardButton(
                text=BUTTONS[lang]["edit_target_chat"],
                callback_data="edit_target_chat",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["edit_token_name"],
                callback_data="edit_token_name",
            ),
        ],
        [
            InlineKeyboardButton(
                text=BUTTONS[lang]["edit_links"],
                callback_data="edit_links",
            ),
        ],
    ]
    return keyboard
