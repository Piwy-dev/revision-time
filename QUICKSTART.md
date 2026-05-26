# 🚀 Quick Start Guide

## 5-Second Start

```bash
cd /Users/pierreyves/Programming/Sites/revision-time
./start.sh
# Opens on http://localhost:8000
```

## What You Get

✅ **Study Time Tracking** - Log sessions by start/end time  
✅ **Beautiful Charts** - Daily totals + hourly distribution  
✅ **Daily Targets** - Set goals, track progress  
✅ **Offline First** - All data stored locally in SQLite  
✅ **Responsive Design** - Works on desktop, tablet, mobile  

## Key Actions

| Action | How To |
|--------|--------|
| **Add Session** | Click "+ Add Session" → Set date, start time, end time → Click "Add" |
| **View Stats** | Scroll down to see charts and statistics |
| **Change Time Period** | Use dropdown at top ("This Week", "This Month", etc.) |
| **Update Daily Target** | Click ⚙️ icon next to day in "Daily Targets" section |

## Example Session

- 📅 Date: Today
- 🕘 Start: 09:00
- 🕙 End: 10:30
- ⏱️ Duration: 90 minutes ✓

## Folder Structure

```
revision-time/
├── backend/          (FastAPI server)
├── frontend/         (Svelte UI)
├── study.db         (Your data - sqlite)
├── start.sh         (Run this to start)
└── README.md        (Full documentation)
```

## Troubleshooting

**Frontend not showing?**
```bash
cd frontend && pnpm run build && cd ..
./start.sh
```

## API

All endpoints at `http://localhost:8000/api/`:

```
POST   /sessions                 (add session)
GET    /sessions?start_date=...  (list sessions)
GET    /stats/daily?start_date=... (daily chart data)
GET    /stats/hourly?start_date=... (hourly chart data)
GET    /targets                  (all daily targets)
PUT    /target/{day}             (update target)
```

---

**Happy studying!** 📚✨
