# 📚 Study Tracker

A minimalist web application to track daily study time with beautiful visualizations.

## Features

- **📊 Daily Study Dashboard** - Track total study time per day with visual charts
- **⏰ Session Logging** - Log study sessions with start/end times (auto-calculates duration)
- **📈 Hourly Distribution** - See when you study most during the day
- **🎯 Daily Targets** - Set and track study goals for each day of the week
- **📅 Time Periods** - View stats for this week, last 7 days, this month, or all-time
- **💾 Persistent Storage** - All data stored locally in SQLite database

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: Svelte + Chart.js
- **Package Manager**: pnpm + uv
- **No external dependencies** - Works offline, no cloud required

## Quick Start

### 1. Install Dependencies

```bash
# Python dependencies (backend)
uv sync

# JavaScript dependencies (frontend)
cd frontend && pnpm install && cd ..
```

### 2. Build Frontend

```bash
cd frontend
pnpm run build
cd ..
```

### 3. Start the Server

```bash
./start.sh
```

Or directly:

```bash
.venv/bin/python -m backend.main
```

Then open **http://localhost:8000** in your browser.

## How to Use

### Adding a Study Session

1. Click **"+ Add Session"** button
2. Select the date (defaults to today)
3. Enter start time (e.g., 8:30)
4. Enter end time (e.g., 9:20)
5. Click **"Add Session"** - duration is auto-calculated

**Example**: 8:30 → 9:20 = 50 minutes

### Viewing Statistics

- **Daily Chart**: Shows total study time per day + daily target line
- **Hourly Chart**: Shows how much you studied in each hour
- **Time Period Selector**: Switch between week/month/all-time views
- **Stats Panel**: Aggregate stats + editable daily targets

### Setting Daily Targets

1. Scroll to **"Daily Targets"** section
2. Click ⚙️ icon next to any day
3. Enter target in minutes (e.g., 300 for 5 hours)
4. Click **"Save"**

Targets are stored per day of week and used as benchmark in charts.

## Project Structure

```
revision-time/
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── database.py       # SQLAlchemy + SQLite setup
│   ├── models.py         # Pydantic schemas
│   ├── routes.py         # API endpoints
│   └── __init__.py
│
├── frontend/
│   ├── src/
│   │   ├── App.svelte    # Main component
│   │   ├── main.js       # Entry point
│   │   └── components/
│   │       ├── SessionForm.svelte
│   │       ├── DailyChart.svelte
│   │       ├── HourlyChart.svelte
│   │       └── Stats.svelte
│   ├── public/           # Static assets
│   ├── dist/             # Built files (generated)
│   ├── package.json
│   └── vite.config.js
│
├── pyproject.toml        # Python dependencies
├── study.db             # SQLite database (auto-created)
└── start.sh             # Startup script
```

## API Endpoints

### Sessions
- `POST /api/sessions` - Create a session
- `GET /api/sessions?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - List sessions
- `DELETE /api/sessions/{id}` - Delete a session

### Statistics
- `GET /api/stats/daily?start_date=...&end_date=...` - Daily totals with targets
- `GET /api/stats/hourly?start_date=...&end_date=...` - Hourly distribution

### Targets
- `GET /api/targets` - Get all daily targets
- `GET /api/target/{day}` - Get target for day (0=Mon, 6=Sun)
- `PUT /api/target/{day}` - Update target for day

## Database

Data is stored in `study.db` (SQLite):

- **sessions**: id, date, start_time, end_time, duration_minutes, created_at
- **daily_targets**: id, day_of_week (0-6), target_minutes

No setup required - database is auto-created on first run.

## Development

### Rebuild Frontend

```bash
cd frontend
pnpm run build
cd ..
```

Then restart the server.

### Development Server (with hot reload)

```bash
# Terminal 1: Backend
.venv/bin/python -m backend.main

# Terminal 2: Frontend dev server
cd frontend && pnpm run dev
```

Then visit **http://localhost:5173** (frontend dev server proxies `/api` to backend).

## Troubleshooting

### Port 8000 already in use
Kill the process:
```bash
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Frontend not showing
Make sure to rebuild:
```bash
cd frontend && pnpm run build
```

### Database corruption
Delete `study.db` and restart - a fresh database will be created.

## Notes

- All times are in 24-hour format (HH:MM)
- Daily targets are per day-of-week (applies to all Mondays, etc.)
- Data is never uploaded anywhere - it stays on your machine
- Works fully offline once built

## Future Ideas

- 📱 Mobile responsive design (already mostly there!)
- 🔔 Browser notifications for study reminders
- 📤 Export to CSV/PDF
- 🌙 Dark mode
- 📊 Weekly/monthly goal tracking
- ⏱️ Built-in Pomodoro timer

Enjoy tracking your study progress! 📚✨
