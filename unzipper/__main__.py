# Copyright (c) 2022 - 2024 EDM115
import os
import signal
import time
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
    """Handle stop signals and initiate shutdown."""
    LOGGER.info(
        "Received stop signal (%s, %s, %s). Exiting...",
        signal.Signals(signum).name,
        signum,
        frame,
    )
    shutdown_bot()


def shutdown_bot():
    """Shutdown the bot gracefully."""
    stoptime = time.strftime("%Y/%m/%d - %H:%M:%S")
    LOGGER.info(Messages.STOP_TXT.format(stoptime))
    try:
        # Send shutdown message to logs channel
        unzipperbot.send_message(
            chat_id=Config.LOGS_CHANNEL, text=Messages.STOP_TXT.format(stoptime)
        )
        # Send log file to logs channel
        with open("unzip-log.txt", "rb") as doc_f:
            try:
                unzipperbot.send_document(
                    chat_id=Config.LOGS_CHANNEL,
                    document=doc_f,
                    file_name=doc_f.name,
                )
            except Exception as e:
                LOGGER.error("Error sending log file: %s", e)
    except Exception as e:
        LOGGER.error("Error sending shutdown message: %s", e)
    finally:
        LOGGER.info("Bot stopped 😪")
        unzipperbot.stop(block=False)


def initialize_directories():
    """Initialize necessary directories."""
    os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
    os.makedirs(Config.THUMB_LOCATION, exist_ok=True)


def start_bot():
    """Start the bot and perform initial checks."""
    LOGGER.info(Messages.STARTING_BOT)
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
        except Exception as e:
            LOGGER.error("Error notifying bot owner: %s", e)
        shutdown_bot()


def main():
    """Main function to run the bot."""
    try:
        initialize_directories()
        start_bot()
    except Exception as e:
        LOGGER.error("Error in main loop: %s", e)
    finally:
        shutdown_bot()


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)
    main()
