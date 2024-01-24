from dotenv import load_dotenv
import os

load_dotenv()

secret = os.environ.get("SECRET_AUTH")

smtp_username = os.environ.get("SMTP_USERNAME")
smtp_password = os.environ.get("SMTP_PASSWORD")
smtp_server = os.environ.get("SMTP_SERVER")