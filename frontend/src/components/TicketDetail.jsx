import React, { useState } from 'react';
import {
  Lock,
  Edit2,
  Send,
  MessageSquare,
  Clock,
  User as UserIcon,
  Tag,
} from 'lucide-react';

export default function TicketDetail({
  ticket,
  currentUser,
  onStatusChange,
  onOpenEditModal,
  onAddComment,
}) {
  const [commentText, setCommentText] = useState('');
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);
  const [commentError, setCommentError] = useState('');

  if (!ticket) {
    return (
      <div className="card">
        <div className="empty-state">
          <p>Select a ticket to view details.</p>
        </div>
      </div>
    );
  }

  const isClosed = ticket.status === 'Closed';
  const isSupport = currentUser?.role === 'SUPPORT';
  const isOwner = ticket.owner_id === currentUser?.id;
  // Rule: Only the employee who created the ticket can edit its details while it is not Closed
  const canEdit = !isClosed && currentUser?.role === 'EMPLOYEE' && isOwner;

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) {
      setCommentError('Comment cannot be empty.');
      return;
    }
    setCommentError('');
    setIsSubmittingComment(true);
    try {
      await onAddComment(ticket.id, commentText.trim());
      setCommentText('');
    } catch (err) {
      setCommentError(err.message || 'Failed to post comment.');
    } finally {
      setIsSubmittingComment(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'Open':
        return 'badge-status-open';
      case 'In Progress':
        return 'badge-status-in_progress';
      case 'Resolved':
        return 'badge-status-resolved';
      case 'Closed':
        return 'badge-status-closed';
      default:
        return 'badge-status-open';
    }
  };

  const getCategoryBadgeClass = (category) => {
    switch (category) {
      case 'Hardware':
        return 'badge-category-hardware';
      case 'Software':
        return 'badge-category-software';
      case 'Network':
        return 'badge-category-network';
      case 'Access':
        return 'badge-category-access';
      default:
        return 'badge-category-other';
    }
  };

  const getPriorityBadgeClass = (priority) => {
    switch (priority) {
      case 'Low':
        return 'badge-priority-low';
      case 'Medium':
        return 'badge-priority-medium';
      case 'High':
        return 'badge-priority-high';
      default:
        return 'badge-priority-medium';
    }
  };

  return (
    <div className="detail-container">
      {/* Main Ticket Card */}
      <div className="card">
        <div className="detail-header">
          <div className="detail-top-bar">
            <div style={{ display: 'flex', gap: '0.45rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <span className={`badge ${getStatusBadgeClass(ticket.status)}`}>
                {ticket.status}
              </span>
              <span className={`badge ${getCategoryBadgeClass(ticket.category)}`}>
                {ticket.category}
              </span>
              <span className={`badge ${getPriorityBadgeClass(ticket.priority)}`}>
                {ticket.priority} Priority
              </span>
            </div>

            {canEdit && (
              <button
                className="btn-secondary"
                onClick={() => onOpenEditModal(ticket)}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
              >
                <Edit2 size={14} />
                Edit Ticket
              </button>
            )}
          </div>

          <h2 className="detail-title">
            #{ticket.id} {ticket.title}
          </h2>

          <div className="detail-info-row">
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <UserIcon size={14} /> Created by: <strong>{ticket.owner ? ticket.owner.name : `User #${ticket.owner_id}`}</strong>
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Clock size={14} /> Created: {new Date(ticket.created_at).toLocaleString()}
            </span>
            {ticket.updated_at && ticket.updated_at !== ticket.created_at && (
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Clock size={14} /> Last updated: {new Date(ticket.updated_at).toLocaleString()}
              </span>
            )}
          </div>
        </div>

        <div className="detail-body">
          {/* Closed Alert Banner */}
          {isClosed && (
            <div className="closed-banner">
              <Lock size={18} color="#475569" />
              <div>
                <strong>Closed Ticket:</strong> This ticket is finalized. It cannot be reopened or edited, but new comments can still be added.
              </div>
            </div>
          )}

          {/* Support Staff Status Changer */}
          {isSupport && (
            <div className="status-changer-box">
              <span className="status-changer-label">
                Support Action: Change Ticket Status
              </span>
              {isClosed ? (
                <span style={{ fontSize: '0.825rem', color: '#64748b', fontWeight: 600 }}>
                  Locked (Closed tickets cannot be reopened)
                </span>
              ) : (
                <select
                  className="status-select"
                  value={ticket.status}
                  onChange={(e) => onStatusChange(ticket.id, e.target.value)}
                >
                  <option value="Open">Open</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Resolved">Resolved</option>
                  <option value="Closed">Closed</option>
                </select>
              )}
            </div>
          )}

          <h3 style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '0.5rem', fontWeight: 600 }}>
            Description
          </h3>
          <div className="detail-description-box">{ticket.description}</div>
        </div>
      </div>

      {/* Comments Section */}
      <div className="card comments-card">
        <h3 className="comments-title">
          <MessageSquare size={18} />
          Comments & Discussion ({ticket.comments?.length || 0})
        </h3>

        {/* Existing Comments */}
        <div className="comment-list">
          {(!ticket.comments || ticket.comments.length === 0) ? (
            <p style={{ color: '#64748b', fontSize: '0.85rem' }}>No comments yet.</p>
          ) : (
            ticket.comments.map((c) => (
              <div key={c.id} className="comment-item">
                <div className="comment-header">
                  <span className="comment-author">
                    {c.author?.name || `User #${c.author_id}`}
                    {c.author?.role && (
                      <span
                        className={`badge ${
                          c.author.role === 'SUPPORT' ? 'badge-role-support' : 'badge-role-employee'
                        }`}
                        style={{ fontSize: '0.65rem', padding: '0.1rem 0.4rem' }}
                      >
                        {c.author.role === 'SUPPORT' ? 'Support Staff' : 'Employee'}
                      </span>
                    )}
                  </span>
                  <span className="comment-date">{new Date(c.created_at).toLocaleString()}</span>
                </div>
                <div className="comment-text">{c.content}</div>
              </div>
            ))
          )}
        </div>

        {/* Add Comment Form - Allowed Even If Closed */}
        <form onSubmit={handleCommentSubmit} className="comment-form">
          {commentError && <div className="error-msg">{commentError}</div>}
          <textarea
            className="comment-input"
            rows="3"
            placeholder={
              isClosed
                ? "Add a comment to this closed ticket..."
                : "Type your comment or update here..."
            }
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
          />
          <div className="comment-actions">
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmittingComment || !commentText.trim()}
            >
              <Send size={15} />
              {isSubmittingComment ? 'Posting...' : 'Post Comment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
