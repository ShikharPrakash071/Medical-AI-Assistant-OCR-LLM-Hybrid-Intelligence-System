from fastapi import FastAPI
from backend.routes.chat import router as chat_router
from backend.routes.upload import router as upload_router
app = FastAPI()

# chat route connect
app.include_router(chat_router)
app.include_router(upload_router)

@app.get("/")
def home():
    return {"message": "Medical AI running 🚀"}