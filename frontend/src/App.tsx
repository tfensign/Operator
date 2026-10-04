import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { api } from './services/api';
import './App.css';

// Pages
import Dashboard from './pages/Dashboard';
import Messages from './pages/Messages';
import Checklists from './pages/Checklists';
import Settings from './pages/Settings';
import Setup from './pages/Setup';

function App() {
  const [initialized, setInitialized] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    checkInitialization();
  }, []);

  const checkInitialization = async () => {
    try {
      const response = await api.isInitialized();
      setInitialized(response.data.initialized);
    } catch (err) {
      console.error('Error checking initialization:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="app-loading">Initializing Operator...</div>;
  }

  if (!initialized) {
    return <Setup onSetup={() => setInitialized(true)} />;
  }

  return (
    <BrowserRouter>
      <div className="app">
        <nav className="app-nav">
          <div className="nav-header">
            <h1>Operator</h1>
          </div>
          <ul className="nav-links">
            <li><a href="/">Dashboard</a></li>
            <li><a href="/messages">Messages</a></li>
            <li><a href="/checklists">Checklists</a></li>
            <li><a href="/settings">Settings</a></li>
          </ul>
        </nav>

        <main className="app-main">
          {error && <div className="error-banner">{error}</div>}
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/messages" element={<Messages />} />
            <Route path="/checklists" element={<Checklists />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

function Unlock({ onUnlock }: { onUnlock: () => void }) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUnlock = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await api.unlockApp(password);
      onUnlock();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="unlock-screen">
      <div className="unlock-container">
        <h1>Operator</h1>
        <p>Enter your master password</p>
        <form onSubmit={handleUnlock}>
          <input
            type="password"
            placeholder="Master Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />
          {error && <p className="error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? 'Unlocking...' : 'Unlock'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
