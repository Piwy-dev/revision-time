# 📚 Study Tracker

A minimalist web application to track daily study time with beautiful visualizations.

## Features

- **📚 Exam Sessions** - Create separate study contexts for different exams (e.g., Math Final, Python Midterm)
- **🔒 Data Isolation** - Each exam has its own study sessions and custom daily targets
- **📋 Sessions Manager** - View, edit, and delete all study sessions with inline editing
- **📊 Daily Study Dashboard** - Track total study time per day with visual charts
- **⏰ Session Logging** - Log study sessions with start/end times (auto-calculates duration)
- **📈 Hourly Distribution** - See when you study most during the day
- **🎯 Daily Targets** - Set and track study goals for each day of the week (per exam)
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

### Creating an Exam Session

1. Click **"+ New Exam"** button in the header
2. Fill in:
   - **Exam Name** (e.g., "Python Final", "Math Midterm")
   - **Description** (optional)
   - **Start & End Dates** (study period for this exam)
3. Click **"Create"** - your exam is now selected
4. Use the **"Exam Session"** dropdown to switch between exams

### Adding a Study Session

1. Make sure an exam is selected (shown in header)
2. Click **"+ Add Session"** button
3. Select the date (defaults to today)
4. Enter start time (e.g., 8:30)
5. Enter end time (e.g., 9:20)
6. Click **"Add Session"** - duration is auto-calculated

**Example**: 8:30 → 9:20 = 50 minutes

### Managing Sessions (View, Edit, Delete)

1. Click **"📋 Sessions"** button in the header
2. A table appears showing all sessions for the current period
3. **View**: See all sessions in date order
4. **Edit**: Click "Edit" on any row → modify dates/times → Click "Save"
5. **Delete**: Click "Delete" → Confirm → Session removed
6. **Duration**: Auto-calculates when you edit times
7. **Stats**: Total sessions and total study time shown at bottom

See [SESSIONS_MANAGEMENT.md](./SESSIONS_MANAGEMENT.md) for detailed guide.

### Viewing Statistics

- **Daily Chart**: Shows total study time per day + daily target line
- **Hourly Chart**: Shows how much you studied in each hour
- **Time Period Selector**: Switch between week/month/all-time views
- **Stats Panel**: Aggregate stats + editable daily targets
- **Exam Selector**: Switch between different exams

All statistics are per-exam and updated when you switch exams.

### Setting Daily Targets (Per Exam)

1. Scroll to **"Daily Targets"** section
2. Click ⚙️ icon next to any day
3. Enter target in minutes (e.g., 300 for 5 hours)
4. Click **"Save"**

Targets are stored per exam, per day of week. Each exam can have different targets!

### Switching Between Exams

Use the **"Exam Session"** dropdown to switch. All data, charts, and targets update for the new exam context.

## Project Structure

```
revision-time/
├── backend/
│   ├── main.py           # FastAPI app entry point
│   ├── database.py       # SQLAlchemy + SQLite setup (ExamSession, Session, Targets)
│   ├── models.py         # Pydantic schemas
│   ├── routes.py         # API endpoints (exam-scoped)
│   └── __init__.py
│
├── frontend/
│   ├── src/
│   │   ├── App.svelte           # Main component with exam context
│   │   ├── main.js              # Entry point
│   │   └── components/
│   │       ├── ExamSelector.svelte    # Create/manage exam sessions
│   │       ├── SessionForm.svelte     # Add study sessions
│   │       ├── DailyChart.svelte      # Daily stats chart
│   │       ├── HourlyChart.svelte     # Hourly distribution
│   │       └── Stats.svelte           # Stats panel + targets
│   ├── dist/             # Built files (generated)
│   ├── package.json
│   └── vite.config.js
│
├── pyproject.toml        # Python dependencies
├── study.db             # SQLite database (auto-created)
├── start.sh             # Startup script
├── README.md            # This file
├── EXAM_SESSIONS.md     # Exam sessions feature guide
└── QUICKSTART.md        # Quick start guide
```

## API Endpoints

### Exam Sessions
- `POST /api/exam-sessions` - Create a new exam session
- `GET /api/exam-sessions` - List all exam sessions
- `GET /api/exam-sessions/{id}` - Get exam session details
- `PUT /api/exam-sessions/{id}` - Update exam session
- `DELETE /api/exam-sessions/{id}` - Delete exam session

### Study Sessions (Exam-scoped)
- `POST /api/sessions` - Create a session (requires `exam_session_id`)
- `GET /api/sessions?exam_session_id={id}&start_date=...&end_date=...` - List sessions for exam
- `DELETE /api/sessions/{id}` - Delete a session

### Statistics (Exam-scoped)
- `GET /api/stats/daily?exam_session_id={id}&start_date=...&end_date=...` - Daily totals with targets
- `GET /api/stats/hourly?exam_session_id={id}&start_date=...&end_date=...` - Hourly distribution

### Daily Targets (Exam-scoped)
- `GET /api/exam-targets/{exam_id}` - Get all daily targets for exam
- `PUT /api/exam-targets/{exam_id}/{day}` - Update target for day (0=Mon, 6=Sun)
- `GET /api/target/{day}` - Get global daily target (legacy)
- `PUT /api/target/{day}` - Update global daily target (legacy)

## Database

Data is stored in `study.db` (SQLite):

- **exam_sessions**: Exam session contexts (name, description, dates, active status)
- **sessions**: Study sessions (date, start_time, end_time, duration_minutes, exam_session_id FK)
- **exam_daily_targets**: Per-exam daily targets (day_of_week, target_minutes, exam_session_id FK)
- **daily_targets**: Global daily targets (legacy, day_of_week, target_minutes)

No setup required - database is auto-created on first run with proper relationships.

### Data Isolation

Each exam session has:
- Isolated study sessions (linked via `exam_session_id` FK)
### Data Isolation

Each exam session has:
- Isolated study sessions (linked via `exam_session_id` FK)
- Isolated daily targets (per day of week, per exam)
- Separate statistics (daily/hourly charts computed per exam)

## Exam Sessions Feature

This application supports **multiple isolated exam sessions**, perfect for tracking studies for multiple exams simultaneously.

### Key Capabilities

- ✓ Create unlimited exam sessions with custom date ranges
- ✓ Each exam has isolated study data (no mixing)
- ✓ Set different daily targets for each exam
- ✓ Switch between exams with one click
- ✓ All charts/stats update per exam context
- ✓ Independent hourly patterns per exam

### Use Cases

- Studying for **multiple courses** simultaneously (Math, Python, History)
- **Certification exams** with separate prep periods
- **Summer courses** with overlapping schedules
- **Re-examination attempts** with separate tracking

**See [EXAM_SESSIONS.md](./EXAM_SESSIONS.md) for detailed usage guide.**

## Development

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
