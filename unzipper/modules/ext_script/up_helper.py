# Copyright (c) 2022 - 2024 EDM115
import asyncio
import os
import pathlib
import re
import shutil
import subprocess

from datetime import timedelta
from time import time
from pyrogram.errors import FloodWait, PhotoExtInvalid, PhotoSaveFileInvalid

from config import Config
from unzipper import LOGGER, unzipperbot
from unzipper.helpers.database import get_upload_mode
from unzipper.helpers.unzip_help import (
    extentions_list,
    progress_for_pyrogram,
    progress_urls,
)
from unzipper.modules.bot_data import Messages
from unzipper.modules.ext_script.custom_thumbnail import thumb_exists
from unzipper.modules.ext_script.metadata_helper import get_audio_metadata


async def run_shell_cmds(command):
    run = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    shell_output = run.stdout.read()[:-1].decode("utf-8").rstrip(
        "\n"
    ) + run.stderr.read()[:-1].decode("utf-8").rstrip("\n")
    LOGGER.info("shell_output : " + shell_output)
    if run.stderr:
        run.stderr.close()
    if run.stdout:
        run.stdout.close()
    return shell_output


async def get_size(doc_f):
    try:
        fsize = os.stat(doc_f).st_size
        return fsize
    except:
        return -1


async def send_file(unzip_bot, c_id, doc_f, query, full_path, log_msg, split):
    fsize = await get_size(doc_f)
    if fsize in (-1, 0):
        try:
            await unzipperbot.send_message(
                c_id, Messages.EMPTY_FILE.format(os.path.basename(doc_f))
            )
        except:
            pass
        return
    try:
        ul_mode = await get_upload_mode(c_id)
        fname = os.sep.join(os.path.abspath(doc_f).split(os.sep)[5:])
        fext = (pathlib.Path(os.path.abspath(doc_f)).suffix).casefold().replace(".", "")
        thumbornot = await thumb_exists(c_id)
        upmsg = await unzipperbot.send_message(
            c_id, Messages.PROCESSING2, disable_notification=True
        )
        
        # Check if file size is greater than 50 MB
        if fsize > 50 * 1024 * 1024:
            thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg" if thumbornot else None
        else:
            thumb_image = None
        
        if ul_mode == "media" and fext in extentions_list["audio"]:
            metadata = await get_audio_metadata(doc_f)
            await unzip_bot.send_audio(
                chat_id=c_id,
                audio=doc_f,
                caption=Messages.EXT_CAPTION.format(fname),
                duration=metadata["duration"],
                performer=metadata["performer"],
                title=metadata["title"],
                thumb=thumb_image if thumbornot else None,
                disable_notification=True,
                progress=progress_for_pyrogram,
                progress_args=(
                    Messages.TRY_UP.format(fname),
                    upmsg,
                    time(),
                    unzip_bot,
                ),
            )
        elif ul_mode == "media" and fext in extentions_list["photo"]:
            try:
                await unzip_bot.send_photo(
                    chat_id=c_id,
                    photo=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Messages.TRY_UP.format(fname),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )
            except (PhotoExtInvalid, PhotoSaveFileInvalid):
                await unzip_bot.send_document(
                    chat_id=c_id,
                    document=doc_f,
                    thumb=thumb_image if thumbornot else None,
                    caption=Messages.EXT_CAPTION.format(fname),
                    force_document=True,
                    disable_notification=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Messages.TRY_UP.format(fname),
                        upmsg,
                        time(),
                        unzip_bot,
                    ),
                )
        elif ul_mode == "media" and fext in extentions_list["video"]:
            vid_duration = await run_shell_cmds(
                f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{doc_f}"'
            )
            # Generate thumbnail for video
            thumb_image = Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg"
            await run_shell_cmds(
                f'ffmpeg -i "{doc_f}" -ss 00:00:01.000 -vframes 1 "{thumb_image}"'
            )
            await unzip_bot.send_video(
                chat_id=c_id,
                video=doc_f,
                caption=Messages.EXT_CAPTION.format(fname),
                duration=int(float(vid_duration)) if vid_duration.replace(".", "").isnumeric() else 0,
                thumb=thumb_image,
                disable_notification=True,
                progress=progress_for_pyrogram,
                progress_args=(
                    Messages.TRY_UP.format(fname),
                    upmsg,
                    time(),
                    unzip_bot,
                ),
            )
        else:
            await unzip_bot.send_document(
                chat_id=c_id,
                document=doc_f,
                thumb=thumb_image if thumbornot else None,
                caption=Messages.EXT_CAPTION.format(fname),
                force_document=True,
                disable_notification=True,
                progress=progress_for_pyrogram,
                progress_args=(
                    Messages.TRY_UP.format(fname),
                    upmsg,
                    time(),
                    unzip_bot,
                ),
            )
        
        await upmsg.delete()
        os.remove(doc_f)
    except FloodWait as f:
        await asyncio.sleep(f.value)
        return await send_file(unzip_bot, c_id, doc_f, query, full_path, log_msg, split)
    except FileNotFoundError:
        try:
            await unzipperbot.send_message(
                c_id, Messages.CANT_FIND.format(os.path.basename(doc_f))
            )
        except:
            pass
        return
    except BaseException as e:
        LOGGER.error(e)
        shutil.rmtree(full_path)

async def forward_file(message, cid):
    try:
        await unzipperbot.copy_message(
            chat_id=cid,
            from_chat_id=message.chat.id,
            message_id=message.id,
            disable_notification=True,
        )
    except FloodWait as f:
        await asyncio.sleep(f.value)
        return await forward_file(message, cid)


async def send_url_logs(unzip_bot, c_id, doc_f, source, message):
    try:
        u_file_size = os.stat(doc_f).st_size
        if Config.TG_MAX_SIZE < int(u_file_size):
            await unzip_bot.send_message(chat_id=c_id, text=Messages.TOO_LARGE)
            return
        fname = os.path.basename(doc_f)
        await unzip_bot.send_document(
            chat_id=c_id,
            document=doc_f,
            caption=Messages.LOG_CAPTION.format(fname, source),
            disable_notification=True,
            progress=progress_urls,
            progress_args=(
                Messages.CHECK_MSG,
                message,
                time(),
            ),
        )
    except FloodWait as f:
        await asyncio.sleep(f.value)
        return send_url_logs(unzip_bot, c_id, doc_f, source, message)
    except FileNotFoundError:
        await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=Messages.ARCHIVE_GONE,
        )
    except BaseException:
        pass


async def merge_splitted_archives(user_id, path):
    cmd = f'cd "{path}" && cat * > MERGED_{user_id}.zip'
    await run_shell_cmds(cmd)


# Function to remove basic markdown characters from a string
async def rm_mark_chars(text: str):
    return re.sub("[*`_]", "", text)


# Function to answer queries
async def answer_query(
    query, message_text: str, answer_only: bool = False, unzip_client=None, buttons=None
):
    try:
        if answer_only:
            await query.answer(await rm_mark_chars(message_text), show_alert=True)
        else:
            await query.message.edit(message_text, reply_markup=buttons)
    except:
        try:
            if unzip_client:
                await unzip_client.send_message(
                    chat_id=query.message.chat.id,
                    text=message_text,
                    reply_markup=buttons,
                )
            else:
                await unzipperbot.send_message(
                    chat_id=query.message.chat.id,
                    text=message_text,
                    reply_markup=buttons,
                )
        except:
            pass
