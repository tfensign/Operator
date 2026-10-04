# Operator - Development Guide

## Project Overview

Operator is a privacy-first desktop communication manager that consolidates messages from email, Slack, SMS, and other platforms into a single interface. All data stays on the user's device, encrypted with their master password.

## Architecture Decisions

### Backend
- **FastAPI** chosen for lightweight, async-capable REST API
- **SQLite** for local database (no server setup needed)
- **AES-256-GCM** for credential encryption (authenticated encryption)
- **PBKDF2** for key derivation from master password

### Frontend
- **React + TypeScript** for type-safe UI
- **Web app** (browser-based, no Electron)
- **Axios** for HTTP calls to backend
- **React Router** for navigation

### Security
- Credentials stored encrypted in SQLite
- Master password never stored plaintext
- Messages at rest are plaintext (MVP tradeoff - no server attack surface)
- E2E encryption deferred to Phase 2 (when multi-device sync added)

## Key Files

### Backend
- `app.py` - FastAPI app entry point, route registration
- `database.py` - SQLAlchemy models and database setup
- `crypto.py` - Encryption/decryption service
- `config.py` - Configuration and environment variables
- `routes/` - API route handlers
- `services/` - Business logic (message prioritization, sending, checklists)

### Frontend
- `src/App.tsx` - Root React component with routing
- `src/pages/` - Page components (Dashboard, Messages, Checklists, Settings)
- `src/services/api.ts` - HTTP client for backend API
- `src/types/index.ts` - TypeScript type definitions
- `public/index.html` - HTML entry point
- `package.json` - Dependencies and scripts

## Development Workflow

### Running Locally

**Option 1: One-Command Start**
```bash
cd /home/te23/workspace/Operator
./start.sh
```

**Option 2: Manual (Two Terminals)**

Terminal 1 - Backend:
```bash
cd backend
python -m uvicorn app:app --port 3001 --reload
```

Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

Then open `http://localhost:3000` in your browser.

### Database

- Location: `data/operator.db` (created automatically on first run)
- Schema initialized in `database.py` with SQLAlchemy
- Use `init_db()` in main script to create tables

### API Communication

Frontend uses `axios` to make HTTP calls to `http://localhost:3001`. All API calls go through the service layer in `src/services/api.ts`.

## Important Notes

### Encryption
- Credentials are encrypted with user's master password
- Each credential has its own IV (initialization vector) for GCM mode
- Never log or print encrypted values
- Decryption happens only in memory, in `sender_service.py`

### Message Prioritization
- Keyword-based scoring in `message_service.py`
- Urgency keywords (+2), all-caps subject (+1), VIP senders (+1)
- Priority capped at 5.0

### Webhook Receivers
- Generic webhook endpoints accept JSON payloads with `from_address`, `subject`, `body`
- Messages auto-prioritized on ingestion
- Action items extracted with regex patterns (TODO, Action, FYI)

### Sending Messages
- Requires approval from user before sending
- Backend decrypts stored credentials with master password
- Supports SMTP (email), Slack API, Twilio (SMS)
- Sent messages logged in `sent_messages` table

## Testing

### Manual Testing Checklist
- [ ] Setup master password on first run
- [ ] Unlock app with correct password (fails with wrong password)
- [ ] Create test webhook message via curl or Postman
- [ ] Verify message appears in dashboard with correct priority
- [ ] Create checklist from message
- [ ] Extract action items (TODO: item)
- [ ] Create draft message and approve it
- [ ] Verify sent message appears in history

### Webhook Testing
```bash
curl -X POST http://localhost:3001/webhook/email \
  -H "Content-Type: application/json" \
  -d '{
    "from_address": "boss@example.com",
    "subject": "URGENT: Action Required",
    "body": "TODO: Review the report\nTODO: Send feedback"
  }'
```

## Common Tasks

### Adding a New Message Platform
1. Add webhook receiver in `routes/webhooks.py`
2. Add credential fields for that platform in Settings UI
3. Add sending logic in `services/sender_service.py`
4. Update `platformConfig` in frontend Settings page

### Adding a New Feature
1. Design API endpoint in backend route
2. Add Pydantic model for request/response
3. Add corresponding axios call in `src/services/api.ts`
4. Add TypeScript type in `src/types/index.ts`
5. Build UI component/page to use it

### Database Schema Changes
1. Update model in `database.py`
2. Delete `data/operator.db` to force schema recreation (dev only)
3. Test with fresh DB initialization

## Performance Considerations

- Messages are prioritized on ingestion (not at query time)
- Full-text search uses LIKE queries (fine for local DB)
- No pagination yet (MVP), load all messages into memory
- Consider pagination if message count grows > 1000

## Known Limitations (MVP)

1. Single device only (multi-device sync in Phase 2)
2. No E2E encryption (messages stored plaintext locally)
3. No real-time sync (fetch data when viewing pages)
4. Limited platforms (email, Slack, SMS via webhooks)
5. No message body encryption (only credentials encrypted)
6. Simple priority algorithm (no ML/sentiment analysis)

## Future Improvements

- Multi-device sync with encrypted cloud backend
- Real-time message updates via WebSocket
- AI-powered action item extraction and summarization
- Direct API integrations (pull-based, not just webhooks)
- Message templates and scheduling
- Integration with calendar/task managers
- Dark mode UI
- Offline-first with eventual sync

## Troubleshooting

### Backend fails to start
- Check Python 3.8+ installed
- Check port 3001 not in use
- Install dependencies: `pip install -r backend/requirements.txt`

### Frontend fails to connect
- Ensure backend is running on port 3001
- Check `http://localhost:3001/health` in browser
- Check browser console for CORS errors

### Encryption errors
- Verify master password is correct
- Check that credentials were saved before trying to send
- Look at error in `sender_service.py` for decryption failures

### Database locked
- Ensure only one Python process accessing `data/operator.db`
- Kill any stuck processes: `lsof -i :3001` then `kill -9 <pid>`
