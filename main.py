from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.items_router import router as irouter
from app.routers.user_router import router as urouter
from app.routers.history_router import router as hrouter

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(urouter)
app.include_router(irouter)
app.include_router(hrouter)


@app.get('/')
def root():
    return dict(message=f"all works")
