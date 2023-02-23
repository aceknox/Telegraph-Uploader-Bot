#© aceknox
import os
import time
import math
import json
import string
import random
import traceback
import asyncio
import datetime
import aiofiles
from dotenv import load_dotenv
from random import choice 
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid, UserNotParticipant, UserBannedInChannel
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from telegraph import upload_file
from database import Database
from config import config


load_dotenv()
BOT_OWNER = int(os.environ.get("BOT_OWNER","654804764"))
DATABASE_URL = os.environ.get("DATABASE_URL","mongodb+srv://Knoxop24:knoxop24@cluster0.f6m6fwo.mongodb.net/?retryWrites=true&w=majority")
db = Database(DATABASE_URL, "Telegraph-Uploader-Bot")

Bot = Client(
    "Telegraph Uploader Bot V2",
    bot_token=os.environ.get("BOT_TOKEN","5836641197:AAFn6rJE1tLGnbP947OK7wHLGhw26cBIxeM"),
    api_id=int(os.environ.get("API_ID","28457125")),
    api_hash=os.environ.get("API_HASH","c25bda5d2624db06db8a1624d4e484ce")
)

START_TEXT = """**Hi {} 
I am small media or file to telegra.ph link uploader bot.**

>> `I can convert under 5MB photo or video to telegraph link.`

Made by @knoxprojects"""

HELP_TEXT = """**Hey, Follow these steps:**

◽Just give me a media under 5MB
◽Then I will download it
◽I will then upload it to the telegra.ph link

**Available Commands**

/start - Checking Bot Online
/help - For more help
/about - For more about me
/status - For bot updates

Made by @knoxprojects
Support @knoxsupport"""

ABOUT_TEXT = """--**About Me**-- 😎

🤖 **Name :** [Telegraph Uploader](https://telegram.me/{})

👨‍💻 **Developer :** [ace knox](https://github.com/aceknox)

📢 **Channel :** [knox projects](https://telegram.me/knoxprojects)

📬 **Support :** [knox support](https://telegram.me/knoxsupport)

🌐 **Source :** [Click here](https://telegram.me/botsareavailable/2)

📝 **Language :** [Python3](https://python.org)

"""

START_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('⚙ Help', callback_data='help'),
            InlineKeyboardButton('About 🪧', callback_data='about'),
            InlineKeyboardButton('Close 🔻️', callback_data='close')
        ]
    ]
)

HELP_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('🏡 Home', callback_data='home'),
            InlineKeyboardButton('About 🪧', callback_data='about'),
            InlineKeyboardButton('Close 🔻', callback_data='close')
        ]
    ]
)

ABOUT_BUTTONS = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('🏡Home', callback_data='home'),
            InlineKeyboardButton('Help ⚙', callback_data='help'),
            InlineKeyboardButton('Close 🔻', callback_data='close')
        ]
    ]
)


async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return 200, None
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id} : deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id} : user is blocked\n"
    except PeerIdInvalid:
        return 400, f"{user_id} : user id invalid\n"
    except Exception as e:
        return 500, f"{user_id} : {traceback.format_exc()}\n"


@Bot.on_callback_query()
async def cb_handler(bot, update):
    
    if update.data == "home":
        await update.message.edit_text(
            text=START_TEXT.format(update.from_user.mention),
            reply_markup=START_BUTTONS,
            disable_web_page_preview=True
        )
    
    elif update.data == "help":
        await update.message.edit_text(
            text=HELP_TEXT,
            reply_markup=HELP_BUTTONS,
            disable_web_page_preview=True
        )
    
    elif update.data == "about":
        await update.message.edit_text(
            text=ABOUT_TEXT.format((await bot.get_me()).username),
            reply_markup=ABOUT_BUTTONS,
            disable_web_page_preview=True
        )
    
    else:
        await update.message.delete()


@Bot.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    if Config.UPDATES_CHANNEL:
      fsub = await handle_force_subscribe(bot, message)
      if fsub == 400:
        return
    if not await db.is_user_exist(update.from_user.id):
        await db.add_user(update.from_user.id)
    
    await update.reply_text(
        text=START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=START_BUTTONS
    )


@Bot.on_message(filters.private & filters.command(["help"]))
async def help(bot, update):
    
    if not await db.is_user_exist(update.from_user.id):
        await db.add_user(update.from_user.id)
    
    await update.reply_text(
        text=HELP_TEXT,
        disable_web_page_preview=True,
        reply_markup=HELP_BUTTONS
    )


@Bot.on_message(filters.private & filters.command(["about"]))
async def about(bot, update):
    
    if not await db.is_user_exist(update.from_user.id):
        await db.add_user(update.from_user.id)
    
    await update.reply_text(
        text=ABOUT_TEXT.format((await bot.get_me()).username),
        disable_web_page_preview=True,
        reply_markup=ABOUT_BUTTONS
    )


@Bot.on_message(filters.media & filters.private)
async def telegraph_upload(bot, update):
    
    if not await db.is_user_exist(update.from_user.id):
        await db.add_user(update.from_user.id)
    
    text = await update.reply_text(
        text="<code>Downloading ...</code>",
        disable_web_page_preview=True
    )
    media = await update.download()
    
    await text.edit_text(
        text="<code>Downloading Completed. Now I am Uploading to telegra.ph Link ...</code>",
        disable_web_page_preview=True
    )
    
    try:
        response = upload_file(media)
    except Exception as error:
        print(error)
        await text.edit_text(
            text=f"Error :- {error}",
            disable_web_page_preview=True
        )
        return
    
    try:
        os.remove(media)
    except Exception as error:
        print(error)
        return
    
    await text.edit_text(
        text=f"<b>Link :-</b> <code>https://telegra.ph{response[0]}</code>\n\n<b>Join :-</b> @knoxprojects",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="Open Link", url=f"https://telegra.ph{response[0]}"),
                    InlineKeyboardButton(text="Share Link", url=f"https://telegram.me/share/url?url=https://telegra.ph{response[0]}")
                ],
                [InlineKeyboardButton(text="⚙ Join Updates Channel ⚙", url="https://telegram.me/knoxsupport")]
            ]
        )
    )


@Bot.on_message(
    filters.private &
    filters.command("broadcast") &
    filters.user(BOT_OWNER) &
    filters.reply
)
async def broadcast(bot, update, broadcast_ids={}):
    
    all_users = await db.get_all_users()
    broadcast_msg = update
    
    while True:
        broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
        if not broadcast_ids.get(broadcast_id):
            break

    out = await update.reply_text(text=f"Broadcast Started! You will be notified with log file when all the users are notified.")
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    failed = 0
    success = 0
    broadcast_ids[broadcast_id] = dict(total = total_users, current = done, failed = failed, success = success)
        
    async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
        async for user in all_users:
            sts, msg = await send_msg(user_id = int(user['id']), message = broadcast_msg)
            if msg is not None:
                await broadcast_log_file.write(msg)
            if sts == 200:
                success += 1
            else:
                failed += 1
            if sts == 400:
                await db.delete_user(user['id'])
            done += 1
            if broadcast_ids.get(broadcast_id) is None:
                break
            else:
                broadcast_ids[broadcast_id].update(dict(current = done, failed = failed, success = success))
        
    if broadcast_ids.get(broadcast_id):
        broadcast_ids.pop(broadcast_id)
    
    completed_in = datetime.timedelta(seconds=int(time.time()-start_time))
    await asyncio.sleep(3)
    await out.delete()

    if failed == 0:
        await update.reply_text(text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.", quote=True)
    else:
        await update.reply_document(document='broadcast.txt', caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.")
        
    os.remove('broadcast.txt')


@Bot.on_message(filters.private & filters.command("status"), group=5)
async def status(bot, update):

    total_users = await db.total_users_count()
    text = "**Bot Status**\n"
    text += f"\n**Total Users:** `{total_users}`"

    await update.reply_text(
        text=text,
        quote=True,
        disable_web_page_preview=True
    )


Bot.run()
