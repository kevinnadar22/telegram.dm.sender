import os

if os.name != "nt":
    import uvloop

    uvloop.install()


import asyncio
import logging
from pyrogram import Client, raw, types, errors
import logging.config
from bot.config import Config
from typing import Iterable, List, Union
from plugins.admin.utils import add_admin
from bot.logger import setup_root_logger
from bot.database import init_db
import pyromod


setup_root_logger()


class Bot(Client):
    def __init__(self):
        super().__init__(
            "bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="plugins"),
        )

    async def start(self, *args, **kwargs):
        await super().start(*args, **kwargs)
        await init_db()
        me = await self.get_me()
        self.owner = await self.get_users(int(Config.OWNER_ID))
        self.username = f"@{me.username}"

        logging.info(f"Bot started as {me.username}")
        logging.info(f"Owner: {self.owner.mention}")
        await add_admin(self.owner.id)
        await set_commands(self)

    async def stop(self, *args):
        await super().stop()

    async def get_users(
        self: "Client",
        user_ids: Union[int, str, Iterable[Union[int, str]]],
        raise_error: bool = True,
        limit: int = 200,
    ) -> Union["types.User", List["types.User"]]:
        """Get information about a user.
        You can retrieve up to 200 users at once.

        Parameters:
            user_ids (``int`` | ``str`` | Iterable of ``int`` or ``str``):
                A list of User identifiers (id or username) or a single user id/username.
                For a contact that exists in your Telegram address book you can use his phone number (str).
            raise_error (``bool``, *optional*):
                If ``True``, an error will be raised if a user_id is invalid or not found.
                If ``False``, the function will continue to the next user_id if one is invalid or not found.
            limit (``int``, *optional*):
                The maximum number of users to retrieve per request. Must be a value between 1 and 200.

        Returns:
            :obj:`~pyrogram.types.User` | List of :obj:`~pyrogram.types.User`: In case *user_ids* was not a list,
            a single user is returned, otherwise a list of users is returned.

        Example:
            .. code-block:: python

                # Get information about one user
                await app.get_users("me")

                # Get information about multiple users at once
                await app.get_users([user_id1, user_id2, user_id3])
        """
        is_iterable = not isinstance(user_ids, (int, str))
        user_ids = list(user_ids) if is_iterable else [user_ids]

        users = types.List()
        user_ids_chunks = [
            user_ids[i : i + limit] for i in range(0, len(user_ids), limit)
        ]

        # Define the `resolve` function with error handling based on the `raise_error` parameter
        async def resolve(user_id):
            try:
                return await self.resolve_peer(user_id)
            except Exception:
                if raise_error:
                    raise
                else:
                    return user_id

        for chunk in user_ids_chunks:
            chunk_resolved = await asyncio.gather(
                *[resolve(i) for i in chunk if i is not None]
            )

            # Remove any `None` values from the resolved user_ids list
            blocked_accounts = [i for i in chunk_resolved if isinstance(i, int)]
            chunk_resolved = list(filter(None, chunk_resolved))
            chunk_resolved = [i for i in chunk_resolved if not isinstance(i, int)]

            r = await self.invoke(raw.functions.users.GetUsers(id=chunk_resolved))

            for i in r:
                users.append(types.User._parse(self, i))

            for i in blocked_accounts:
                users.append(i)

        return users if is_iterable else users[0]

    async def reply(self, query, *args, **kwargs):
        if isinstance(query, types.Message):
            return await query.reply(*args, **kwargs)
        elif isinstance(query, types.CallbackQuery):
            return await query.edit_message_text(*args, **kwargs)
        else:
            raise ValueError("Invalid query type")

    async def floodwait_handler(self, func, *args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except errors.FloodWait as e:
            logging.warning(f"Floodwait for {e.value} seconds")
            await asyncio.sleep(e.value)
            return await self.floodwait_handler(func, *args, **kwargs)


async def set_commands(app: "Bot"):
    COMMANDS = [
        types.BotCommand("start", "Start the bot."),
        types.BotCommand("help", "Need help?"),
    ]
    await app.set_bot_commands(COMMANDS)
