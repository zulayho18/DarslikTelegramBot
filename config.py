import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN= os.getenv('BOT_TOKEN','')
BASE_URL=os.getenv('BASE_URL','')