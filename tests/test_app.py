def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert "uptime_seconds" in data
    assert "version" in data


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "python_info" in response.text


def test_create_note(client):
    response = client.post(
        "/api/notes/",
        json={"title": "Test Note", "content": "This is a test note content"},
    )
    with open("debug_test.log", "w") as f:
        f.write(f"Status: {response.status_code}\n")
        f.write(f"Body: {response.text}\n")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note content"
    assert data["version"] == 1
    assert "id" in data


def test_get_notes(client):
    # Create a note first
    client.post("/api/notes/", json={"title": "Test Note", "content": "Test content"})

    response = client.get("/api/notes/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Note"


def test_search_notes(client):
    # Create notes
    client.post("/api/notes/", json={"title": "Apple", "content": "Fruit"})
    client.post("/api/notes/", json={"title": "Banana", "content": "Yellow fruit"})
    client.post("/api/notes/", json={"title": "Carrot", "content": "Vegetable"})

    # Search for "fruit"
    response = client.get("/api/notes/?search=fruit")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = [note["title"] for note in data]
    assert "Apple" in titles
    assert "Banana" in titles
    assert "Carrot" not in titles


def test_get_specific_note(client):
    create_response = client.post(
        "/api/notes/", json={"title": "Specific Note", "content": "Specific content"}
    )
    note_id = create_response.json()["id"]

    response = client.get(f"/api/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Specific Note"


def test_update_note(client):
    create_response = client.post(
        "/api/notes/", json={"title": "Original", "content": "Content"}
    )
    note_id = create_response.json()["id"]

    response = client.put(
        f"/api/notes/{note_id}", json={"title": "Updated", "content": "New Content"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["version"] == 2


def test_delete_note(client):
    create_response = client.post(
        "/api/notes/", json={"title": "Delete Me", "content": "Content"}
    )
    note_id = create_response.json()["id"]

    response = client.delete(f"/api/notes/{note_id}")
    assert response.status_code == 200

    get_response = client.get(f"/api/notes/{note_id}")
    assert get_response.status_code == 404


def test_version_history_and_restore(client):
    # 1. Create note (v1)
    create_res = client.post("/api/notes/", json={"title": "v1", "content": "c1"})
    note_id = create_res.json()["id"]

    # 2. Update note (v2)
    client.put(f"/api/notes/{note_id}", json={"title": "v2", "content": "c2"})

    # 3. Get versions
    versions_res = client.get(f"/api/notes/{note_id}/versions")
    versions = versions_res.json()
    assert len(versions) == 2

    # Find v1 id
    v1_id = next(v["id"] for v in versions if v["version"] == 1)

    # 4. Restore v1
    restore_res = client.post(f"/api/notes/{note_id}/restore/{v1_id}")
    assert restore_res.status_code == 200
    data = restore_res.json()
    assert data["title"] == "v1"
    assert data["content"] == "c1"
    assert data["version"] == 3
