from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from bot.config import Script


@Client.on_message(filters.command("help") & filters.private & filters.incoming)
@Client.on_callback_query(filters.regex("^help$"))
async def help(bot: Client, message: Message | CallbackQuery):

    help_message = Script.HELP_MESSAGE

    await bot.reply(
        message,
        text=help_message,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔙 Back", callback_data="start")],
            ]
        ),
    )