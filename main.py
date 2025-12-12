from fastapi import FastAPI

app = FastAPI()


@app.get("/ping")
async def get_pong():
    return "pong"