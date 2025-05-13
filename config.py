import os
from dotenv import load_dotenv

# Load .env variables if running locally
load_dotenv()

class Config(object):
    try:
        APP_ID = int(os.environ.get("APP_ID", "20826111"))  # your API ID
    except ValueError:
        raise ValueError("❌ APP_ID must be a valid integer. Please check your environment variables.")

    API_HASH = os.environ.get("API_HASH", "7b6813d0d82891dd367b420b46133691")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7540535871:AAE6F0k7NBEn_m3s0wAEtT1HdmfqHvUI1ok")
    LOGS_CHANNEL = int(os.environ.get("LOGS_CHANNEL", "-1002688784997"))
    MONGODB_URL = os.environ.get(
        "MONGODB_URL",
        "mongodb+srv://nobodynote10:Nobody@cluster0.7fqavjv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    )
    MONGODB_DBNAME = os.environ.get("MONGODB_DBNAME", "UnzipperBot")
    BOT_OWNER = int(os.environ.get("BOT_OWNER", "8171174878"))

    # Constants
    DOWNLOAD_LOCATION = f"{os.path.dirname(__file__)}/Downloaded"
    THUMB_LOCATION = f"{os.path.dirname(__file__)}/Thumbnails"
    TG_MAX_SIZE = 2097152000
    MAX_MESSAGE_LENGTH = 4096
    CHUNK_SIZE = 1024 * 1024 * 10  # 10 MB
    BOT_THUMB = f"{os.path.dirname(__file__)}/bot_thumb.jpg"
    MAX_CONCURRENT_TASKS = 15
    MAX_TASK_DURATION_EXTRACT = 60 * 60  # 1 hour
    MAX_TASK_DURATION_MERGE = 120 * 60  # 2 hours

print("✅ Config Loaded Successfully!")
