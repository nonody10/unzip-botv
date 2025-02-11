import os
from dotenv import load_dotenv

# Load .env variables if running locally
load_dotenv()

class Config(object):
    try:
        APP_ID = int(os.environ.get("APP_ID", "25465082"))  # Default value to avoid NoneType error
    except ValueError:
        raise ValueError("❌ APP_ID must be a valid integer. Please check your environment variables.")

    API_HASH = os.environ.get("API_HASH", "4a6b5e40c8bc08c8af09add6cca23b18")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7821525708:AAFkeXtKLVd3v9K-ZUPx3K4cP6n5uuc7Ajk")
    LOGS_CHANNEL = int(os.environ.get("LOGS_CHANNEL", "-1001628560294"))
    MONGODB_URL = os.environ.get("MONGODB_URL", "mongodb+srv://uhdprime:uhdprime@cluster0.ry5y4yk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    MONGODB_DBNAME = os.environ.get("MONGODB_DBNAME", "Unzipper_Bot")
    BOT_OWNER = int(os.environ.get("BOT_OWNER", "6487118438"))

    # Constants
    DOWNLOAD_LOCATION = f"{os.path.dirname(__file__)}/Downloaded"
    THUMB_LOCATION = f"{os.path.dirname(__file__)}/Thumbnails"
    TG_MAX_SIZE = 2097152000
    MAX_MESSAGE_LENGTH = 4096
    CHUNK_SIZE = 1024 * 1024 * 10  # 10 MB
    MAX_CONCURRENT_TASKS = 75
    MAX_TASK_DURATION_EXTRACT = 120 * 60  # 2 hours
    MAX_TASK_DURATION_MERGE = 240 * 60  # 4 hours

print("✅ Config Loaded Successfully!")
