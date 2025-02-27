import os
import logging
import boto3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from dotenv import load_dotenv

load_dotenv()  # Memuat variabel dari file .env


# Konfigurasi logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Ambil environment variables
BOT_TOKEN = os.getenv("8110316274:AAHRiBJS5Tyh5PKeLRqhBkZF6vZtXAjzDIY")
SPACES_ACCESS_KEY = os.getenv("DO8018MFEJXTH43X96XR")
SPACES_SECRET_KEY = os.getenv("IxQxB8ouflMicot1DBSHSZ+phQvzXc/YNgSJshlhCpI")
SPACES_REGION = os.getenv("sgp1")
SPACES_BUCKET = os.getenv("disiniajalah")

# Konfigurasi S3 untuk DigitalOcean Spaces
s3_client = boto3.client(
    's3',
    region_name=SPACES_REGION,
    endpoint_url=f'https://{SPACES_REGION}.digitaloceanspaces.com',
    aws_access_key_id=SPACES_ACCESS_KEY,
    aws_secret_access_key=SPACES_SECRET_KEY
)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Send me a file, and I'll upload it to DigitalOcean Spaces!")

def upload_to_spaces(file_path: str, file_name: str) -> str:
    """Mengunggah file ke DigitalOcean Spaces di dalam folder 'TEST' dengan akses public."""
    object_name = f'TEST/{file_name}'
    
    s3_client.upload_file(
        file_path, SPACES_BUCKET, object_name,
        ExtraArgs={'ACL': 'public-read'}  # Buat file menjadi publik
    )
    return f'https://{SPACES_BUCKET}.{SPACES_REGION}.digitaloceanspaces.com/{object_name}'

def handle_document(update: Update, context: CallbackContext) -> None:
    """Menerima dan mengunggah dokumen ke DigitalOcean Spaces."""
    file = update.message.document
    file_name = file.file_name
    file_path = f'./{file_name}'
    
    file.download(file_path)
    url = upload_to_spaces(file_path, file_name)
    os.remove(file_path)
    
    update.message.reply_text(f'File uploaded: {url}')

def handle_photo(update: Update, context: CallbackContext) -> None:
    """Menerima dan mengunggah foto ke DigitalOcean Spaces."""
    photo = update.message.photo[-1]  # Ambil resolusi tertinggi
    file = photo.get_file()
    file_name = f'{photo.file_id}.jpg'
    file_path = f'./{file_name}'
    
    file.download(file_path)
    url = upload_to_spaces(file_path, file_name)
    os.remove(file_path)
    
    update.message.reply_text(f'Photo uploaded: {url}')

def main() -> None:
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_document))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
