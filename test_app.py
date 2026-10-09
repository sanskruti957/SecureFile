
import io
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_encrypt_page(client):
    response = client.get("/encrypt")
    assert response.status_code == 200


def test_decrypt_page(client):
    response = client.get("/decrypt")
    assert response.status_code == 200


def test_encrypt_without_file(client):
    response = client.post(
        "/encrypt",
        data={"password": "test123"}
    )

    assert response.status_code == 200
    assert b"Please select a file." in response.data


def test_encrypt_without_password(client):
    response = client.post(
        "/encrypt",
        data={
            "file": (io.BytesIO(b"hello"), "hello.txt"),
            "password": ""
        }
    )

    assert response.status_code == 200
    assert b"Please enter a password." in response.data


def test_upload_size_limit(client):
    large_data = b"A" * (11 * 1024 * 1024)

    response = client.post(
        "/encrypt",
        data={
            "file": (io.BytesIO(large_data), "large.txt"),
            "password": "test123"
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 413
    