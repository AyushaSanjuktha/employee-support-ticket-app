import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import TicketList from './components/TicketList';
import TicketDetail from './components/TicketDetail';
import TicketModal from './components/TicketModal';
import { api, setActiveUserEmail } from './api';

export default function App() {
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [selectedTicketId, setSelectedTicketId] = useState(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTicket, setEditingTicket] = useState(null);
  const [toastMessage, setToastMessage] = useState('');

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(''), 3500);
  };

  // Initial load: fetch users
  useEffect(() => {
    async function init() {
      try {
        const userList = await api.getUsers();
        setUsers(userList);
        if (userList.length > 0) {
          const defaultUser = userList[0]; // Alice Chen (EMPLOYEE)
          setCurrentUser(defaultUser);
          setActiveUserEmail(defaultUser.email);
        }
      } catch (err) {
        console.error('Failed to fetch initial users:', err);
      }
    }
    init();
  }, []);

  // Fetch tickets whenever active user changes
  useEffect(() => {
    if (!currentUser) return;
    loadTickets();
  }, [currentUser]);

  // Load ticket details when selectedTicketId changes
  useEffect(() => {
    if (!selectedTicketId || !currentUser) {
      setSelectedTicket(null);
      return;
    }
    loadTicketDetail(selectedTicketId);
  }, [selectedTicketId, currentUser]);

  const loadTickets = async () => {
    try {
      const data = await api.getTickets();
      setTickets(data);
      // If currently selected ticket is still in the list, keep it selected; else select first
      if (data.length > 0) {
        if (!data.some((t) => t.id === selectedTicketId)) {
          setSelectedTicketId(data[0].id);
        }
      } else {
        setSelectedTicketId(null);
        setSelectedTicket(null);
      }
    } catch (err) {
      console.error('Error loading tickets:', err);
      showToast(`Error: ${err.message}`);
    }
  };

  const loadTicketDetail = async (id) => {
    try {
      const data = await api.getTicket(id);
      setSelectedTicket(data);
    } catch (err) {
      console.error('Error fetching ticket detail:', err);
      setSelectedTicket(null);
      showToast(`Could not load ticket #${id}: ${err.message}`);
    }
  };

  const handleSelectUser = (email) => {
    const found = users.find((u) => u.email === email);
    if (found) {
      setActiveUserEmail(found.email);
      setCurrentUser(found);
      showToast(`Switched view to ${found.name} (${found.role})`);
    }
  };

  const handleCreateOrEditTicket = async (formData) => {
    if (editingTicket) {
      // Edit existing ticket
      const updated = await api.updateTicket(editingTicket.id, formData);
      showToast(`Ticket #${updated.id} updated successfully.`);
      await loadTickets();
      if (selectedTicketId === updated.id) {
        await loadTicketDetail(updated.id);
      }
    } else {
      // Create new ticket (employee only)
      if (currentUser?.role !== 'EMPLOYEE') {
        showToast('Only employees can create support tickets.');
        return;
      }
      const created = await api.createTicket(formData);
      showToast(`Ticket #${created.id} raised successfully.`);
      await loadTickets();
      setSelectedTicketId(created.id);
    }
  };

  const handleStatusChange = async (ticketId, newStatus) => {
    try {
      const updated = await api.updateTicketStatus(ticketId, newStatus);
      showToast(`Ticket #${ticketId} status changed to ${newStatus}.`);
      await loadTickets();
      if (selectedTicketId === ticketId) {
        await loadTicketDetail(ticketId);
      }
    } catch (err) {
      showToast(`Error updating status: ${err.message}`);
    }
  };

  const handleAddComment = async (ticketId, content) => {
    await api.addComment(ticketId, content);
    showToast('Comment posted.');
    await loadTicketDetail(ticketId);
  };

  const handleOpenCreateModal = () => {
    if (currentUser?.role !== 'EMPLOYEE') {
      showToast('Only employees can create support tickets.');
      return;
    }
    setEditingTicket(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (ticket) => {
    setEditingTicket(ticket);
    setIsModalOpen(true);
  };

  return (
    <div className="app-root">
      <Header
        users={users}
        currentUser={currentUser}
        onSelectUser={handleSelectUser}
      />

      <main className="app-container">
        <div className="main-grid">
          <TicketList
            tickets={tickets}
            selectedTicketId={selectedTicketId}
            onSelectTicket={setSelectedTicketId}
            onOpenCreateModal={handleOpenCreateModal}
            currentUser={currentUser}
          />

          <TicketDetail
            ticket={selectedTicket}
            currentUser={currentUser}
            onStatusChange={handleStatusChange}
            onOpenEditModal={handleOpenEditModal}
            onAddComment={handleAddComment}
          />
        </div>
      </main>

      <TicketModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateOrEditTicket}
        initialData={editingTicket}
      />

      {toastMessage && <div className="toast">{toastMessage}</div>}
    </div>
  );
}
