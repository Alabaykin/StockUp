# Handover Document for AI Agent / Developer

## Project Context
**StockUp** is a Telegram Web App (TMA) for family inventory management.
- **Backend**: Python 3.11 + FastAPI + SQLAlchemy (Async) + Alembic.
- **Frontend**: Vanilla JS + CSS (SPA style).
- **Messaging**: Redis (Pub/Sub) for decoupled notifications.
- **Worker**: Go (Golang) service for sending Telegram messages.

## Technical Nuances
1.  **Auth**: The `get_current_user` dependency in `backend/app/api/auth.py` handles Telegram `initData` validation. For local testing without Telegram, it has a fallback to `dev_mode` (hardcoded user ID).
2.  **NLP**: `backend/app/services/nlp.py` is the core of "smart" features. It uses `nltk` for English and `pymorphy3` for Russian. It normalizes names to lemmas for emoji matching.
3.  **Notifications**:
    - Triggered in `backend/app/api/routes/products.py` when quantity hits 0 or via `/request` endpoint.
    - Payload is sent to Redis `notifications` channel.
    - Go Notifier (`notifier/main.go`) consumes it and calls Telegram Bot API.
4.  **Database**: PostgreSQL. If you change models, run `alembic revision --autogenerate` and `alembic upgrade head`.

## How to Test Telegram Integration
1.  Set `BOT_TOKEN` and `WEBAPP_URL` (HTTPS!) in `.env`.
2.  Users MUST send `/start` to the bot first.
3.  Open the Web App, subscribe to a product (bell icon), and set its quantity to 0.
4.  Watch the `notifier` logs: `docker-compose logs -f notifier`.

## Key Files
- `backend/app/main.py`: Main entry point & Lifespan (Starts Bot + Redis).
- `backend/app/db/models.py`: Database schema.
- `frontend/app.js`: Frontend state management and API calls.
- `notifier/main.go`: The Go worker.

## Next Tasks (Priority)
1.  **UI Product Grouping**: Update `renderProducts` in `app.js` to group items by `category_id`.
2.  **Category Management UI**: Add a way to edit/delete categories in the settings or a separate view.
3.  **Empty States**: Add nice illustrations/messages when there are no products or categories.
4.  **Unit Tests**: The project currently lacks automated tests.

Good luck! 🚀
