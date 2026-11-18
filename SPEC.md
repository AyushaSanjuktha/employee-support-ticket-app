+# Specification: Employee Support Ticket App

## 1. Problem
Employees face IT issues during daily operations and need a structured system to raise support tickets and communicate with IT. IT support staff need central visibility across all tickets to manage and update resolution statuses while ensuring that unauthorized users cannot alter ticket states or edit finalized tickets.

---

## 2. Scope and Out of Scope
- **In Scope**:
  - Employee creation of IT support tickets with title (up to 100 characters) and description.
  - Role-based ticket visibility (employees see only their own tickets; support staff see all tickets).
  - Status updates restricted exclusively to support staff.
  - Immutability of closed tickets (prohibiting title, description, or detail edits).
  - Comment addition on tickets by ticket owners and support staff, including on closed tickets.
  - Sample data seeding for employees, support staff, and initial tickets.
- **Out of Scope**:
  - Integration with production corporate identity providers (LDAP, Active Directory, SSO).
  - Real company or customer data.
  - Email or SMS external notification delivery.
  - File attachments, screenshots, or binary uploads.
  - Ticket deletion or purging functionality.

---

## 3. Users
- **Employee**: An internal team member who raises IT support tickets, tracks the status of their own tickets, edits their open tickets, and posts comments.
- **Support Staff**: An IT technician or administrator who views all organizational tickets, updates ticket statuses, and provides comments/updates.

---

## 4. What a ticket stores
| Detail | Rule | Who fills it |
|---|---|---|
| Title | Required, up to 100 characters | Employee |
| Description | Required | Employee |
| Category | Hardware, Software, Network, Access, Other | Employee picks from a list |
| Priority | Low, Medium, High | Employee picks from a list |
| Status | Open, In Progress, Resolved, Closed | App sets Open; support staff change it |
| Created by | The employee's name | App fills it automatically |
| Created date | Date of creation | App fills it automatically |
| Last updated date | Date of the latest change | App updates it on every change |

**Status flow:** Open → In Progress → Resolved → Closed

---

## 5. User Stories with Acceptance Criteria (Given / When / Then)

### Story 1: Raise a ticket
As an **employee**, I want to raise a ticket, so that IT knows my problem.
- **Normal:** Given I am an employee, when I submit a title, a description, a category and a priority, then the ticket is created with status Open, my name as created by, and today's date as created date and last updated date.
- **Negative:** Given the title is empty (or only spaces), when I submit, then I see "Title is required" and no ticket is created.
- **Negative:** Given the description is empty (or only spaces), when I submit, then I see "Description is required" and no ticket is created.
- **Edge:** Given the title has exactly 100 characters, when I submit, then the ticket is saved.
- **Negative edge:** Given the title has 101 characters, when I submit, then I see "Title must be 100 characters or less" and no ticket is created.

### Story 2: See my own tickets
As an **employee**, I want to see only my tickets and their status, so that I can follow up.
- **Normal:** Given I have 2 tickets and other employees have 3, when I open my ticket list, then I see only my 2 tickets with their status.
- **Negative:** Given a ticket belongs to another employee, when I try to open it, then I am blocked and I do not see its content.
- **Edge:** Given I have no tickets, when I open my list, then I see "No tickets yet".

### Story 3: See all tickets
As **support staff**, I want to see all tickets, so that I can manage the work.
- **Normal:** Given there are 5 tickets from different employees, when I open the ticket list, then I see all 5.

### Story 4: Change the status
As **support staff**, I want to change a ticket's status, so that the employee knows the progress.
- **Normal:** Given a ticket is Open, when I change it to In Progress, then the status changes and the last updated date is updated.
- **Negative:** Given I am an employee, when I try to change a ticket's status, then I am blocked with "Not allowed" and the status does not change.

### Story 5: Add comments
As an **employee or support staff**, I want to add comments on a ticket, so that we can discuss the problem.
- **Normal:** Given I can see a ticket, when I add a comment, then it is saved with my name and the date.
- **Edge:** Given the ticket is Closed, when I add a comment, then it is saved.
- **Negative:** Given I am an employee and the ticket belongs to someone else, when I try to add a comment, then I am blocked.
- **Negative:** Given the comment is empty, when I submit it, then I see "Comment cannot be empty" and it is not saved.

### Story 6: Closed tickets are locked
As a **ticket owner**, I want a Closed ticket to stay as it was, so that the record is reliable.
- **Negative:** Given a ticket is Closed, when I try to edit its title or description, then I see "Closed tickets cannot be edited" and nothing changes.
- **Normal:** Given a ticket is Open, when I (the owner) edit its description, then the change is saved and the last updated date is updated.


---

## 6. Business Rules
1. **Status Update Authority**: Only support staff can change a ticket's status.
2. **Access & Visibility Boundary**: An employee sees only their own tickets; support staff see all.
3. **Closed Ticket Immutability**: A Closed ticket cannot be edited.
4. **Closed Ticket Comment Allowance**: Comments can still be added to a Closed ticket.
5. **Mandatory Fields & Limits**: Title (up to 100 characters) and description cannot be empty.
6. **Data Boundaries**: Use only sample data. No real company data.

---

## 7. Non-Functional Needs (with numbers)
- **Input Constraints**: Title length maximum = 100 characters; minimum = 1 character (trimmed). Description minimum = 1 character (trimmed).
- **API Response Latency**: Maximum 200 ms response time for local API operations (ticket creation, listing, detail fetch, status change, and commenting).
- **UI Render Latency**: Initial dashboard render within 1.0 second under local environment.
- **Test Pass Rate**: 100% automated test pass rate for all business rule unit and integration tests.
- **Database Concurrency**: Single-file SQLite database with connection timeout of 5000 ms to handle local concurrent access without thread deadlocks.

---

## 8. Assumptions to Confirm
1. **Allowed Status Values**: Whether the valid statuses are strictly `Open`, `In Progress`, `Resolved`, and `Closed`, or if additional lifecycle steps are required.
2. **Priority Taxonomy**: Whether ticket priority levels (e.g., `Low`, `Medium`, `High`, `Urgent`) are fixed or optional.
3. **Support Edit Permissions**: Whether support staff should have permission to edit the description of an open ticket submitted by an employee, or if only the original author can edit it.
4. **Authentication Flow**: Whether the current header-based user identifier (`X-User-Email`) with sample user switcher is sufficient for demonstration, or if session/JWT tokens are required for deployment.

---

## 9. Data We Store

### Users
- **ID**: Unique integer identifier.
- **Name**: User's display name (string).
- **Email**: Unique contact email address (string).
- **Role**: User role flag (`EMPLOYEE` or `SUPPORT`).

### Tickets
- **ID**: Unique integer identifier.
- **Title**: Summary of the issue (string, max 100 characters, required).
- **Description**: Detailed explanation of the issue (text, required).
- **Status**: Current lifecycle status (e.g., `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`).
- **Priority**: Urgency level (e.g., `LOW`, `MEDIUM`, `HIGH`, `URGENT`).
- **Owner ID**: Foreign key referencing the User who created the ticket.
- **Created Timestamp**: UTC timestamp of ticket creation.
- **Updated Timestamp**: UTC timestamp of last ticket modification.

### Comments
- **ID**: Unique integer identifier.
- **Ticket ID**: Foreign key referencing the associated Ticket.
- **Author ID**: Foreign key referencing the User who authored the comment.
- **Content**: Non-empty text body of the comment.
- **Created Timestamp**: UTC timestamp of comment submission.
