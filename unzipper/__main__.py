# Copyright (c) 2022 - 2024 EDM115
import os
import signal
import time
import asyncio

from pyrogram import idle
from pyrogram.errors import FloodWait

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


# Signal handler for graceful shutdown
def handler_stop_signals(signum, frame):
    LOGGER.info(
        "Received stop signal (%s, %s, %s). Exiting...",
        signal.Signals(signum).name,
        signum,
        frame,
    )
    asyncio.run(shutdown_bot())


# Register signal handlers
signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)


# Function to handle flood wait errors
async def handle_flood_wait(error):
    wait_time = error.x
    LOGGER.warning(f"Flood wait triggered. Sleeping for {wait_time} seconds.")
    await asyncio.sleep(wait_time)
    return True


# Function to shut down the bot gracefully
async def shutdown_bot():
    stoptime = time.strftime("%Y/%m/%d - %H:%M:%S")
    LOGGER.info(Messages.STOP_TXT.format(stoptime))
    try:
        if await unzipperbot.is_connected():
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
                    LOGGER.error(f"Error sending log file: {e}")
    except Exception as e:
        LOGGER.error(f"Error sending shutdown message: {e}")
    finally:
        if await unzipperbot.is_connected():
            await unzipperbot.stop()
        LOGGER.info("Bot stopped 😪")


# Main function to start the bot
async def main():
    try:
        # Create necessary directories
        os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
        os.makedirs(Config.THUMB_LOCATION, exist_ok=True)

        LOGGER.info(Messages.STARTING_BOT)
        await unzipperbot.start()

        # Send startup message to logs channel
        starttime = time.strftime("%Y/%m/%d - %H:%M:%S")
        try:
            await unzipperbot.send_message(
                chat_id=Config.LOGS_CHANNEL, text=Messages.START_TXT.format(starttime)
            )
        except FloodWait as e:
            await handle_flood_wait(e)
            await unzipperbot.send_message(
                chat_id=Config.LOGS_CHANNEL, text=Messages.START_TXT.format(starttime)
            )

        # Initialize bot resources
        set_boot_time()
        dl_thumbs()

        # Check logs and start cron jobs
        LOGGER.info(Messages.CHECK_LOG)
        if check_logs():
            LOGGER.info(Messages.LOG_CHECKED)
            removal(True)
            start_cron_jobs()
            LOGGER.info(Messages.BOT_RUNNING)
            await idle()
        else:
            # Notify bot owner if logs are invalid
            try:
                await unzipperbot.send_message(
                    chat_id=Config.BOT_OWNER,
                    text=Messages.WRONG_LOG.format(Config.LOGS_CHANNEL),
                )
            except Exception as e:
                LOGGER.error(f"Error notifying bot owner: {e}")
            await shutdown_bot()

    except FloodWait as e:
        await handle_flood_wait(e)
        await main()  # Retry after the wait

    except Exception as e:
        LOGGER.error(f"Error in main loop: {e}")
    finally:
        await shutdown_bot()


# Entry point
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped manually.")
    except Exception as e:
        LOGGER.error(f"Unexpected error: {e}")
