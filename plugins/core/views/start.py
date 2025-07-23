from pyrogram import Client, filters
from pyrogram.types import Message
from bot.config import Script
from ..utils.helpers import add_user


@Client.on_message(filters.command("start") & filters.private & filters.incoming)
@Client.on_callback_query(filters.regex("^start$"))
async def start(bot: Client, message: Message):
    # get or create user
    await add_user(message.from_user.id)

    text = Script.START_MESSAGE
    await bot.reply(message, text)