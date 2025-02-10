# Copyright (c) 2022 - 2024 EDM115
import os
import signal
import time
import asyncio

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
            except Exception as e:
                LOGGER.error("Error sending document: %s", e)
    except Exception as e:
        LOGGER.error("Error sending shutdown message: %s", e)
    finally:
        LOGGER.info("Bot stopped 😪")
        await unzipperbot.stop(block=False)


def handler_stop_signals(signum, frame):
    LOGGER.info(
        "Received stop signal (%s, %s, %s). Exiting...",
        signal.Signals(signum).name,
        signum,
        frame,
    )
    asyncio.create_task(shutdown_bot())  # Run shutdown async function


signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)


async def main():
    try:
        os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
        os.makedirs(Config.THUMB_LOCATION, exist_ok=True)
        LOGGER.info(Messages.STARTING_BOT)
        await unzipperbot.start()
        starttime = time.strftime("%Y/%m/%d - %H:%M:%S")
        await unzipperbot.send_message(
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
            await idle()  # Keep the bot running
        else:
            try:
                await unzipperbot.send_message(
                    chat_id=Config.BOT_OWNER,
                    text=Messages.WRONG_LOG.format(Config.LOGS_CHANNEL),
                )
            except Exception as e:
                LOGGER.error("Error sending wrong log message: %s", e)
            await shutdown_bot()
    except Exception as e:
        LOGGER.error("Error in main loop: %s", e)
    finally:
        await shutdown_bot()


if __name__ == "__main__":
    asyncio.run(main())  # Run the bot using asyncio
