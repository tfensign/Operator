import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Checklist } from '../types';

function Checklists() {
  const [checklists, setChecklists] = useState<Checklist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [selectedChecklist, setSelectedChecklist] = useState<Checklist | null>(null);
  const [newItemText, setNewItemText] = useState('');

  useEffect(() => {
    loadChecklists();
  }, []);

  const loadChecklists = async () => {
    try {
      setLoading(true);
      const response = await api.getChecklists();
      setChecklists(response.data);
    } catch (err: any) {
      setError('Failed to load checklists');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateChecklist = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    try {
      const response = await api.createChecklist(newTitle, newDescription);
      setChecklists([response.data, ...checklists]);
      setNewTitle('');
      setNewDescription('');
    } catch (err: any) {
      setError('Failed to create checklist');
    }
  };

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedChecklist || !newItemText.trim()) return;

    try {
      const response = await api.addChecklistItem(selectedChecklist.id, newItemText);
      const updated = {
        ...selectedChecklist,
        items: [...(selectedChecklist.items || []), response.data]
      };
      setSelectedChecklist(updated);
      setChecklists(checklists.map(c => c.id === updated.id ? updated : c));
      setNewItemText('');
    } catch (err: any) {
      setError('Failed to add item');
    }
  };

  const handleMarkItemComplete = async (itemId: number) => {
    if (!selectedChecklist) return;

    try {
      await api.markItemComplete(selectedChecklist.id, itemId);
      const updated = {
        ...selectedChecklist,
        items: selectedChecklist.items.map(item =>
          item.id === itemId ? { ...item, completed_at: new Date().toISOString() } : item
        )
      };
      setSelectedChecklist(updated);
      setChecklists(checklists.map(c => c.id === updated.id ? updated : c));
    } catch (err: any) {
      setError('Failed to complete item');
    }
  };

  if (loading) {
    return <div className="page-loading">Loading checklists...</div>;
  }

  return (
    <div className="checklists-page">
      <h1>Checklists</h1>

      {error && <div className="error-banner">{error}</div>}

      <div className="checklists-layout">
        <div className="checklist-list">
          <div className="create-checklist">
            <h3>Create New Checklist</h3>
            <form onSubmit={handleCreateChecklist}>
              <input
                type="text"
                placeholder="Checklist title"
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
              />
              <textarea
                placeholder="Description (optional)"
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                rows={2}
              />
              <button type="submit">Create</button>
            </form>
          </div>

          {checklists.length === 0 ? (
            <p className="empty-state">No checklists yet</p>
          ) : (
            <ul>
              {checklists.map((list) => (
                <li
                  key={list.id}
                  className={`checklist-item ${selectedChecklist?.id === list.id ? 'selected' : ''}`}
                  onClick={() => setSelectedChecklist(list)}
                >
                  <h4>{list.title}</h4>
                  <p className="item-count">
                    {list.items?.filter(i => i.completed_at).length || 0} / {list.items?.length || 0}
                  </p>
                  {list.description && <p className="description">{list.description}</p>}
                </li>
              ))}
            </ul>
          )}
        </div>

        {selectedChecklist && (
          <div className="checklist-detail">
            <div className="detail-header">
              <h2>{selectedChecklist.title}</h2>
              <button className="close-btn" onClick={() => setSelectedChecklist(null)}>✕</button>
            </div>

            {selectedChecklist.description && (
              <p className="description">{selectedChecklist.description}</p>
            )}

            <div className="add-item">
              <h4>Add Item</h4>
              <form onSubmit={handleAddItem}>
                <input
                  type="text"
                  placeholder="New item"
                  value={newItemText}
                  onChange={(e) => setNewItemText(e.target.value)}
                />
                <button type="submit">Add</button>
              </form>
            </div>

            <div className="items">
              {selectedChecklist.items?.length === 0 ? (
                <p className="empty-state">No items yet</p>
              ) : (
                <ul>
                  {selectedChecklist.items?.map((item) => (
                    <li key={item.id} className={item.completed_at ? 'completed' : ''}>
                      <input
                        type="checkbox"
                        checked={!!item.completed_at}
                        onChange={() => handleMarkItemComplete(item.id)}
                      />
                      <span>{item.text}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Checklists;
