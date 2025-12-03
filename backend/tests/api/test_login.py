from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core import security
from app.models.user import User

client = TestClient(app)

def create_user(db: Session, username: str, role: str = "admin", is_active: bool = True) -> User:
    password = "password"
    hashed_password = security.get_password_hash(password)
    user = User(username=username, hashed_password=hashed_password, role=role, is_active=is_active)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_token_headers(client: TestClient, username: str, password: str = "password") -> dict:
    response = client.post(
        "/api/login/access-token",
        data={"username": username, "password": password}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_login_access_token(db: Session):
    create_user(db, "testadmin", "admin")
    response = client.post(
        "/api/login/access-token",
        data={"username": "testadmin", "password": "password"}
    )
    assert response.status_code == 200
    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"

def test_login_wrong_password(db: Session):
    create_user(db, "testuser", "admin")
    response = client.post(
        "/api/login/access-token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_inactive_user(db: Session):
    create_user(db, "inactive", "admin", is_active=False)
    response = client.post(
        "/api/login/access-token",
        data={"username": "inactive", "password": "password"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user"

def test_read_users_me(db: Session):
    create_user(db, "me", "admin")
    headers = get_token_headers(client, "me")
    response = client.get("/api/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "me"
    assert data["role"] == "admin"

def test_admin_delete_data(db: Session):
    create_user(db, "realadmin", "admin")
    headers = get_token_headers(client, "realadmin")
    response = client.delete("/api/admin/data", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "All data deleted successfully"

def test_shangu_delete_data_forbidden(db: Session):
    create_user(db, "operator", "shangu")
    headers = get_token_headers(client, "operator")
    response = client.delete("/api/admin/data", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"
