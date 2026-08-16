# ============================================================
# JASMINE X MUSIC
# Corrected clean version
# ============================================================

import asyncio
import os
import sqlite3
import time

from pyrogram import Client, filters, idle
from pyrogram.enums import ChatType
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

# PyTgCalls is optional
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import MediaStream
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PyTgCalls = None
    MediaStream = None
    PYTGCALLS_AVAILABLE = False

from yt_dlp import YoutubeDL


# ============================================================
# CONFIG
# ============================================================

API_ID = 30672609

API_HASH = "7b1d2b631725691a89df22a377f3c53a"
BOT_TOKEN = "8835783533:AAHiWongoQnSuZqdQBROsph_DMKPfImLqhA"
SESSION_STRING = "1BVtsOJ8Bu3_uu1j7BKSQQKEwlxZTDKoeiPafFWpSLteCvqem886-IwLU_CzEEvpZiovba5LtFQC_wIN9JWqDa2iiXfys35n3HbTowfqL5J3qJoARvo1ODvPes0whQCuqV0l6s--_y6WnO35L12fe4IXJBY70IYhTejshOUxF_D01ylgvGxAAQICJQHVOIySV12Reu-_PFdIBMi_sDfUqlKbUdQA7xD5k6yYoL7XOjr7-YgWrlXNSGzSDpxWxK0cc5B2wOPGrmrYyMMhN4vtOX_k4pqDalRk7eiKtn8Vx67-Ukx5ffQcz7gTPvf8NE2U6erK1fpnEdabpCOJ7NJ5PVPFReiblE18="

OWNER_ID = 7499742938

INITIAL_ADMINS = {
    6239941845,
}

BOT_NAME = "JASMINE X MUSIC"
BOT_USERNAME = "JasmineXmusicbot"


# ============================================================
# SUPPORT / CHANNELS
# ============================================================

SUPPORT_GROUP = "https://t.me/+rSUEvBcRswkwYThh"
SUPPORT_GROUP_ID = -1004462544512

SUPPORT_CHANNEL = "https://t.me/AS_WORKSPACE"
SUPPORT_CHANNEL_ID = -1003598183958

UPDATE_CHANNEL = "https://t.me/Jasminesupport"
UPDATE_CHANNEL_ID = -1004402662430


# ============================================================
# START
# ============================================================

START_PHOTO = ""

START_MESSAGE = """🎵 **JASMINE X MUSIC**

Welcome to JASMINE X MUSIC.

🎧 Music • 🎬 Video • ⚡ Fast Playback

Use /help to see all commands.
"""


# ============================================================
# DATABASE
# ============================================================

DB_FILE = "jasmine_music.db"

db = sqlite3.connect(
    DB_FILE,
    check_same_thread=False
)

db.row_factory = sqlite3.Row


db.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        added_at INTEGER
    )
    """
)


db.execute(
    """
    CREATE TABLE IF NOT EXISTS groups (
        chat_id INTEGER PRIMARY KEY,
        title TEXT,
        added_at INTEGER
    )
    """
)


db.execute(
    """
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        added_by INTEGER,
        added_at INTEGER
    )
    """
)

db.commit()


def save_user(user):

    if not user:
        return

    db.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, first_name, username, added_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            user.id,
            user.first_name or "",
            user.username or "",
            int(time.time()),
        ),
    )

    db.commit()


def save_group(chat):

    if not chat:
        return

    db.execute(
        """
        INSERT OR IGNORE INTO groups
        (chat_id, title, added_at)
        VALUES (?, ?, ?)
        """,
        (
            chat.id,
            chat.title or "",
            int(time.time()),
        ),
    )

    db.commit()


def add_admin(user_id, added_by):

    db.execute(
        """
        INSERT OR REPLACE INTO admins
        (user_id, added_by, added_at)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            added_by,
            int(time.time()),
        ),
    )

    db.commit()


def remove_admin(user_id):

    db.execute(
        "DELETE FROM admins WHERE user_id = ?",
        (user_id,),
    )

    db.commit()


def is_bot_admin(user_id):

    if user_id == OWNER_ID:
        return True

    row = db.execute(
        "SELECT user_id FROM admins WHERE user_id = ?",
        (user_id,),
    ).fetchone()

    return row is not None


def admin_list():

    rows = db.execute(
        "SELECT user_id FROM admins ORDER BY added_at"
    ).fetchall()

    return [row["user_id"] for row in rows]


for admin_id in INITIAL_ADMINS:
    add_admin(admin_id, OWNER_ID)


# ============================================================
# PYROGRAM
# ============================================================

bot = Client(
    "jasmine_x_music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


user = Client(
    "jasmine_x_music_user",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
)


calls = (
    PyTgCalls(user)
    if PYTGCALLS_AVAILABLE
    else None
)


# ============================================================
# QUEUES
# ============================================================

queues = {}


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(query):

    options = {
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "noplaylist": True,
        "skip_download": True,
        "format": "best",
    }

    with YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            query,
            download=False
        )

    if not info:
        raise RuntimeError(
            "No result found."
        )

    if "entries" in info:

        entries = info.get("entries") or []

        if not entries:
            raise RuntimeError(
                "No result found."
            )

        info = entries[0]

    webpage = info.get("webpage_url")

    if not webpage:
        webpage = info.get("original_url")

    if not webpage:
        webpage = query

    return {
        "title": info.get(
            "title",
            "Unknown"
        ),
        "url": webpage,
    }


# ============================================================
# START KEYBOARD
# ============================================================

def start_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🎵 Commands",
                    callback_data="commands",
                ),

                InlineKeyboardButton(
                    "➕ Add Me",
                    url=(
                        f"https://t.me/"
                        f"{BOT_USERNAME}"
                        f"?startgroup=true"
                    ),
                ),
            ],

            [
                InlineKeyboardButton(
                    "📢 Updates",
                    url=UPDATE_CHANNEL,
                ),

                InlineKeyboardButton(
                    "💬 Support",
                    url=SUPPORT_GROUP,
                ),
            ],
        ]
    )


# ============================================================
# /START
# ============================================================

@bot.on_message(
    filters.command("start")
)
async def start_command(_, message: Message):

    if message.from_user:
        save_user(
            message.from_user
        )

    keyboard = start_keyboard()

    if START_PHOTO:

        await message.reply_photo(
            START_PHOTO,
            caption=START_MESSAGE,
            reply_markup=keyboard,
        )

    else:

        await message.reply_text(
            START_MESSAGE,
            reply_markup=keyboard,
        )


# ============================================================
# /HELP
# ============================================================

@bot.on_message(
    filters.command("help")
)
async def help_command(_, message: Message):

    text = """🎵 **JASMINE X MUSIC**

**Music**

/play <song>
/vplay <video>
/skip
/pause
/resume
/stop
/queue
/song
/shuffle
/clear

**Bot Admin**

/admins
/addadmin <user_id>
/deladmin <user_id>
/stats
/ping
/broadcast <message>
/broadcast_groups <message>
/panel
/restart
"""

    await message.reply_text(
        text
    )


# ============================================================
# COMMANDS BUTTON
# ============================================================

@bot.on_callback_query(
    filters.regex("^commands$")
)
async def commands_callback(
    _,
    query: CallbackQuery
):

    await query.answer()

    await query.message.edit_text(

        """🎵 **JASMINE X MUSIC**

▶️ `/play song`
🎬 `/vplay video`
⏭ `/skip`
⏸ `/pause`
▶️ `/resume`
⏹ `/stop`
📜 `/queue`
🎵 `/song`
🔀 `/shuffle`
🗑 `/clear`

Use /help for more commands.
""",

        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="back_start",
                    )
                ]
            ]
        ),
    )


@bot.on_callback_query(
    filters.regex("^back_start$")
)
async def back_start_callback(
    _,
    query: CallbackQuery
):

    await query.answer()

    await query.message.delete()

    if START_PHOTO:

        await bot.send_photo(
            query.message.chat.id,
            START_PHOTO,
            caption=START_MESSAGE,
            reply_markup=start_keyboard(),
        )

    else:

        await bot.send_message(
            query.message.chat.id,
            START_MESSAGE,
            reply_markup=start_keyboard(),
        )


# ============================================================
# SAVE USERS + GROUPS
# ============================================================

@bot.on_message(
    filters.incoming
)
async def database_handler(
    _,
    message: Message
):

    try:

        if message.from_user:
            save_user(
                message.from_user
            )

        if message.chat.type in (
            ChatType.GROUP,
            ChatType.SUPERGROUP,
        ):

            save_group(
                message.chat
            )

    except Exception:

        pass


# ============================================================
# GROUP ADMIN CHECK
# ============================================================

async def group_admin_required(
    message
):

    if not message.from_user:
        return False

    if is_bot_admin(
        message.from_user.id
    ):
        return True

    try:

        member = await bot.get_chat_member(
            message.chat.id,
            message.from_user.id,
        )

        return str(
            member.status
        ) in (
            "administrator",
            "owner",
        )

    except Exception:

        return False


# ============================================================
# PLAY HELPER
# ============================================================

async def play_item(
    chat_id,
    item
):

    if not PYTGCALLS_AVAILABLE:

        raise RuntimeError(
            "PyTgCalls is not installed on "
            "this hosting service."
        )

    await calls.play(

        chat_id,

        MediaStream(
            item["url"],
            video_flags=(
                MediaStream.Flags.IGNORE
            ),
        ),
    )


# ============================================================
# /PLAY
# ============================================================

@bot.on_message(
    filters.command("play")
)
async def play_command(
    _,
    message: Message
):

    if message.chat.type not in (
        ChatType.GROUP,
        ChatType.SUPERGROUP,
    ):

        await message.reply_text(
            "❌ Use /play inside a group."
        )

        return

    if len(message.command) < 2:

        await message.reply_text(
            "🎵 Usage:\n"
            "`/play song name`"
        )

        return

    if not PYTGCALLS_AVAILABLE:

        await message.reply_text(
            "❌ Music playback is unavailable.\n\n"
            "This hosting service does not have "
            "PyTgCalls installed."
        )

        return

    query = " ".join(
        message.command[1:]
    )

    status = await message.reply_text(
        "🔎 **Searching...**"
    )

    try:

        item = await asyncio.to_thread(
            youtube_search,
            query,
        )

    except Exception as exc:

        await status.edit_text(
            "❌ Search failed.\n\n"
            f"`{str(exc)[:500]}`"
        )

        return
f"**{item['title']}**"
    chat_id = message.chat.id

    if chat_id not in queues:
        queues[chat_id] = []

    queues[chat_id].append(
        item
    )

    if len(queues[chat_id]) > 1:

        await status.edit_text(
            "✅ **Added to queue**\n\n"
            f"🎵 {item['title']}\n"
            f"📍 Position: "
            f"`{len(queues[chat_id])}`"
        )

        return

    try:

        await play_item(
            chat_id,
            item
        )

        await status.edit_text(
            "🎵 **Now Playing**\n\n"
            f"
