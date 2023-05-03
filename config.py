import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB():
    MONGO_URI = os.environ.get('MONGODB_URI')