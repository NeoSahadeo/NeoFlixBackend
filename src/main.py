from fastapi import FastAPI
from src.models import create_tables
from src.routes import router

app = FastAPI()
app.include_router(router)

create_tables()
# config = read_config()
# if not config:
#     return
# file_path = Path(config.get("database_location"))
