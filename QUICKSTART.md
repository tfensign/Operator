# Operator - Quick Start Guide

## One-Command Setup

### 1. Install Dependencies (first time only)

```bash
cd /home/te23/workspace/Operator

# Install backend
cd backend
pip install -r requirements.txt
cd ..

# Install frontend
cd frontend
npm install
cd ..
```

### 2. Run the App

```bash
cd /home/te23/workspace/Operator
./start.sh
```

That's it! The script will:
- Start the Python backend on port 3001
- Start the React frontend on port 3000
- Open it automatically (or manually visit `http://localhost:3000`)

## What You'll See

1. **Setup Screen** - Set your master password (min 8 characters)
2. **Dashboard** - Overview of messages, checklists, pending approvals
3. **Messages** - View all incoming messages, search, filter
4. **Checklists** - Create and manage task lists
5. **Settings** - Configure integrations and webhooks

## Testing the App

### Option 1: Via Web UI
- Just use the interface (setup password, click around)

### Option 2: Via Terminal (while app is running)

Open another terminal and run:

```bash
cd /home/te23/workspace/Operator
./test.sh
```

This sends test messages and exercises all API endpoints.

## Troubleshooting

**Backend won't start:**
```bash
# Check if port 3001 is in use
lsof -i :3001

# Kill it if needed
kill -9 <PID>
```

**Frontend won't start:**
```bash
# Make sure dependencies are installed
cd frontend
npm install
npm start
```

**Database locked:**
```bash
# Delete and recreate the database
rm -f backend/data/operator.db
```

## Manual Start (if you prefer)

**Terminal 1 - Backend:**
```bash
cd /home/te23/workspace/Operator/backend
python -m uvicorn app:app --port 3001
```

**Terminal 2 - Frontend:**
```bash
cd /home/te23/workspace/Operator/frontend
npm start
```

Then open `http://localhost:3000` in your browser.

## Stop the App

Press `Ctrl+C` in the terminal, or:

```bash
pkill -f "uvicorn"
pkill -f "react-scripts"
```

## Next Steps

- See `README.md` for full documentation
- See `CLAUDE.md` for development notes
- See `test.sh` for API testing examples
