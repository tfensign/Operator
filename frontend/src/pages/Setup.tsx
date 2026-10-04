import React, { useState } from 'react';
import { api } from '../services/api';

function Setup({ onSetup }: { onSetup: () => void }) {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const passwordsMatch = password && confirmPassword && password === confirmPassword;
  const passwordsVisible = password || confirmPassword;

  const handleSetup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      await api.setupMasterPassword(password);
      onSetup();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Setup failed';
      console.error('Setup error:', err);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="setup-screen">
      <div className="setup-container">
        <h1>Welcome to Operator</h1>
        <p>Set up your master password to get started</p>
        <p className="info">This password encrypts all your API credentials and other sensitive data.</p>

        <form onSubmit={handleSetup}>
          <div className="form-group">
            <label>Master Password</label>
            <input
              type="password"
              placeholder="Enter password (min 8 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              placeholder="Confirm password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
            />
            {passwordsVisible && (
              <p className={passwordsMatch ? 'success' : 'error'}>
                {passwordsMatch ? '✓ Passwords match' : '✗ Passwords do not match'}
              </p>
            )}
          </div>

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading || !password || !confirmPassword}>
            {loading ? 'Setting up...' : 'Set Up Operator'}
          </button>
        </form>

        <div className="setup-info">
          <h3>About Operator</h3>
          <ul>
            <li>All data is stored locally on your device</li>
            <li>API credentials are encrypted with your master password</li>
            <li>No data is sent to any server</li>
            <li>You maintain complete control and privacy</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Setup;
