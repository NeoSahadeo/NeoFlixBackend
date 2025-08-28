from fastapi import FastAPI
from src.models import create_tables
from src.routes import access_router, manageprofiles_router, watchlist_router, watchhistory_router

app = FastAPI()

app.include_router(access_router)
app.include_router(manageprofiles_router)
app.include_router(watchlist_router)
app.include_router(watchhistory_router)

create_tables()
# config = read_config()
# if not config:
#     return
# file_path = Path(config.get("database_location"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
