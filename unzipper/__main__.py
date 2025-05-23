# Copyright (c) 2022 - 2024 EDM115
import os
import signal
import time
import asyncio

from keep_alive import keep_alive
from pyrogram import idle

from config import Config
from . import LOGGER, unzipperbot
from .helpers.start import (
    check_logs,
    dl_thumbs,
    set_boot_time,
    start_cron_jobs,
    removal,
)
from .modules.bot_data import Messages


def handler_stop_signals(signum, frame):
    LOGGER.info(
        "Received stop signal (%s, %s, %s). Exiting...",
        signal.Signals(signum).name,
        signum,
        frame,
    )
    asyncio.run(shutdown_bot())  # updated to call async function properly


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)


async def shutdown_bot():
    stoptime = time.strftime("%Y/%m/%d - %H:%M:%S")
    LOGGER.info(Messages.STOP_TXT.format(stoptime))
    try:
        await unzipperbot.send_message(
            chat_id=Config.LOGS_CHANNEL, text=Messages.STOP_TXT.format(stoptime)
        )
        with open("unzip-log.txt", "rb") as doc_f:
            try:
                await unzipperbot.send_document(
                    chat_id=Config.LOGS_CHANNEL,
                    document=doc_f,
                    file_name=doc_f.name,
                )
            except:
                pass
    except Exception as e:
        LOGGER.error("Error sending shutdown message : %s", e)
    finally:
        LOGGER.info("Bot stopped 😪")
        try:
            if unzipperbot.is_connected:
                await unzipperbot.stop()
        except:
            pass


if __name__ == "__main__":
    try:
        os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
        os.makedirs(Config.THUMB_LOCATION, exist_ok=True)
        LOGGER.info(Messages.STARTING_BOT)
        keep_alive()
        unzipperbot.start()
        starttime = time.strftime("%Y/%m/%d - %H:%M:%S")
        unzipperbot.send_message(
            chat_id=Config.LOGS_CHANNEL, text=Messages.START_TXT.format(starttime)
        )
        set_boot_time()
        dl_thumbs()
        LOGGER.info(Messages.CHECK_LOG)
        if check_logs():
            LOGGER.info(Messages.LOG_CHECKED)
            removal(True)
            start_cron_jobs()
            LOGGER.info(Messages.BOT_RUNNING)
            idle()
        else:
            try:
                unzipperbot.send_message(
                    chat_id=Config.BOT_OWNER,
                    text=Messages.WRONG_LOG.format(Config.LOGS_CHANNEL),
                )
            except:
                pass
            asyncio.run(shutdown_bot())
    except Exception as e:
        LOGGER.error("Error in main loop : %s", e)
    finally:
        asyncio.run(shutdown_bot())
