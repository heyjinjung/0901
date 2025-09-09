from fastapi import status


def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == status.HTTP_200_OK


def test_docs_available(client):
    r = client.get("/docs")
    assert r.status_code in (status.HTTP_200_OK, status.HTTP_307_TEMPORARY_REDIRECT)
