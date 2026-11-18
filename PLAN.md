# Build Plan: Employee Support Ticket App

This plan breaks down the implementation of the Employee Support Ticket App into incremental, independently committable steps based strictly on [SPEC.md](file:///C:/Users/91778/.gemini/antigravity/scratch/employee-support-ticket-app/SPEC.md) and [Agents.md](file:///C:/Users/91778/.gemini/antigravity/scratch/employee-support-ticket-app/Agents.md).

---

## Step 1: Database Setup and Core Models
- **Touches Database**: **Yes**
- **Files Created/Changed**:
  - `backend/requirements.txt`
  - `backend/app/database.py`
  - `backend/app/models.py`
- **What the step does**:
  - Defines Python dependencies (`fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `pytest`, `httpx`).
  - Sets up SQLite connection engine with a 5000 ms timeout and declarative Base.
  - Implements SQLAlchemy ORM models: `User` (id, name, email, role), `Ticket` (id, title, description, status, priority, owner_id, timestamps), and `Comment` (id, ticket_id, author_id, content, timestamp).
- **How to test**:
  - Run a Python script to initialize the database: verify `tickets.db` is created with tables `users`, `tickets`, and `comments`.
- **Acceptance Criteria Covered**:
  - SPEC.md Section 8 (Data We Store: Users, Tickets, Comments)
  - SPEC.md Section 6 (Non-Functional Needs: SQLite configuration)

---

## Step 2: Pydantic Validation Schemas
- **Touches Database**: **No**
- **Files Created/Changed**:
  - `backend/app/schemas.py`
- **What the step does**:
  - Implements schemas for User, Ticket, and Comment with type hints.
  - Adds validators to ensure:
    - `title` is between 1 and 100 characters and not empty or whitespace.
    - `description` is not empty or whitespace.
    - `content` for comments is not empty or whitespace.
    - `status` only accepts valid statuses (`OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`).
    - `priority` accepts valid levels (`LOW`, `MEDIUM`, `HIGH`, `URGENT`).
- **How to test**:
  - Instantiate schemas in Python with:
    1. Empty title `""` or whitespace `"   "` (expect `ValidationError`).
    2. 101-character title (expect `ValidationError`).
    3. Exactly 100-character title (expect validation success).
    4. Empty description (expect `ValidationError`).
- **Acceptance Criteria Covered**:
  - SPEC.md Story 2 (Raising a Ticket with Missing Fields)
  - SPEC.md Story 3 (Title Character Limit)
  - SPEC.md Section 5 Business Rule 5 (Mandatory Fields & Limits)

---

## Step 3: Role Authentication and User Context Helper
- **Touches Database**: **Yes**
- **Files Created/Changed**:
  - `backend/app/auth.py`
  - `backend/app/routers/auth.py`
- **What the step does**:
  - Implements `get_current_user` dependency resolving user by `X-User-Email` header.
  - Implements `require_support_role` dependency enforcing that `current_user.role == 'SUPPORT'`.
  - Exposes `GET /api/users` (list sample users) and `GET /api/users/me` (get active user profile).
- **How to test**:
  - Make HTTP request to `/api/users/me` with header `X-User-Email: alice@example.com` (expect 200 with Alice's profile).
  - Make HTTP request to `/api/users/me` without header (expect 401 Unauthorized).
- **Acceptance Criteria Covered**:
  - SPEC.md Section 3 (Users: Employee and Support Staff roles)
  - SPEC.md Section 7 (Assumption 4: Authentication mechanism)

---

## Step 4: Sample Data Seeding and Application Startup
- **Touches Database**: **Yes**
- **Files Created/Changed**:
  - `backend/app/seed.py`
  - `backend/app/main.py`
- **What the step does**:
  - Implements `seed_sample_data` to populate sample employees (*Alice Chen*, *Bob Martin*) and support staff (*Charlie Support*, *Dana Support*) with initial sample tickets and comments.
  - Configures FastAPI lifespan handler to auto-create tables and run seed on startup.
  - Adds CORS middleware and health check endpoint `GET /api/health`.
- **How to test**:
  - Start FastAPI server with `uvicorn app.main:app` and call `GET /api/health` (expect `{"status": "ok"}`).
  - Query SQLite database to verify sample users, tickets, and comments are populated.
- **Acceptance Criteria Covered**:
  - SPEC.md Section 5 Business Rule 6 (Use only sample data; no real company data)
  - SPEC.md Section 2 (In Scope: Sample data seeding)

---

## Step 5: Ticket Creation Endpoint with Validation
- **Touches Database**: **Yes**
- **Files Created/Changed**:
  - `backend/app/crud.py`
  - `backend/app/routers/tickets.py`
- **What the step does**:
  - Implements `create_ticket` function in CRUD.
  - Exposes `POST /api/tickets` to raise a support ticket assigned to the authenticated user's ID with initial status `OPEN`.
  - Rejects empty titles, whitespace-only titles, titles > 100 characters, or empty descriptions.
- **How to test**:
  - `POST /api/tickets` with `{"title": "VPN issue", "description": "Cannot connect"}` (expect 201 Created).
  - `POST /api/tickets` with `{"title": "", "description": "Desc"}` (expect 422 Unprocessable Entity).
  - `POST /api/tickets` with title of 101 characters (expect 422 Unprocessable Entity).
- **Acceptance Criteria Covered**:
  - SPEC.md Story 1 (Raising a Support Ticket Happy Path)
  - SPEC.md Story 2 (Missing Fields Negative Case)
  - SPEC.md Story 3 (Title Character Limit Edge Case)
  - SPEC.md Section 5 Business Rule 5 (Title up to 100 characters and description cannot be empty)

---

## Step 6: Role-Based Ticket Visibility
- **Touches Database**: **Yes**
- **Files Created/Changed**:
  - `backend/app/crud.py`
  - `backend/app/routers/tickets.py`
- **What the step does**:
  - Implements `get_visible_tickets` and `get_ticket_by_id`.
  - Exposes `GET /api/tickets`:
    - Returns only tickets where `owner_id == current_user.id` if the user has `EMPLOYEE` role.
    - Returns all tickets across all employees if the user has `SUPPORT` role.
  - Exposes `GET /api/tickets/{ticket_id}`:
    - Returns 403 Forbidden if an employee attempts to view another employee's ticket.
    - Returns 200 OK for support staff for any valid ticket.
- **How to test**:
  - Call `GET /api/tickets` with `X-User-Email: alice@example.com` (expect only Alice's tickets).
  - Call `GET /api/tickets` with `X-User-Email: bob@example.com` (expect only Bob's tickets).
  - Call `GET /api/tickets` with `X-User-Email: charlie@example.com` (expect all tickets).
  - Call `GET /api/tickets/{bob_ticket_id}` with Alice's email (expect 403 Forbidden).
- **Acceptance Criteria Covered**:
  - SPEC.md Story 4 (Ticket Visibility by Role Happy Path & Negative Case)
  - SPEC.md Section 5 Business Rule 2 (An employee sees only their own tickets; support staff see all)

---

## Step 7: Support-Only Status Updates
- **Touches Database**: **Yes**
- **Files Created/Changed**:
  - `backend/app/crud.py`
  - `backend/app/routers/tickets.py`
- **What the step does**:
  - Implements `update_ticket_status` in CRUD.
  - Exposes `PATCH /api/tickets/{ticket_id}/status`.
  - Uses `require_support_role` dependency to enforce that only support staff can invoke this endpoint.
  - Returns 403 Forbidden if an employee attempts to change a ticket's status.
- **How to test**:
  - Call `PATCH /api/tickets/{id}/status` with `{"status": "IN_PROGRESS"}` using Alice's header (`EMPLOYEE`) (expect 403 Forbidden).
  - Call `PATCH /api/tickets/{id}/status` with `{"status": "IN_PROGRESS"}` using Charlie's header (`SUPPORT`) (expect 200 OK with updated status).
- **Acceptance Criteria Covered**:
  - SPEC.md Story 5 (Restricting Status Changes to Support Staff Negative & Happy Path)
  - SPEC.md Section 5 Business Rule 1 (Only support staff can change a ticket's status)

---

## Step 8: Closed Ticket Immutability and Commenting
- **Touches Database**: **Yes**
- **Files Created/Changed**:
  - `backend/app/crud.py`
  - `backend/app/routers/tickets.py`
  - `backend/app/routers/comments.py`
- **What the step does**:
  - Implements `PUT /api/tickets/{ticket_id}` to edit ticket title, description, or priority:
    - If `ticket.status == 'CLOSED'`, rejects request with 400 Bad Request ("A Closed ticket cannot be edited").
  - Implements `POST /api/tickets/{ticket_id}/comments` and `GET /api/tickets/{ticket_id}/comments`:
    - Allows adding comments to any ticket, including `CLOSED` tickets.
    - Validates comment content is not empty.
- **How to test**:
  - Update ticket status to `CLOSED` via support user.
  - Attempt `PUT /api/tickets/{id}` to edit title (expect 400 Bad Request).
  - Call `POST /api/tickets/{id}/comments` with `{"content": "Checking on this"}` (expect 201 Created).
  - Call `GET /api/tickets/{id}/comments` (verify comment is listed).
- **Acceptance Criteria Covered**:
  - SPEC.md Story 6 (Closed Ticket Edit Prevention Negative Case)
  - SPEC.md Story 7 (Adding Comments to a Closed Ticket Edge Case)
  - SPEC.md Section 5 Business Rule 3 (A Closed ticket cannot be edited)
  - SPEC.md Section 5 Business Rule 4 (Comments can still be added to a Closed ticket)

---

## Step 9: Comprehensive Automated Pytest Suite
- **Touches Database**: **Yes** (in-memory isolated SQLite test database)
- **Files Created/Changed**:
  - `backend/pytest.ini`
  - `backend/tests/__init__.py`
  - `backend/tests/conftest.py`
  - `backend/tests/test_tickets.py`
- **What the step does**:
  - Configures isolated test database session fixture and FastAPI `TestClient`.
  - Implements unit and integration tests covering:
    - `test_validation_empty_title_and_description`
    - `test_validation_title_max_100_chars`
    - `test_ticket_visibility_rule`
    - `test_only_support_staff_can_change_status`
    - `test_closed_ticket_cannot_be_edited_but_comments_allowed`
- **How to test**:
  - Execute `pytest -v` from `backend` directory.
  - Verify all tests pass with 100% success rate.
- **Acceptance Criteria Covered**:
  - SPEC.md Section 6 (Non-Functional Needs: 100% test pass rate)
  - SPEC.md Stories 1, 2, 3, 4, 5, 6, 7
  - SPEC.md Section 5 Business Rules 1, 2, 3, 4, 5

---

## Step 10: Frontend Scaffolding and API Client
- **Touches Database**: **No**
- **Files Created/Changed**:
  - `frontend/package.json`
  - `frontend/vite.config.js`
  - `frontend/index.html`
  - `frontend/src/api.js`
- **What the step does**:
  - Sets up Vite + React configuration with proxy to `http://localhost:8000/api`.
  - Implements `api.js` helper methods for users, tickets, and comments, injecting `X-User-Email` header.
- **How to test**:
  - Run `npm run build` in `frontend` directory; verify build finishes with zero errors.
- **Acceptance Criteria Covered**:
  - SPEC.md Section 6 (Non-Functional Needs: UI rendering and responsiveness)
  - SPEC.md Section 7 (Assumption 4: Demonstration user context switching)

---

## Step 11: Header and User Role Switcher Component
- **Touches Database**: **No**
- **Files Created/Changed**:
  - `frontend/src/components/Header.jsx`
  - `frontend/src/index.css`
- **What the step does**:
  - Renders app header with brand title and user selector dropdown (Alice, Bob, Charlie, Dana).
  - Displays dynamic badge showing active role (`Employee` or `Support Staff`).
- **How to test**:
  - Mount component and select different users; verify role badge toggles between `Employee` and `Support Staff`.
- **Acceptance Criteria Covered**:
  - SPEC.md Section 3 (Users: Employee and Support Staff)
  - SPEC.md Section 5 Business Rule 6 (Sample user data)

---

## Step 12: Ticket List with Status Filters Component
- **Touches Database**: **No**
- **Files Created/Changed**:
  - `frontend/src/components/TicketList.jsx`
- **What the step does**:
  - Renders list of tickets showing ID, title, description preview, status badge, priority badge, and owner name.
  - Implements filter chips: `All`, `Open`, `In Progress`, `Resolved`, `Closed`.
  - Displays "My Tickets" for employees and "All Tickets" for support staff.
- **How to test**:
  - Pass ticket list; toggle filter chips and verify filtered counts update accurately.
- **Acceptance Criteria Covered**:
  - SPEC.md Story 4 (Ticket Visibility by Role)
  - SPEC.md Section 5 Business Rule 2 (Visibility boundaries)

---

## Step 13: Ticket Creation and Edit Modal with Character Counter
- **Touches Database**: **No**
- **Files Created/Changed**:
  - `frontend/src/components/TicketModal.jsx`
- **What the step does**:
  - Implements modal dialog for creating and editing tickets.
  - Displays live character counter `xx / 100` for title with visual warning at limit.
  - Enforces `maxLength={100}` on title input and prevents submission of empty fields.
- **How to test**:
  - Attempt to type more than 100 characters into title input (verify typing stops at 100).
  - Clear title and verify submit button is disabled or triggers validation error.
- **Acceptance Criteria Covered**:
  - SPEC.md Story 1 (Raising a Support Ticket)
  - SPEC.md Story 2 (Missing Fields)
  - SPEC.md Story 3 (Title Character Limit)
  - SPEC.md Section 5 Business Rule 5 (Title up to 100 chars, non-empty description)

---

## Step 14: Ticket Detail View, Status Changer, and Comments Thread
- **Touches Database**: **No**
- **Files Created/Changed**:
  - `frontend/src/components/TicketDetail.jsx`
  - `frontend/src/App.jsx`
  - `frontend/src/main.jsx`
- **What the step does**:
  - Displays full ticket details and comments thread.
  - If current user is `SUPPORT`, renders status dropdown to change status.
  - If ticket status is `CLOSED`:
    - Shows alert banner indicating the ticket is closed and cannot be edited.
    - Hides or disables the "Edit Ticket" button.
  - Enables comment input form on all tickets, including `CLOSED` tickets.
- **How to test**:
  1. Open a closed ticket as an employee: verify status dropdown is absent, edit button is absent, and closed banner is shown.
  2. Post a comment on the closed ticket: verify comment is added to the thread.
  3. Switch to support user: verify status changer dropdown is displayed and allows changing status.
- **Acceptance Criteria Covered**:
  - SPEC.md Story 5 (Restricting Status Changes to Support Staff)
  - SPEC.md Story 6 (Closed Ticket Edit Prevention)
  - SPEC.md Story 7 (Adding Comments to a Closed Ticket)
  - SPEC.md Section 5 Business Rules 1, 3, 4

---

## Step 15: Run Instructions & Documentation Verification
- **Touches Database**: **No**
- **Files Created/Changed**:
  - `Agents.md`
  - `README.md`
- **What the step does**:
  - Updates `Agents.md` and `README.md` with explicit backend startup, pytest run, and frontend dev/build commands.
  - Verifies that all rules from `Agents.md` and `SPEC.md` are documented and test instructions are clear.
- **How to test**:
  - Follow commands in `README.md` sequentially to verify backend starts, tests pass, and frontend builds.
- **Acceptance Criteria Covered**:
  - Agents.md Build / test section
  - Agents.md Done criteria ("tests pass, no secrets in code, I have read every change")
