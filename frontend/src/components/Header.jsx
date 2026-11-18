import React from 'react';
import { ShieldCheck, User as UserIcon } from 'lucide-react';

export default function Header({ users, currentUser, onSelectUser }) {
  const isSupport = currentUser?.role === 'SUPPORT';

  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-icon">IT</div>
        <div>
          <h1 className="brand-title">HelpDesk Support Portal</h1>
          <p className="brand-subtitle">Employee IT ticketing & resolution platform</p>
        </div>
      </div>

      <div className="header-user-controls">
        <div className="user-switch-box">
          <UserIcon size={16} color="#64748b" />
          <span className="user-switch-label">Acting As:</span>
          <select
            className="user-select"
            value={currentUser?.email || ''}
            onChange={(e) => onSelectUser(e.target.value)}
          >
            {users.map((u) => (
              <option key={u.email} value={u.email}>
                {u.name} ({u.role === 'SUPPORT' ? 'Support Staff' : 'Employee'})
              </option>
            ))}
          </select>
        </div>

        {currentUser && (
          <span
            className={`badge ${
              isSupport ? 'badge-role-support' : 'badge-role-employee'
            }`}
          >
            {isSupport ? 'Support Staff' : 'Employee'}
          </span>
        )}
      </div>
    </header>
  );
}
