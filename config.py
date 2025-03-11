import os
from dotenv import load_dotenv

# Load .env variables if running locally
load_dotenv()

class Config(object):
    try:
        APP_ID = int(os.environ.get("APP_ID", "24421857"))  # Default value to avoid NoneType error
    except ValueError:
        raise ValueError("❌ APP_ID must be a valid integer. Please check your environment variables.")

    API_HASH = os.environ.get("API_HASH", "a3813a12d8cdf6f9231791704fc1d04d")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7736597933:AAF-4yAhAmo3WFVmbovtXaBzDuaRqpXL6p8")
    LOGS_CHANNEL = int(os.environ.get("LOGS_CHANNEL", "-1002057446010"))
    MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb+srv://uhdprime:uhdprime@cluster0.ry5y4yk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    MONGODB_DBNAME = os.environ.get("MONGODB_DBNAME", "Unzipper_Bot")
    BOT_OWNER = int(os.environ.get("BOT_OWNER", "7388366658"))

    # Constants
    DOWNLOAD_LOCATION = f"{os.path.dirname(__file__)}/Downloaded"
    THUMB_LOCATION = f"{os.path.dirname(__file__)}/Thumbnails"
    TG_MAX_SIZE = 2097152000
    MAX_MESSAGE_LENGTH = 4096
    CHUNK_SIZE = 1024 * 1024 * 1  # 10 MB
    BOT_THUMB = f"{os.path.dirname(__file__)}/bot_thumb.jpg"
    MAX_CONCURRENT_TASKS = 15
    MAX_TASK_DURATION_EXTRACT = 60 * 60  # 1 hours
    MAX_TASK_DURATION_MERGE = 120 * 60  # 2 hours

print("✅ Config Loaded Successfully!")
