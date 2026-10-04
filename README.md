# Operator - Privacy-First Communication Manager

A desktop application for managing all your communications (email, Slack, SMS) in one place, with message prioritization, checklist management, and approval workflows. All data stays on your device.

## Features

- **Message Organization**: Receive messages from multiple platforms (email, Slack, SMS) via webhooks
- **Automatic Prioritization**: Keyword-based priority scoring (0-5) for urgent messages
- **Checklist Management**: Create checklists from messages with auto-extracted action items
- **Approval Workflow**: Review and approve messages before sending
- **End-to-End Security**: All API credentials encrypted with your master password
- **Privacy-First**: All data stored locally, no cloud uploads

## Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (local, encrypted credentials)
- **Security**: AES-256-GCM encryption for credentials, bcrypt for passwords

### Frontend
- **UI Framework**: React (TypeScript)
- **Desktop**: Electron
- **Communication**: HTTP to local backend

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm

### Installation & Run (One Command)

```bash
cd /home/te23/workspace/Operator

# Install dependencies (first time only)
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..

# Start the app
./start.sh
```

Then open **http://localhost:3000** in your browser.

### Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app:app --port 3001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

Open http://localhost:3000 in your browser.

## Project Structure

```
Operator/
├── backend/
│   ├── app.py                 # FastAPI app
│   ├── database.py            # SQLAlchemy models
│   ├── crypto.py              # Encryption service
│   ├── config.py              # Configuration
│   ├── models/                # Database models
│   ├── routes/                # API routes
│   ├── services/              # Business logic
│   └── requirements.txt
├── frontend/
│   ├── public/                # Static files
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   ├── types/             # TypeScript types
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── main.js                # Electron main process
│   ├── preload.js             # Electron preload
│   ├── package.json
│   └── tsconfig.json
├── .gitignore
└── README.md
```

## API Endpoints

### Authentication
- `POST /auth/setup` - Initialize with master password
- `POST /auth/unlock` - Verify master password

### Messages
- `GET /messages` - List messages
- `POST /messages/search` - Full-text search
- `POST /webhook/{platform}` - Receive webhook messages

### Checklists
- `GET /checklists` - List checklists
- `POST /checklists` - Create checklist
- `POST /checklists/from-message/{id}` - Create from message

### Send/Approve
- `POST /send/draft` - Create draft message
- `GET /send/pending` - List pending approvals
- `POST /send/{id}/approve` - Approve & send

### Integrations
- `GET /integrations` - List connected platforms
- `POST /integrations/{platform}` - Add integration

## Webhook Configuration

Each platform needs to send messages to the appropriate webhook URL:

### Email (SMTP)
- Configure your email provider to forward/push messages to: `http://localhost:3001/webhook/email`
- Store SMTP credentials in integrations

### Slack
- Create a Slack app with message permissions
- Configure webhook URL: `http://localhost:3001/webhook/slack`
- Store bot token in integrations

### SMS (Twilio)
- Configure Twilio webhook: `http://localhost:3001/webhook/sms`
- Store Twilio credentials in integrations

## Security Model

1. **Master Password**: User sets on first run, used to encrypt API credentials
2. **Credential Encryption**: AES-256-GCM encryption with PBKDF2 key derivation
3. **Local Storage**: All data stays on device in SQLite database
4. **No Server**: No cloud syncing or external servers in MVP

## Development Notes

- Backend runs on port 3001
- Frontend runs on port 3000 (dev), embedded in Electron
- Database file: `data/operator.db` (local to user's device)
- All API calls require authentication (unlock with master password)

## Future Enhancements (Phase 2)

- Multi-device sync (with client-side encryption)
- AI-powered checklist extraction
- Advanced message prioritization
- Direct integrations (pull-based from APIs)
- Message templates and scheduling
- Dark mode

## License

Private project
