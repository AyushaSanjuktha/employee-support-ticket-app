About: Small app where employees raise IT support tickets and support staff update the status.
Stack: FastAPI (Python), SQLite, React
Build / test:
- Backend run: `cd backend && .venv\Scripts\uvicorn app.main:app --reload --port 8000`
- Pytest: `cd backend && .venv\Scripts\pytest -v`
- Frontend run: `cd frontend && npm run dev`
- Frontend build: `cd frontend && npm run build`

Rules:
- Only support staff can change a ticket's status
- An employee sees only their own tickets; support staff see all
- A Closed ticket cannot be edited, but comments can still be added
- Title (up to 100 characters) and description cannot be empty

Style: Python type hints, small functions, clear names. One responsibility per file.
Data: use only the sample data. No real company data.
Do not touch: .env files, keys, .git folder
Done means: tests pass, no secrets in code, I have read every change
