"""End-to-end tests for student and assignment flows."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


async def register_and_login(client: AsyncClient) -> dict[str, str]:
    register_resp = await client.post(
        "/auth/register",
        json={"email": "tutor@example.com", "password": "SuperSecure123"},
    )
    assert register_resp.status_code == 201, register_resp.text

    token_resp = await client.post(
        "/auth/token",
        data={"username": "tutor@example.com", "password": "SuperSecure123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200, token_resp.text
    token = token_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_student_crud_with_idempotency(client: AsyncClient) -> None:
    auth_headers = await register_and_login(client)

    payload = {"full_name": "Alice", "level": 2, "progress_points": 10}
    headers = {**auth_headers, "Idempotency-Key": "student-create-1"}

    create_resp = await client.post("/students/", json=payload, headers=headers)
    assert create_resp.status_code == 201, create_resp.text
    student_body = create_resp.json()
    student_id = student_body["id"]

    replay_resp = await client.post("/students/", json=payload, headers=headers)
    assert replay_resp.status_code == 201
    assert replay_resp.json() == student_body

    list_resp = await client.get("/students/", headers=auth_headers)
    assert list_resp.status_code == 200
    assert list_resp.json()[0]["id"] == student_id

    update_resp = await client.patch(
        f"/students/{student_id}",
        json={"progress_points": 25},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["progress_points"] == 25

    delete_resp = await client.delete(f"/students/{student_id}", headers=auth_headers)
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_assignment_flow(client: AsyncClient) -> None:
    auth_headers = await register_and_login(client)

    student_resp = await client.post(
        "/students/",
        json={"full_name": "Bob", "level": 1, "progress_points": 0},
        headers={**auth_headers, "Idempotency-Key": "student-bob"},
    )
    student_id = student_resp.json()["id"]

    assignment_payload = {
        "student_id": student_id,
        "title": "Homework 1",
        "description": "Solve equations",
        "status": "pending",
    }
    headers = {**auth_headers, "Idempotency-Key": "assign-create-1"}

    assign_resp = await client.post("/assignments/", json=assignment_payload, headers=headers)
    assert assign_resp.status_code == 201, assign_resp.text
    assignment_id = assign_resp.json()["id"]

    list_resp = await client.get(f"/assignments/student/{student_id}", headers=auth_headers)
    assert list_resp.status_code == 200
    assert list_resp.json()[0]["id"] == assignment_id

    patch_resp = await client.patch(
        f"/assignments/{assignment_id}",
        json={"status": "done"},
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "done"

    delete_resp = await client.delete(f"/assignments/{assignment_id}", headers=auth_headers)
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_observability_endpoints(client: AsyncClient) -> None:
    resp = await client.get("/health")
    assert resp.status_code == 200

    metrics = await client.get("/metrics")
    assert metrics.status_code == 200
    assert "http_requests_total" in metrics.text
