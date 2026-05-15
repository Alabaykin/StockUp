# StockUp 🛒 — Family Shopping Assistant

StockUp is a modern application (Telegram Web App) for managing joint family purchases. It helps track groceries inventory, automatically assigns icons (emojis) to products, and notifies family members when something runs out.

## 🚀 Quick Start

### 1. Environment Setup
Create a `.env` file in the root of the project (based on the example):
```env
BOT_TOKEN=your_telegram_bot_token
WEBAPP_URL=https://your-ngrok-url.ngrok-free.app/ # URL to open the Web App in Telegram
DATABASE_URL=postgresql+asyncpg://stockup_user:stockup_password@db:5432/stockup_db
REDIS_URL=redis://redis:6379/0
```

### 2. Run with Docker
```bash
docker-compose up --build -d
```
The application will be available at: [http://localhost:8000](http://localhost:8000)

## 🏗 Architecture

The project is built on a modular architecture using a message broker:

1.  **Backend (Python/FastAPI)**:
    *   Main API for the frontend.
    *   Telegram Integration (Aiogram) to launch the Web App.
    *   **NLP Service**: Automatic lemmatization of names and emoji assignment (uses `nltk` for English and `pymorphy3` for Russian).
    *   Publishes events (notifications) to Redis.
2.  **Notifier (Go)**:
    *   A lightweight worker that listens to the `notifications` channel in Redis.
    *   Sends real notifications to Telegram via the Bot API.
3.  **Frontend (JS/CSS SPA)**:
    *   Native design in Telegram style (Dark Mode, CSS theme variables).
    *   Works as a Single Page Application without heavy frameworks.
4.  **Database (PostgreSQL)**:
    *   Storage for users, families, products, and categories.
    *   Migrations are managed via Alembic.

## ✨ Key Features

*   **Multilingual Support**: Supports EN/RU at the NLP and interface level.
*   **Auto-Emoji**: Type "Milk" or "Молоко" — the system will automatically assign 🥛.
*   **Subscriptions (Alerts)**: Tap 🔔 on a product, and the bot will message you personally when it runs out.
*   **Shopping Request**: Tap 🛒 to send a notification to the whole family: "We need to buy this!".
*   **Categories**: Group products for easy search.

## 🛠 To-Do (Backlog)

1.  **UI Grouping**: Currently, products in the list are shown in a single row. Visual separation by categories needs to be added in `renderProducts()`.
2.  **Delete Categories**: The API for deletion exists, but there is no category deletion button in the interface yet.
3.  **Search and Filtering**: Add a search bar to search products by name.
4.  **Real Deployment**: Configure SSL and a stable domain for the Web App (currently, ngrok is required for testing in Telegram).
5.  **"Go Shopping" Logic**: A shopping list that can be "checked off" as the cart fills up.

## 👨‍💻 For Developers

*   **Migrations**: `docker-compose exec backend alembic upgrade head`
*   **Worker Logs**: `docker-compose logs -f notifier`
*   **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
