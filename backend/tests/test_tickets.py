from fastapi.testclient import TestClient


def test_validation_empty_title_and_description(client: TestClient) -> None:
    """Title and description cannot be empty or whitespace."""
    headers = {"X-User-Email": "alice@example.com"}

    # Empty title
    res_empty_title = client.post(
        "/api/tickets",
        json={"title": "   ", "description": "Valid description", "category": "Hardware", "priority": "High"},
        headers=headers,
    )
    assert res_empty_title.status_code == 422

    # Empty description
    res_empty_desc = client.post(
        "/api/tickets",
        json={"title": "Valid title", "description": "   ", "category": "Hardware", "priority": "High"},
        headers=headers,
    )
    assert res_empty_desc.status_code == 422


def test_validation_title_max_100_chars(client: TestClient) -> None:
    """Title must be up to 100 characters."""
    headers = {"X-User-Email": "alice@example.com"}

    long_title = "A" * 101
    res = client.post(
        "/api/tickets",
        json={"title": long_title, "description": "Valid description", "category": "Hardware", "priority": "High"},
        headers=headers,
    )
    assert res.status_code == 422

    # Exactly 100 characters should succeed
    exact_100_title = "B" * 100
    res_valid = client.post(
        "/api/tickets",
        json={"title": exact_100_title, "description": "Valid description", "category": "Software", "priority": "Low"},
        headers=headers,
    )
    assert res_valid.status_code == 201
    assert res_valid.json()["title"] == exact_100_title


def test_category_and_priority_validation(client: TestClient) -> None:
    """Category must be Hardware, Software, Network, Access, Other. Priority must be Low, Medium, High."""
    headers = {"X-User-Email": "alice@example.com"}

    # Invalid category
    res_inv_cat = client.post(
        "/api/tickets",
        json={"title": "Test Title", "description": "Valid desc", "category": "Finance", "priority": "High"},
        headers=headers,
    )
    assert res_inv_cat.status_code == 422

    # Invalid priority
    res_inv_pri = client.post(
        "/api/tickets",
        json={"title": "Test Title", "description": "Valid desc", "category": "Hardware", "priority": "Critical"},
        headers=headers,
    )
    assert res_inv_pri.status_code == 422

    # Valid categories and priorities
    valid_categories = ["Hardware", "Software", "Network", "Access", "Other"]
    for cat in valid_categories:
        res = client.post(
            "/api/tickets",
            json={"title": f"Valid {cat}", "description": "Details", "category": cat, "priority": "Medium"},
            headers=headers,
        )
        assert res.status_code == 201
        assert res.json()["category"] == cat


def test_ticket_visibility_rule(client: TestClient) -> None:
    """An employee sees only their own tickets; support staff see all."""
    alice_headers = {"X-User-Email": "alice@example.com"}
    bob_headers = {"X-User-Email": "bob@example.com"}
    support_headers = {"X-User-Email": "charlie@example.com"}

    # Alice creates ticket A
    res_a = client.post(
        "/api/tickets",
        json={"title": "Alice's Issue", "description": "Laptop not charging", "category": "Hardware", "priority": "High"},
        headers=alice_headers,
    )
    assert res_a.status_code == 201
    ticket_a_id = res_a.json()["id"]

    # Bob creates ticket B
    res_b = client.post(
        "/api/tickets",
        json={"title": "Bob's Issue", "description": "Cannot log in to VPN", "category": "Network", "priority": "High"},
        headers=bob_headers,
    )
    assert res_b.status_code == 201
    ticket_b_id = res_b.json()["id"]

    # Alice checks list: sees only her own
    alice_list = client.get("/api/tickets", headers=alice_headers).json()
    assert len(alice_list) == 1
    assert alice_list[0]["id"] == ticket_a_id

    # Bob checks list: sees only his own
    bob_list = client.get("/api/tickets", headers=bob_headers).json()
    assert len(bob_list) == 1
    assert bob_list[0]["id"] == ticket_b_id

    # Charlie (Support) checks list: sees all tickets
    support_list = client.get("/api/tickets", headers=support_headers).json()
    assert len(support_list) == 2

    # Alice cannot view Bob's ticket details directly
    res_forbidden = client.get(f"/api/tickets/{ticket_b_id}", headers=alice_headers)
    assert res_forbidden.status_code == 403

    # Charlie can view Bob's ticket details
    res_support_view = client.get(f"/api/tickets/{ticket_b_id}", headers=support_headers)
    assert res_support_view.status_code == 200


def test_status_transition_rules(client: TestClient) -> None:
    """
    - Only support staff can change ticket status.
    - Support staff can move tickets directly between Open, In Progress, Resolved.
    - Once Closed, a ticket cannot be reopened or edited.
    - Employees cannot change status.
    """
    alice_headers = {"X-User-Email": "alice@example.com"}
    support_headers = {"X-User-Email": "charlie@example.com"}

    # Alice creates ticket
    res = client.post(
        "/api/tickets",
        json={"title": "Monitor issue", "description": "No display signal", "category": "Hardware", "priority": "Low"},
        headers=alice_headers,
    )
    ticket_id = res.json()["id"]
    assert res.json()["status"] == "Open"

    # Employee attempts to change status -> 403 Forbidden
    res_emp = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "In Progress"},
        headers=alice_headers,
    )
    assert res_emp.status_code == 403

    # Support staff moves directly to In Progress -> 200 OK
    res_prog = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "In Progress"},
        headers=support_headers,
    )
    assert res_prog.status_code == 200
    assert res_prog.json()["status"] == "In Progress"

    # Support staff moves directly to Resolved -> 200 OK
    res_res = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "Resolved"},
        headers=support_headers,
    )
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "Resolved"

    # Support staff moves back to Open if needed -> 200 OK
    res_reopen = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "Open"},
        headers=support_headers,
    )
    assert res_reopen.status_code == 200
    assert res_reopen.json()["status"] == "Open"

    # Support staff moves to Closed -> 200 OK
    res_close = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "Closed"},
        headers=support_headers,
    )
    assert res_close.status_code == 200
    assert res_close.json()["status"] == "Closed"

    # Once Closed, ticket CANNOT be reopened -> 400 Bad Request
    res_reopen_closed = client.patch(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "In Progress"},
        headers=support_headers,
    )
    assert res_reopen_closed.status_code == 400
    assert "cannot be reopened" in res_reopen_closed.json()["detail"].lower()


def test_edit_permissions_on_active_tickets(client: TestClient) -> None:
    """
    - Only the employee who created the ticket can edit title, description, category, priority.
    - Support staff cannot modify the employee's original ticket details.
    - Closed tickets cannot be edited.
    """
    alice_headers = {"X-User-Email": "alice@example.com"}
    bob_headers = {"X-User-Email": "bob@example.com"}
    support_headers = {"X-User-Email": "charlie@example.com"}

    # Alice creates ticket
    res = client.post(
        "/api/tickets",
        json={"title": "Keyboard sticky", "description": "Key 'A' is stuck", "category": "Hardware", "priority": "Medium"},
        headers=alice_headers,
    )
    ticket_id = res.json()["id"]

    # Bob (different employee) attempts to edit Alice's ticket -> 403 Forbidden
    res_bob_edit = client.put(
        f"/api/tickets/{ticket_id}",
        json={"title": "Bob hacking title", "description": "Edited"},
        headers=bob_headers,
    )
    assert res_bob_edit.status_code == 403

    # Support staff attempts to edit ticket details -> 403 Forbidden
    res_support_edit = client.put(
        f"/api/tickets/{ticket_id}",
        json={"title": "Support changing title", "description": "Edited by tech"},
        headers=support_headers,
    )
    assert res_support_edit.status_code == 403

    # Alice (creator) edits her own active ticket -> 200 OK
    res_alice_edit = client.put(
        f"/api/tickets/{ticket_id}",
        json={"title": "Keyboard spacebar sticky", "description": "Actually spacebar", "category": "Hardware", "priority": "High"},
        headers=alice_headers,
    )
    assert res_alice_edit.status_code == 200
    assert res_alice_edit.json()["title"] == "Keyboard spacebar sticky"
    assert res_alice_edit.json()["priority"] == "High"

    # Support closes the ticket
    client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "Closed"}, headers=support_headers)

    # Alice attempts to edit Closed ticket -> 400 Bad Request
    res_edit_closed = client.put(
        f"/api/tickets/{ticket_id}",
        json={"title": "Trying to edit closed ticket", "description": "New info"},
        headers=alice_headers,
    )
    assert res_edit_closed.status_code == 400
    assert "closed ticket cannot be edited" in res_edit_closed.json()["detail"].lower()


def test_comment_rules_and_closed_tickets(client: TestClient) -> None:
    """Both employees and support staff can add comments; allowed even on closed tickets."""
    alice_headers = {"X-User-Email": "alice@example.com"}
    support_headers = {"X-User-Email": "charlie@example.com"}

    # Alice creates ticket
    res = client.post(
        "/api/tickets",
        json={"title": "Folder permission", "description": "Need access to /projects/alpha", "category": "Access", "priority": "Medium"},
        headers=alice_headers,
    )
    ticket_id = res.json()["id"]

    # Support staff comments
    c1_res = client.post(
        f"/api/tickets/{ticket_id}/comments",
        json={"content": "Adding you to the AD group now."},
        headers=support_headers,
    )
    assert c1_res.status_code == 201
    assert c1_res.json()["author"]["name"] == "Charlie Support"
    assert "created_at" in c1_res.json()

    # Support closes ticket
    client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "Closed"}, headers=support_headers)

    # Alice comments on Closed ticket
    c2_res = client.post(
        f"/api/tickets/{ticket_id}/comments",
        json={"content": "Access confirmed, thanks!"},
        headers=alice_headers,
    )
    assert c2_res.status_code == 201
    assert c2_res.json()["author"]["name"] == "Alice Employee"

    # Verify both comments exist in order
    comments = client.get(f"/api/tickets/{ticket_id}/comments", headers=alice_headers).json()
    assert len(comments) == 2
    assert comments[0]["content"] == "Adding you to the AD group now."
    assert comments[1]["content"] == "Access confirmed, thanks!"


def test_combined_filters_and_sorting(client: TestClient) -> None:
    """Test filtering by combined status, category, and priority, with newest first sorting."""
    alice_headers = {"X-User-Email": "alice@example.com"}

    # Create 3 tickets with different metadata
    client.post(
        "/api/tickets",
        json={"title": "T1", "description": "Desc 1", "category": "Hardware", "priority": "High"},
        headers=alice_headers,
    )
    client.post(
        "/api/tickets",
        json={"title": "T2", "description": "Desc 2", "category": "Software", "priority": "Medium"},
        headers=alice_headers,
    )
    client.post(
        "/api/tickets",
        json={"title": "T3", "description": "Desc 3", "category": "Hardware", "priority": "Medium"},
        headers=alice_headers,
    )

    # Default sort: newest first (T3 then T2 then T1)
    all_tickets = client.get("/api/tickets", headers=alice_headers).json()
    assert len(all_tickets) == 3
    assert all_tickets[0]["title"] == "T3"
    assert all_tickets[1]["title"] == "T2"
    assert all_tickets[2]["title"] == "T1"

    # Filter by category = Hardware
    hw_tickets = client.get("/api/tickets?category=Hardware", headers=alice_headers).json()
    assert len(hw_tickets) == 2
    assert {t["title"] for t in hw_tickets} == {"T1", "T3"}

    # Combined filter: category = Hardware and priority = High
    hw_high = client.get("/api/tickets?category=Hardware&priority=High", headers=alice_headers).json()
    assert len(hw_high) == 1
    assert hw_high[0]["title"] == "T1"


def test_only_employees_can_create_tickets(client: TestClient) -> None:
    """Only employees can create tickets; support staff are forbidden."""
    support_headers = {"X-User-Email": "charlie@example.com"}
    employee_headers = {"X-User-Email": "alice@example.com"}

    # Support staff attempts to create a ticket -> 403 Forbidden
    res_support = client.post(
        "/api/tickets",
        json={"title": "Tech issue", "description": "Support creating ticket", "category": "Hardware", "priority": "Low"},
        headers=support_headers,
    )
    assert res_support.status_code == 403
    assert "only employees can create support tickets" in res_support.json()["detail"].lower()

    # Employee creates a ticket -> 201 Created
    res_emp = client.post(
        "/api/tickets",
        json={"title": "Mouse broken", "description": "Scroll wheel not working", "category": "Hardware", "priority": "Low"},
        headers=employee_headers,
    )
    assert res_emp.status_code == 201
    assert res_emp.json()["title"] == "Mouse broken"
