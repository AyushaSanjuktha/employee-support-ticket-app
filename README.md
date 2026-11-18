# Employee Support Ticket App

A full-stack IT support ticketing web application where employees raise support tickets and support staff manage and update their resolution status.

## Tech Stack
- **Backend**: FastAPI (Python 3.14+), SQLite, SQLAlchemy, Pydantic, Pytest
- **Frontend**: React 19, Vite, Lucide Icons, Modern CSS

---

## Core Business Rules
1. **Ticket Creation Restriction**: Only Employees can create support tickets. Support Staff cannot access the creation option in the UI and are denied on the backend API (`403 Forbidden`).
2. **Status Update Authority**: Only support staff can change a ticket's status (`Open`, `In Progress`, `Resolved`, `Closed`).
3. **Flexible Active Statuses**: Support staff can move tickets directly between `Open`, `In Progress`, and `Resolved`.
4. **Closed Ticket Finality**: Once a ticket is `Closed`, it cannot be reopened or edited.
5. **Edit Permissions on Active Tickets**: Only the employee who created the ticket can edit its title, description, category, and priority while it is not Closed. Support staff cannot modify the employee's original ticket details.
6. **Access & Visibility Boundary**: An employee sees only their own tickets; support staff see all tickets across the organization.
7. **Closed Ticket Comment Allowance**: Comments can still be added to Closed tickets by both employees and support staff.
8. **Mandatory Fields & Limits**: Title (required, up to 100 characters) and description (required) cannot be empty.
9. **Categories & Priorities**:
   - Categories: `Hardware`, `Software`, `Network`, `Access`, `Other`
   - Priorities: `Low`, `Medium`, `High`

---

## Sample Users & Seeded Tickets

### Sample Users
- **Alice** (`alice@example.com`) – Role: `EMPLOYEE`
- **Bob** (`bob@example.com`) – Role: `EMPLOYEE`
- **Charlie** (`charlie@example.com`) – Role: `SUPPORT`
- **Dana** (`dana@example.com`) – Role: `SUPPORT`

The UI header features an active user switcher allowing instant testing of Employee vs Support views.

### Seeded Tickets
1. **Laptop not charging** | Hardware | High | Open | Assigned to: Alice
2. **Cannot log in to VPN** | Network | High | In Progress | Assigned to: Bob
3. **Need access to the shared project folder** | Access | Medium | Open | Assigned to: Alice
4. **Excel keeps crashing on startup** | Software | Medium | Resolved | Assigned to: Bob
5. **Request a second monitor** | Hardware | Low | Closed | Assigned to: Alice

---

## Running the Application

### 1. Backend Server
```powershell
cd backend
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```
- Interactive Swagger API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### 2. Automated Tests
```powershell
cd backend
.\.venv\Scripts\pytest.exe -v
```

### 3. Frontend Development Server
```powershell
cd frontend
npm run dev
```
- Access web application: `http://localhost:5173`

### 4. Frontend Production Build
```powershell
cd frontend
npm run build
```
