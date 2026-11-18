import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const MAX_TITLE_LENGTH = 100;
const CATEGORIES = ['Hardware', 'Software', 'Network', 'Access', 'Other'];
const PRIORITIES = ['Low', 'Medium', 'High'];

export default function TicketModal({
  isOpen,
  onClose,
  onSubmit,
  initialData = null,
}) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Hardware');
  const [priority, setPriority] = useState('Medium');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title || '');
      setDescription(initialData.description || '');
      setCategory(initialData.category || 'Hardware');
      setPriority(initialData.priority || 'Medium');
    } else {
      setTitle('');
      setDescription('');
      setCategory('Hardware');
      setPriority('Medium');
    }
    setError('');
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    const cleanTitle = title.trim();
    const cleanDesc = description.trim();

    if (!cleanTitle) {
      setError('Title cannot be empty.');
      return;
    }
    if (cleanTitle.length > MAX_TITLE_LENGTH) {
      setError(`Title cannot exceed ${MAX_TITLE_LENGTH} characters.`);
      return;
    }
    if (!cleanDesc) {
      setError('Description cannot be empty.');
      return;
    }

    setError('');
    setIsSubmitting(true);
    try {
      await onSubmit({
        title: cleanTitle,
        description: cleanDesc,
        category,
        priority,
      });
      onClose();
    } catch (err) {
      setError(err.message || 'Operation failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isTitleAtLimit = title.length >= MAX_TITLE_LENGTH;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3 className="modal-title">
            {initialData ? 'Edit Support Ticket' : 'Raise New Support Ticket'}
          </h3>
          <button className="btn-close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-form">
            {error && <div className="error-msg">{error}</div>}

            <div className="form-group">
              <div className="form-label-row">
                <label className="form-label">Ticket Title *</label>
                <span
                  className={`char-counter ${
                    isTitleAtLimit ? 'limit' : title.length > 80 ? 'warning' : ''
                  }`}
                >
                  {title.length} / {MAX_TITLE_LENGTH}
                </span>
              </div>
              <input
                type="text"
                className="form-input"
                maxLength={MAX_TITLE_LENGTH}
                placeholder="Brief summary of the issue (required, max 100 characters)"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                autoFocus
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="form-group">
                <label className="form-label">Category</label>
                <select
                  className="form-select"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Priority</label>
                <select
                  className="form-select"
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                >
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Description *</label>
              <textarea
                className="form-textarea"
                rows="4"
                placeholder="Detailed description of the issue or request (required)..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting || !title.trim() || !description.trim()}
            >
              {isSubmitting
                ? 'Saving...'
                : initialData
                ? 'Save Changes'
                : 'Raise Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
