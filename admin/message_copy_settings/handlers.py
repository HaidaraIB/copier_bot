from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    MessageEntity,
)
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from admin.message_copy_settings.keyboards import (
    build_message_copy_settings_keyboard,
    build_edit_message_copy_keyboard,
)
from common.back_to_home_page import back_to_admin_home_page_handler
from common.keyboards import (
    build_admin_keyboard,
    build_back_to_home_page_button,
    build_back_button,
    build_keyboard,
)
from common.lang_dicts import TEXTS, BUTTONS, get_lang
from TeleClientSingleton import TeleBotSingleton, TeleClientSingleton
from custom_filters import PrivateChatAndAdmin, PermissionFilter
from start import admin_command
import models


async def message_copy_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        keyboard = build_message_copy_settings_keyboard(lang)
        keyboard.append(build_back_to_home_page_button(lang=lang, is_admin=True)[0])
        if update.callback_query:
            await update.callback_query.delete_message()
        if update.message and update.message.text == "/back":
            await update.message.reply_text(
                text=TEXTS[lang]["back_done"], reply_markup=ReplyKeyboardRemove()
            )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=TEXTS[lang]["message_copy_settings_title"],
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


message_copy_settings_handler = CallbackQueryHandler(
    message_copy_settings,
    "^message_copy_settings$|^back_to_message_copy_settings$",
)

SOURCE_CHAT_ID, TARGET_CHAT_ID, TOKEN_NAME, LINKS = range(4)


async def add_message_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        if update.callback_query:
            await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                TEXTS[lang]["add_message_copy_source_instruction"]
                + "\n\n"
                + TEXTS[lang]["go_back_with_back_command"]
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=BUTTONS[lang]["channel"],
                            request_chat=KeyboardButtonRequestChat(
                                request_id=8,
                                chat_is_channel=True,
                            ),
                        ),
                        KeyboardButton(
                            text=BUTTONS[lang]["group"],
                            request_chat=KeyboardButtonRequestChat(
                                request_id=9,
                                chat_is_channel=False,
                            ),
                        ),
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return SOURCE_CHAT_ID


back_to_add_message_copy = message_copy_settings


async def get_source_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)

        if update.message:
            if update.message.chat_shared:
                source_chat_id = update.message.chat_shared.chat_id
            else:
                source_chat_id = int(update.message.text)

        try:
            if not update.callback_query:
                await TeleClientSingleton().get_entity(source_chat_id)
                chat = await context.bot.get_chat(chat_id=source_chat_id)
                context.user_data["source_chat_id"] = source_chat_id
                context.user_data["source_chat_title"] = (
                    chat.title if hasattr(chat, "title") else f"Chat {source_chat_id}"
                )
            else:
                await update.callback_query.delete_message()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    TEXTS[lang]["add_message_copy_target_instruction"]
                    + "\n\n"
                    + TEXTS[lang]["go_back_with_back_command"]
                ),
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(
                                text=BUTTONS[lang]["channel"],
                                request_chat=KeyboardButtonRequestChat(
                                    request_id=10,
                                    chat_is_channel=True,
                                ),
                            ),
                            KeyboardButton(
                                text=BUTTONS[lang]["group"],
                                request_chat=KeyboardButtonRequestChat(
                                    request_id=11,
                                    chat_is_channel=False,
                                ),
                            ),
                        ]
                    ],
                    resize_keyboard=True,
                ),
            )
        except ValueError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXTS[lang]["client_should_join_source_chat"],
            )
            return SOURCE_CHAT_ID
        except Exception:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXTS[lang]["chat_not_found"],
            )
            return SOURCE_CHAT_ID
        return TARGET_CHAT_ID


back_to_get_source_chat_id = add_message_copy


async def get_target_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)

        if update.message:
            if update.message.chat_shared:
                target_chat_id = update.message.chat_shared.chat_id
            else:
                target_chat_id = int(update.message.text)

        # Get chat info
        try:
            if not update.callback_query:
                chat = await context.bot.get_chat(chat_id=target_chat_id)
                context.user_data["target_chat_id"] = target_chat_id
                context.user_data["target_chat_title"] = (
                    chat.title if hasattr(chat, "title") else f"Chat {target_chat_id}"
                )
            else:
                await update.callback_query.delete_message()

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXTS[lang]["chat_found"],
                reply_markup=ReplyKeyboardRemove(),
            )
            back_buttons = [
                build_back_button("back_to_get_target_chat_id", lang=lang),
                build_back_to_home_page_button(lang=lang, is_admin=True)[0],
            ]
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXTS[lang]["add_message_copy_token_instruction"],
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return TOKEN_NAME
        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=TEXTS[lang]["chat_not_found"],
            )


back_to_get_target_chat_id = get_source_chat_id


async def get_token_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        token_name = update.message.text.strip()

        if not token_name:
            await update.message.reply_text(
                text=TEXTS[lang]["invalid_token_name"],
            )
            return TOKEN_NAME

        context.user_data["token_name"] = token_name

        back_buttons = [
            build_back_button("back_to_get_token_name", lang=lang),
            build_back_to_home_page_button(lang=lang, is_admin=True)[0],
        ]
        await update.message.reply_text(
            text=TEXTS[lang]["add_message_copy_links_instruction"],
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return LINKS


back_to_get_token_name = get_target_chat_id


async def get_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        labels = ["dext", "screener", "buy", "trending"]

        links = {}
        for entity in update.message.entities:
            if entity.type == "text_link" and entity.url:
                link_text = update.message.text[
                    entity.offset : entity.offset + entity.length
                ].lower()
                if link_text in labels:
                    links[link_text.strip()] = entity.url

        # Check if we have all required links
        if len(links) != 4:
            await update.message.reply_text(
                text=TEXTS[lang]["invalid_links_format"],
            )
            return LINKS

        # Get data from context
        source_chat_id = context.user_data["source_chat_id"]
        target_chat_id = context.user_data["target_chat_id"]
        source_chat_title = context.user_data["source_chat_title"]
        target_chat_title = context.user_data["target_chat_title"]
        token_name = context.user_data["token_name"]

        # Save to database
        with models.session_scope() as s:
            new_message_copy = models.MessageCopy(
                source_chat_id=source_chat_id,
                source_chat_title=source_chat_title,
                target_chat_id=target_chat_id,
                target_chat_title=target_chat_title,
                token_name=token_name,
                dext_url=links["dext"],
                screener_url=links["screener"],
                buy_url=links["buy"],
                trending_url=links["trending"],
            )
            s.add(new_message_copy)

        # Clean up user_data
        context.user_data.pop("source_chat_id", None)
        context.user_data.pop("target_chat_id", None)
        context.user_data.pop("source_chat_title", None)
        context.user_data.pop("target_chat_title", None)
        context.user_data.pop("token_name", None)

        await update.message.reply_text(
            text=TEXTS[lang]["message_copy_added_success"],
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )
        return ConversationHandler.END


add_message_copy_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_message_copy,
            pattern="^add_message_copy$",
        ),
    ],
    states={
        SOURCE_CHAT_ID: [
            MessageHandler(
                filters=filters.Regex(r"^-?\d+$") | filters.StatusUpdate.CHAT_SHARED,
                callback=get_source_chat_id,
            ),
            CommandHandler(
                command="back",
                callback=back_to_add_message_copy,
            ),
        ],
        TARGET_CHAT_ID: [
            MessageHandler(
                filters=filters.Regex(r"^-?\d+$") | filters.StatusUpdate.CHAT_SHARED,
                callback=get_target_chat_id,
            ),
            CommandHandler(
                command="back",
                callback=back_to_get_source_chat_id,
            ),
        ],
        TOKEN_NAME: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_token_name,
            ),
        ],
        LINKS: [
            MessageHandler(
                filters=filters.Entity(MessageEntity.TEXT_LINK),
                callback=get_links,
            ),
        ],
    },
    fallbacks=[
        message_copy_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(
            callback=back_to_get_target_chat_id,
            pattern="^back_to_get_target_chat_id$",
        ),
        CallbackQueryHandler(
            callback=back_to_get_token_name,
            pattern="^back_to_get_token_name$",
        ),
    ],
)


CHOOSE_MESSAGE_COPY_TO_REMOVE = range(1)


async def remove_message_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:
            if update.callback_query.data.isnumeric():
                message_copy = s.get(
                    models.MessageCopy, int(update.callback_query.data)
                )
                if message_copy:
                    s.delete(message_copy)
                    s.commit()
                    await update.callback_query.answer(
                        text=TEXTS[lang]["message_copy_removed_success"],
                        show_alert=True,
                    )

            message_copies = s.query(models.MessageCopy).all()

            if not message_copies:
                await update.callback_query.answer(
                    text=TEXTS[lang]["no_message_copies"],
                    show_alert=True,
                )
                if update.callback_query.data.isnumeric():
                    await update.callback_query.edit_message_text(
                        text=TEXTS[lang]["home_page"],
                        reply_markup=build_admin_keyboard(
                            lang=lang, user_id=update.effective_user.id
                        ),
                    )
                return ConversationHandler.END

            message_copy_keyboard = build_keyboard(
                columns=1,
                texts=[
                    f"{message_copy.token_name} ({message_copy.source_chat_title} → {message_copy.target_chat_title})"
                    for message_copy in message_copies
                ],
                buttons_data=[str(message_copy.id) for message_copy in message_copies],
            )
            message_copy_keyboard.append(
                build_back_button("back_to_message_copy_settings", lang=lang)
            )
            message_copy_keyboard.append(
                build_back_to_home_page_button(lang=lang, is_admin=True)[0]
            )
            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["remove_message_copy_instruction"],
                reply_markup=InlineKeyboardMarkup(message_copy_keyboard),
            )
        return CHOOSE_MESSAGE_COPY_TO_REMOVE


remove_message_copy_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=remove_message_copy,
            pattern="^remove_message_copy$",
        ),
    ],
    states={
        CHOOSE_MESSAGE_COPY_TO_REMOVE: [
            CallbackQueryHandler(
                remove_message_copy,
                "^[0-9]+$",
            ),
        ]
    },
    fallbacks=[
        message_copy_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)


async def show_message_copies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:
            message_copies = s.query(models.MessageCopy).all()

            if not message_copies:
                await update.callback_query.answer(
                    text=TEXTS[lang]["no_message_copies"],
                    show_alert=True,
                )
                return
            text = TEXTS[lang]["message_copies_list_title"] + "\n\n"
            for message_copy in message_copies:
                text += message_copy.stringify(lang) + "\n\n"
            text += TEXTS[lang]["continue_with_admin_command"]

        keyboard = [
            build_back_button("back_to_message_copy_settings", lang=lang),
            build_back_to_home_page_button(lang=lang, is_admin=True)[0],
        ]
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


show_message_copies_handler = CallbackQueryHandler(
    callback=show_message_copies,
    pattern="^show_message_copies$",
)


(
    CHOOSE_MESSAGE_COPY_TO_EDIT,
    EDITING_MESSAGE_COPY,
    EDIT_SOURCE_CHAT,
    EDIT_TARGET_CHAT,
    EDIT_TOKEN,
    EDIT_LINKS,
) = range(6)


async def edit_message_copy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        with models.session_scope() as s:
            message_copies = s.query(models.MessageCopy).all()

            if not message_copies:
                await update.callback_query.answer(
                    text=TEXTS[lang]["no_message_copies"],
                    show_alert=True,
                )
                return ConversationHandler.END

            message_copy_keyboard = build_keyboard(
                columns=1,
                texts=[
                    f"{mc.token_name} ({mc.source_chat_title} → {mc.target_chat_title})"
                    for mc in message_copies
                ],
                buttons_data=[str(mc.id) for mc in message_copies],
            )
            message_copy_keyboard.append(
                build_back_button("back_to_message_copy_settings", lang=lang)
            )
            message_copy_keyboard.append(
                build_back_to_home_page_button(lang=lang, is_admin=True)[0]
            )

            await update.callback_query.edit_message_text(
                text=TEXTS[lang]["select_message_copy_to_edit"],
                reply_markup=InlineKeyboardMarkup(message_copy_keyboard),
            )
        return CHOOSE_MESSAGE_COPY_TO_EDIT


async def show_edit_message_copy_options(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        if update.callback_query:
            message_copy_id = int(update.callback_query.data)
            context.user_data["editing_message_copy_id"] = message_copy_id

        keyboard = build_edit_message_copy_keyboard(lang=lang)
        keyboard.append(
            build_back_button("back_to_choose_message_copy_to_edit", lang=lang)
        )
        keyboard.append(build_back_to_home_page_button(lang=lang, is_admin=True)[0])

        with models.session_scope() as s:
            message_copy = s.get(models.MessageCopy, message_copy_id)
            message_copy_info = f"<b>{TEXTS[lang]['message_copy_info']}</b>\n{message_copy.stringify(lang)}\n\n"
            message_copy_info += TEXTS[lang]["select_field_to_edit"]
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text=message_copy_info,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
            else:
                await update.message.reply_text(
                    text=message_copy_info,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
        return EDITING_MESSAGE_COPY


back_to_choose_message_copy_to_edit = edit_message_copy


async def start_edit_source_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                TEXTS[lang]["edit_source_chat_instruction"]
                + "\n\n"
                + TEXTS[lang]["go_back_with_back_command"]
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=BUTTONS[lang]["channel"],
                            request_chat=KeyboardButtonRequestChat(
                                request_id=12,
                                chat_is_channel=True,
                            ),
                        ),
                        KeyboardButton(
                            text=BUTTONS[lang]["group"],
                            request_chat=KeyboardButtonRequestChat(
                                request_id=13,
                                chat_is_channel=False,
                            ),
                        ),
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return EDIT_SOURCE_CHAT


back_to_start_edit_source_chat = show_edit_message_copy_options


async def save_source_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        message_copy_id = context.user_data.get("editing_message_copy_id")

        if update.effective_message.chat_shared:
            new_source_chat_id = update.effective_message.chat_shared.chat_id
        else:
            new_source_chat_id = int(update.message.text)

        try:
            await TeleClientSingleton().get_entity(new_source_chat_id)
            new_source_chat = await context.bot.get_chat(chat_id=new_source_chat_id)
            with models.session_scope() as s:
                message_copy = s.get(models.MessageCopy, message_copy_id)
                if message_copy:
                    message_copy.source_chat_id = new_source_chat_id
                    message_copy.source_chat_title = new_source_chat.title
            await update.message.reply_text(
                text=TEXTS[lang]["message_copy_updated_success"],
                reply_markup=ReplyKeyboardRemove(),
            )
            await update.message.reply_text(
                text=TEXTS[lang]["home_page"],
                reply_markup=build_admin_keyboard(lang, update.effective_user.id),
            )
            return ConversationHandler.END
        except ValueError:
            await update.message.reply_text(text=TEXTS[lang]["client_should_join_source_chat"])
        except Exception:
            await update.message.reply_text(text=TEXTS[lang]["chat_not_found"])


async def start_edit_target_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                TEXTS[lang]["edit_target_chat_instruction"]
                + "\n\n"
                + TEXTS[lang]["go_back_with_back_command"]
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text=BUTTONS[lang]["channel"],
                            request_chat=KeyboardButtonRequestChat(
                                request_id=14,
                                chat_is_channel=True,
                            ),
                        ),
                        KeyboardButton(
                            text=BUTTONS[lang]["group"],
                            request_chat=KeyboardButtonRequestChat(
                                request_id=15,
                                chat_is_channel=False,
                            ),
                        ),
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return EDIT_TARGET_CHAT


back_to_start_edit_target_chat = show_edit_message_copy_options


async def save_target_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        message_copy_id = context.user_data.get("editing_message_copy_id")

        if update.effective_message.chat_shared:
            new_target_chat_id = update.effective_message.chat_shared.chat_id
        else:
            new_target_chat_id = int(update.message.text)

        try:
            new_target_chat = await context.bot.get_chat(chat_id=new_target_chat_id)
            with models.session_scope() as s:
                message_copy = s.get(models.MessageCopy, message_copy_id)
                if message_copy:
                    message_copy.target_chat_id = new_target_chat_id
                    message_copy.target_chat_title = new_target_chat.title

            await update.message.reply_text(
                text=TEXTS[lang]["message_copy_updated_success"],
                reply_markup=ReplyKeyboardRemove(),
            )
            await update.message.reply_text(
                text=TEXTS[lang]["home_page"],
                reply_markup=build_admin_keyboard(lang, update.effective_user.id),
            )
            return ConversationHandler.END

        except Exception:
            await update.message.reply_text(text=TEXTS[lang]["chat_not_found"])


async def start_edit_token_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        back_buttons = [
            build_back_button("back_to_start_edit_token_name", lang=lang),
            build_back_to_home_page_button(lang=lang, is_admin=True)[0],
        ]
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["edit_token_name_instruction"],
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return EDIT_TOKEN


back_to_start_edit_token_name = show_edit_message_copy_options


async def save_token_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        message_copy_id = context.user_data.get("editing_message_copy_id")
        new_token_name = update.message.text.strip()

        with models.session_scope() as s:
            message_copy = s.get(models.MessageCopy, message_copy_id)
            if message_copy:
                message_copy.token_name = new_token_name

        await update.message.reply_text(
            text=TEXTS[lang]["message_copy_updated_success"],
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )
        return ConversationHandler.END


async def start_edit_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        back_buttons = [
            build_back_button("back_to_start_edit_links", lang),
            build_back_to_home_page_button(lang=lang, is_admin=True)[0],
        ]
        await update.callback_query.edit_message_text(
            text=TEXTS[lang]["edit_links_instruction"],
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return EDIT_LINKS


back_to_start_edit_links = show_edit_message_copy_options


async def save_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if PrivateChatAndAdmin().filter(update) and PermissionFilter(
        models.Permission.MANAGE_MESSAGE_COPY
    ).filter(update):
        lang = get_lang(update.effective_user.id)
        message_copy_id = context.user_data.get("editing_message_copy_id")
        labels = ["dext", "screener", "buy", "trending"]

        links = {}
        for entity in update.message.entities:
            if entity.type == "text_link" and entity.url:
                link_text = update.message.text[
                    entity.offset : entity.offset + entity.length
                ].lower()
                if link_text in labels:
                    links[link_text.strip()] = entity.url

        if len(links) != 4:
            await update.message.reply_text(
                text=TEXTS[lang]["invalid_links_format"],
            )
            return EDIT_LINKS

        with models.session_scope() as s:
            message_copy = s.get(models.MessageCopy, message_copy_id)
            if message_copy:
                message_copy.dext_url = links["dext"]
                message_copy.screener_url = links["screener"]
                message_copy.buy_url = links["buy"]
                message_copy.trending_url = links["trending"]
        await update.message.reply_text(
            text=TEXTS[lang]["message_copy_updated_success"],
            reply_markup=build_admin_keyboard(lang, update.effective_user.id),
        )
        return ConversationHandler.END


edit_message_copy_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=edit_message_copy,
            pattern="^edit_message_copy$",
        ),
    ],
    states={
        CHOOSE_MESSAGE_COPY_TO_EDIT: [
            CallbackQueryHandler(
                callback=show_edit_message_copy_options,
                pattern=r"^[0-9]+$",
            ),
        ],
        EDITING_MESSAGE_COPY: [
            CallbackQueryHandler(
                callback=start_edit_source_chat,
                pattern="^edit_source_chat$",
            ),
            CallbackQueryHandler(
                callback=start_edit_target_chat,
                pattern="^edit_target_chat$",
            ),
            CallbackQueryHandler(
                callback=start_edit_token_name,
                pattern="^edit_token_name$",
            ),
            CallbackQueryHandler(
                callback=start_edit_links,
                pattern="^edit_links$",
            ),
        ],
        EDIT_SOURCE_CHAT: [
            MessageHandler(
                filters=filters.Regex(r"^-?\d+$") | filters.StatusUpdate.CHAT_SHARED,
                callback=save_source_chat,
            ),
            CommandHandler(
                command="back",
                callback=back_to_start_edit_source_chat,
            ),
        ],
        EDIT_TARGET_CHAT: [
            MessageHandler(
                filters=filters.Regex(r"^-?\d+$") | filters.StatusUpdate.CHAT_SHARED,
                callback=save_target_chat,
            ),
            CommandHandler(
                command="back",
                callback=back_to_start_edit_target_chat,
            ),
        ],
        EDIT_TOKEN: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=save_token_name,
            ),
        ],
        EDIT_LINKS: [
            MessageHandler(
                filters=filters.Entity(MessageEntity.TEXT_LINK),
                callback=save_links,
            ),
        ],
    },
    fallbacks=[
        message_copy_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(
            callback=back_to_choose_message_copy_to_edit,
            pattern="^back_to_choose_message_copy_to_edit$",
        ),
        CallbackQueryHandler(
            callback=back_to_start_edit_token_name,
            pattern="^back_to_start_edit_token_name$",
        ),
        CallbackQueryHandler(
            callback=back_to_start_edit_links,
            pattern="^back_to_start_edit_links$",
        ),
    ],
)
