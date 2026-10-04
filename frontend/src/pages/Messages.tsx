import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Message } from '../types';

function Messages() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [platformFilter, setPlatformFilter] = useState('');
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);

  useEffect(() => {
    loadMessages();
  }, [platformFilter]);

  const loadMessages = async () => {
    try {
      setLoading(true);
      const response = await api.getMessages(platformFilter || undefined);
      setMessages(response.data);
    } catch (err: any) {
      setError('Failed to load messages');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadMessages();
      return;
    }

    try {
      const response = await api.searchMessages(searchQuery);
      setMessages(response.data);
    } catch (err: any) {
      setError('Search failed');
    }
  };

  const handleMarkRead = async (messageId: number) => {
    try {
      await api.markMessageRead(messageId);
      setMessages(messages.map(m =>
        m.id === messageId ? { ...m, read_at: new Date().toISOString() } : m
      ));
    } catch (err) {
      setError('Failed to mark message as read');
    }
  };

  const handleDelete = async (messageId: number) => {
    try {
      await api.deleteMessage(messageId);
      setMessages(messages.filter(m => m.id !== messageId));
    } catch (err) {
      setError('Failed to delete message');
    }
  };

  if (loading) {
    return <div className="page-loading">Loading messages...</div>;
  }

  return (
    <div className="messages-page">
      <h1>Messages</h1>

      {error && <div className="error-banner">{error}</div>}

      <div className="messages-controls">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search messages..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit">Search</button>
        </form>

        <select value={platformFilter} onChange={(e) => setPlatformFilter(e.target.value)}>
          <option value="">All Platforms</option>
          <option value="email">Email</option>
          <option value="slack">Slack</option>
          <option value="sms">SMS</option>
        </select>
      </div>

      <div className="messages-layout">
        <div className="message-list">
          {messages.length === 0 ? (
            <p className="empty-state">No messages found</p>
          ) : (
            <ul>
              {messages.map((msg) => (
                <li
                  key={msg.id}
                  className={`message-item ${msg.read_at ? 'read' : 'unread'}`}
                  onClick={() => setSelectedMessage(msg)}
                >
                  <div className="message-summary">
                    <span className="platform">{msg.platform}</span>
                    <span className="priority" title={`Priority: ${msg.priority}`}>
                      {'★'.repeat(Math.ceil(msg.priority))}
                    </span>
                  </div>
                  <p className="from">{msg.from_address}</p>
                  {msg.subject && <p className="subject">{msg.subject}</p>}
                  <p className="preview">{msg.body.substring(0, 80)}...</p>
                  <span className="date">{new Date(msg.created_at).toLocaleDateString()}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {selectedMessage && (
          <div className="message-detail">
            <div className="detail-header">
              <h2>{selectedMessage.subject || '(No subject)'}</h2>
              <button className="close-btn" onClick={() => setSelectedMessage(null)}>✕</button>
            </div>

            <div className="detail-meta">
              <p><strong>From:</strong> {selectedMessage.from_address}</p>
              <p><strong>Platform:</strong> {selectedMessage.platform}</p>
              <p><strong>Priority:</strong> {selectedMessage.priority.toFixed(1)}</p>
              <p><strong>Date:</strong> {new Date(selectedMessage.created_at).toLocaleString()}</p>
            </div>

            <div className="detail-body">
              {selectedMessage.body}
            </div>

            <div className="detail-actions">
              {!selectedMessage.read_at && (
                <button onClick={() => handleMarkRead(selectedMessage.id)}>Mark as Read</button>
              )}
              <button onClick={() => handleDelete(selectedMessage.id)} className="delete-btn">
                Delete
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Messages;
