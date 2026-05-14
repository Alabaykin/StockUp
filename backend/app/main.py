from fastapi import FastAPI

app = FastAPI(title="StockUp API")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "StockUp Backend"}

# TODO: Добавить инициализацию Aiogram, подключение к БД (asyncpg) и Redis.
