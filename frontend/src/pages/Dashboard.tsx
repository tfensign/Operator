import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Message, PendingSend, Checklist } from '../types';

function Dashboard() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [pendingSends, setPendingSends] = useState<PendingSend[]>([]);
  const [checklists, setChecklists] = useState<Checklist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [messagesRes, pendingRes, checklistsRes] = await Promise.all([
        api.getMessages(),
        api.getPendingSends(),
        api.getChecklists()
      ]);

      setMessages(messagesRes.data.slice(0, 5));
      setPendingSends(pendingRes.data);
      setChecklists(checklistsRes.data.slice(0, 5));
    } catch (err: any) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="page-loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      {error && <div className="error-banner">{error}</div>}

      <div className="dashboard-grid">
        <section className="dashboard-section">
          <h2>Recent Messages ({messages.length})</h2>
          {messages.length === 0 ? (
            <p className="empty-state">No messages yet</p>
          ) : (
            <ul className="message-list">
              {messages.map((msg) => (
                <li key={msg.id} className={`message-item priority-${Math.floor(msg.priority)}`}>
                  <div className="message-header">
                    <span className="platform-badge">{msg.platform}</span>
                    <span className="priority">Priority: {msg.priority.toFixed(1)}</span>
                  </div>
                  <p className="message-from">{msg.from_address}</p>
                  {msg.subject && <p className="message-subject">{msg.subject}</p>}
                  <p className="message-body">{msg.body.substring(0, 100)}...</p>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="dashboard-section">
          <h2>Pending Approval ({pendingSends.length})</h2>
          {pendingSends.length === 0 ? (
            <p className="empty-state">No pending messages</p>
          ) : (
            <ul className="pending-list">
              {pendingSends.map((send) => (
                <li key={send.id} className="pending-item">
                  <div className="pending-header">
                    <span className="platform-badge">{send.platform}</span>
                    <span className="to-address">{send.to_address}</span>
                  </div>
                  {send.subject && <p className="subject">{send.subject}</p>}
                  <p className="body">{send.body.substring(0, 80)}...</p>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="dashboard-section">
          <h2>Active Checklists ({checklists.length})</h2>
          {checklists.length === 0 ? (
            <p className="empty-state">No checklists yet</p>
          ) : (
            <ul className="checklist-list">
              {checklists.map((list) => (
                <li key={list.id} className="checklist-item">
                  <h4>{list.title}</h4>
                  <p className="item-count">{list.items?.length || 0} items</p>
                  {list.items && list.items.length > 0 && (
                    <ul className="items-preview">
                      {list.items.slice(0, 3).map((item) => (
                        <li key={item.id} className={item.completed_at ? 'completed' : ''}>
                          {item.text}
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
