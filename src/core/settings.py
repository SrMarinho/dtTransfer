import os
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", 50_000))
THREADS_NUM = int(os.getenv("THREADS_NUM", 4))
