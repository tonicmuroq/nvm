# NVM Grudge Tracker

A simple web app to record things that made you angry.

## Backend

- Python Flask backend (see `backend/app.py`)
- Data stored in SQLite (`anger.db`)
- API endpoints:
  - `POST /events` with JSON `{person, content}` to record an event
  - `GET /events` list all events
  - `GET /summary?date=YYYY-MM-DD` daily total anger
  - `GET /scores` ranking of people with anger grades
  - `GET /filter?start=...&end=...&level=...` filtered events

Run backend:

```bash
pip install -r backend/requirements.txt
python backend/app.py
```

## Frontend

Open `frontend/index.html` in your browser. The page expects the backend
to be running on `http://127.0.0.1:5000`, so start the Flask server first.
The React UI allows adding events and viewing the list.
