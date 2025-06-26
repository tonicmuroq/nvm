# NVM Grudge Tracker

A simple web app to record things that made you angry.

## How to Run

This project uses `uv` for Python package management.

### Backend

1.  **Install `uv`:**
    If you don't have it, install `uv` by running this command:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Sync Dependencies & Run Server:**
    Navigate to the `backend` directory, sync the dependencies, and then run the Flask server. `uv run` handles the virtual environment automatically.
    ```bash
    cd backend
    uv sync
    uv run flask run
    ```
    The backend will be running at `http://127.0.0.1:5000`.

### Frontend

To run the frontend, simply open the `frontend/index.html` file in your web browser.

## Backend Details

- Python Flask backend (see `backend/app.py`)
- Data stored in SQLite (`anger.db`)
- API endpoints:
  - `POST /events` with JSON `{person, content}` to record an event
  - `GET /events` list all events
  - `GET /summary?date=YYYY-MM-DD` daily total anger
  - `GET /scores` ranking of people with anger grades
  - `GET /filter?start=...&end=...&level=...` filtered events

## Cloudflare Worker Deployment

The `worker` folder contains a TypeScript backend. During the build step the
frontend `index.html` file is copied into `worker/dist/site` so the Worker can
serve it. Visiting the Worker URL loads `index.html` from that folder. The
Worker also uses a D1 database for storage.

1. Build the worker script and copy the frontend:
   ```bash
   cd worker
   npm run build
   ```
2. Deploy using Wrangler:
   ```bash
   wrangler deploy
   ```
   Configure your D1 database binding in `wrangler.toml` before deploying.
