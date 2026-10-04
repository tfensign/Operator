import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Integration } from '../types';

function Settings() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPlatform, setSelectedPlatform] = useState('');
  const [credentials, setCredentials] = useState<Record<string, string>>({});
  const [masterPassword, setMasterPassword] = useState('');
  const [setupLoading, setSetupLoading] = useState(false);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      setLoading(true);
      const response = await api.getIntegrations();
      setIntegrations(response.data);
    } catch (err: any) {
      setError('Failed to load integrations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const platformConfig: Record<string, { fields: string[] }> = {
    email: {
      fields: ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_password']
    },
    slack: {
      fields: ['bot_token']
    },
    sms: {
      fields: ['twilio_sid', 'twilio_token', 'from_phone']
    }
  };

  const handleSetupIntegration = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPlatform || !masterPassword) return;

    setSetupLoading(true);
    try {
      await api.setupIntegration(selectedPlatform, credentials, masterPassword);
      setCredentials({});
      setMasterPassword('');
      setSelectedPlatform('');
      loadIntegrations();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to setup integration');
    } finally {
      setSetupLoading(false);
    }
  };

  const handleDeleteIntegration = async (platform: string) => {
    if (!window.confirm(`Delete ${platform} integration?`)) return;

    try {
      await api.deleteIntegration(platform);
      setIntegrations(integrations.filter(i => i.platform !== platform));
    } catch (err: any) {
      setError('Failed to delete integration');
    }
  };

  if (loading) {
    return <div className="page-loading">Loading settings...</div>;
  }

  const selectedConfig = selectedPlatform ? platformConfig[selectedPlatform] : null;

  return (
    <div className="settings-page">
      <h1>Settings</h1>

      {error && <div className="error-banner">{error}</div>}

      <div className="settings-layout">
        <section className="settings-section">
          <h2>Connected Integrations</h2>
          {integrations.length === 0 ? (
            <p className="empty-state">No integrations set up yet</p>
          ) : (
            <ul className="integration-list">
              {integrations.map((integration) => (
                <li key={integration.id} className="integration-item">
                  <div className="integration-info">
                    <h4>{integration.platform.toUpperCase()}</h4>
                    <p className="status">Status: {integration.status}</p>
                    <p className="webhook">
                      Webhook: <code>{integration.webhook_url}</code>
                    </p>
                  </div>
                  <button
                    onClick={() => handleDeleteIntegration(integration.platform)}
                    className="delete-btn"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="settings-section">
          <h2>Add Integration</h2>
          <form onSubmit={handleSetupIntegration} className="setup-form">
            <div className="form-group">
              <label>Platform</label>
              <select
                value={selectedPlatform}
                onChange={(e) => {
                  setSelectedPlatform(e.target.value);
                  setCredentials({});
                }}
              >
                <option value="">Select a platform</option>
                <option value="email">Email (SMTP)</option>
                <option value="slack">Slack</option>
                <option value="sms">SMS (Twilio)</option>
              </select>
            </div>

            {selectedConfig && (
              <>
                {selectedConfig.fields.map((field) => (
                  <div key={field} className="form-group">
                    <label>{field.replace(/_/g, ' ').toUpperCase()}</label>
                    <input
                      type={field.includes('password') ? 'password' : 'text'}
                      placeholder={field}
                      value={credentials[field] || ''}
                      onChange={(e) => setCredentials({
                        ...credentials,
                        [field]: e.target.value
                      })}
                    />
                  </div>
                ))}
              </>
            )}

            <div className="form-group">
              <label>Master Password (to encrypt credentials)</label>
              <input
                type="password"
                placeholder="Master Password"
                value={masterPassword}
                onChange={(e) => setMasterPassword(e.target.value)}
              />
            </div>

            <button type="submit" disabled={setupLoading || !selectedPlatform || !masterPassword}>
              {setupLoading ? 'Setting up...' : 'Add Integration'}
            </button>
          </form>
        </section>

        <section className="settings-section">
          <h2>How to Configure Webhooks</h2>
          <div className="instructions">
            <h3>Email Setup (SendGrid, Mailgun, etc.)</h3>
            <ol>
              <li>Get your SMTP credentials from your email provider</li>
              <li>Enter SMTP host, port, username, and password above</li>
              <li>Save the webhook URL and configure forwarding to your provider</li>
            </ol>

            <h3>Slack Setup</h3>
            <ol>
              <li>Create a Slack app at api.slack.com</li>
              <li>Get your bot token</li>
              <li>Add the webhook URL to your Slack workspace settings</li>
            </ol>

            <h3>SMS Setup (Twilio)</h3>
            <ol>
              <li>Get your Twilio Account SID and Auth Token</li>
              <li>Configure webhook in Twilio dashboard</li>
              <li>Set your Twilio phone number as "from_phone"</li>
            </ol>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Settings;
