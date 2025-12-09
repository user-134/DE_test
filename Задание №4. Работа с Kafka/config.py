from dotenv import load_dotenv
import os

load_dotenv()

PG_USER = os.getenv("PG_USER")
PG_PASS = os.getenv("PG_PASS")
PG_DB   = os.getenv("PG_DB")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")

CH_HOST = os.getenv("CH_HOST")
CH_PORT = os.getenv("CH_PORT")
CH_USER = os.getenv("CH_USER")
CH_PASS = os.getenv("CH_PASS")

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
