from fastapi import FastAPI

from app.routers.items_router import router as irouter
from app.routers.user_router import router as urouter
from app.routers.history_router import router as hrouter

app = FastAPI()
app.include_router(urouter)
app.include_router(irouter)
app.include_router(hrouter)


@app.get('/')
def root():
    return dict(message=f"all works")
