import React, { useState } from 'react';
import { Plus, Filter, RotateCcw } from 'lucide-react';

const STATUS_OPTIONS = ['ALL', 'Open', 'In Progress', 'Resolved', 'Closed'];
const CATEGORY_OPTIONS = ['ALL', 'Hardware', 'Software', 'Network', 'Access', 'Other'];
const PRIORITY_OPTIONS = ['ALL', 'Low', 'Medium', 'High'];

export default function TicketList({
  tickets,
  selectedTicketId,
  onSelectTicket,
  onOpenCreateModal,
  currentUser,
}) {
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  // Combined multi-criteria filtering
  const filteredTickets = tickets.filter((t) => {
    if (statusFilter !== 'ALL' && t.status !== statusFilter) return false;
    if (categoryFilter !== 'ALL' && t.category !== categoryFilter) return false;
    if (priorityFilter !== 'ALL' && t.priority !== priorityFilter) return false;
    return true;
  });

  const isFiltered = statusFilter !== 'ALL' || categoryFilter !== 'ALL' || priorityFilter !== 'ALL';

  const resetFilters = () => {
    setStatusFilter('ALL');
    setCategoryFilter('ALL');
    setPriorityFilter('ALL');
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
    <div className="card">
      <div className="sidebar-header">
        <div>
          <h2 className="sidebar-title">
            {currentUser?.role === 'SUPPORT' ? 'All Tickets' : 'My Tickets'} ({filteredTickets.length})
          </h2>
        </div>
        {currentUser?.role === 'EMPLOYEE' && (
          <button className="btn-primary" onClick={onOpenCreateModal}>
            <Plus size={16} />
            New Ticket
          </button>
        )}
      </div>

      {/* Multi-Criteria Filter Bar */}
      <div className="filter-controls">
        <div className="filter-row">
          <div className="filter-group">
            <span>Status:</span>
            <select
              className="filter-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              {STATUS_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt === 'ALL' ? 'All Statuses' : opt}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <span>Category:</span>
            <select
              className="filter-select"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            >
              {CATEGORY_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt === 'ALL' ? 'All Categories' : opt}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <span>Priority:</span>
            <select
              className="filter-select"
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
            >
              {PRIORITY_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {opt === 'ALL' ? 'All Priorities' : opt}
                </option>
              ))}
            </select>
          </div>

          {isFiltered && (
            <button className="filter-reset-btn" onClick={resetFilters} title="Reset all filters">
              Reset
            </button>
          )}
        </div>
      </div>

      <div className="ticket-items-container">
        {filteredTickets.length === 0 ? (
          <div className="empty-state">
            <p>No tickets match the selected filters.</p>
          </div>
        ) : (
          filteredTickets.map((t) => (
            <div
              key={t.id}
              className={`ticket-item ${selectedTicketId === t.id ? 'selected' : ''}`}
              onClick={() => onSelectTicket(t.id)}
            >
              <div className="ticket-item-header">
                <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
                  <span className={`badge ${getStatusBadgeClass(t.status)}`}>
                    {t.status}
                  </span>
                  <span className={`badge ${getCategoryBadgeClass(t.category)}`}>
                    {t.category}
                  </span>
                  <span className={`badge ${getPriorityBadgeClass(t.priority)}`}>
                    {t.priority}
                  </span>
                </div>
              </div>

              <h3 className="ticket-item-title">#{t.id} {t.title}</h3>
              <p className="ticket-item-snippet">{t.description}</p>

              <div className="ticket-item-meta">
                <span>By: {t.owner ? t.owner.name : `User #${t.owner_id}`}</span>
                <span>{new Date(t.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
