import pytest
from django.contrib.auth import get_user_model


# User related Tests
@pytest.mark.django_db
def test_get_user_by_id(authenticated_user, user_data):
    user_model = get_user_model()
    user = user_model.objects.get(username=user_data["username"])
    resp = authenticated_user.get(f"/apis/users/{user.id}/")
    data = resp.data

    assert data["username"] == user_data["username"]
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert data["email"] == user_data["email"]
    assert resp.status_code == 200
    assert data["id"]


@pytest.mark.django_db
def test_get_user_list(authenticated_user):
    resp = authenticated_user.get("/apis/users/")
    data = resp.data

    assert list(data)
    assert len(data) == 1
    assert resp.status_code == 200


# Registeration related Tests
@pytest.mark.django_db
def test_register_user(authenticated_superuser, user_data):
    resp = authenticated_superuser.post("/auth/register/", user_data)
    data = resp.data

    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert data["email"] == user_data["email"]
    assert data["is_active"]
    assert resp.status_code == 200


@pytest.mark.django_db
def test_register_user_failure_email_exist(authenticated_superuser, create_test_user, user_data):
    resp = authenticated_superuser.post("/auth/register/", user_data)
    data = resp.data

    assert resp.status_code == 400


@pytest.mark.django_db
def test_register_user_failure_characters(authenticated_superuser, user_data):
    user_data["password"] = "Test@12"  # password less than 8 characters.
    resp = authenticated_superuser.post("/auth/register/", user_data)
    data = resp.data

    assert resp.status_code == 412
    assert data["errors"]


@pytest.mark.django_db
def test_register_user_failure_special_character(authenticated_superuser, user_data):
    user_data["password"] = "Test1234"  # password without a special character.
    resp = authenticated_superuser.post("/auth/register/", user_data)
    data = resp.data

    assert resp.status_code == 412
    assert data["errors"]


@pytest.mark.django_db
def test_register_user_failure_numeric_character(authenticated_superuser, user_data):
    user_data["password"] = "Testpass!@"  # password without a numeric character.
    resp = authenticated_superuser.post("/auth/register/", user_data)
    data = resp.data

    assert resp.status_code == 412
    assert data["errors"]


@pytest.mark.django_db
def test_register_user_failure_no_email(authenticated_superuser, user_data):
    del user_data["email"]
    resp = authenticated_superuser.post("/auth/register/", user_data)
    data = resp.data

    assert resp.status_code == 400
    assert data["errors"]


@pytest.mark.django_db
def test_register_user_failure_no_password(authenticated_superuser, user_data):
    del user_data["password"]
    resp = authenticated_superuser.post("/auth/register/", user_data)
    data = resp.data

    assert resp.status_code == 400
    assert data["errors"]


@pytest.mark.django_db
def test_register_user_failure_invalid_email(authenticated_superuser, user_data):
    user_data["email"] = "invalidemail"
    resp = authenticated_superuser.post("/auth/register/", user_data)
    data = resp.data

    assert resp.status_code == 400
    assert data["errors"]


# Login related Tests
@pytest.mark.django_db
def test_login_user(client, create_test_user, user_data):
    resp = client.post("/auth/login/", user_data)
    data = resp.data
    token = data["token"]
    user = data["user"]

    assert token["access"]
    assert token["refresh"]

    assert user["first_name"] == user_data["first_name"]
    assert user["last_name"] == user_data["last_name"]
    assert user["email"] == user_data["email"]
    assert user["is_active"]
    assert resp.status_code == 200


@pytest.mark.django_db
def test_login_failure_wrong_password(client, create_test_user, user_data):
    user_data["password"] = "somewrongpassword"
    resp = client.post("/auth/login/", user_data)
    data = resp.data

    assert resp.status_code == 401
    assert data["errors"]


@pytest.mark.django_db
def test_login_failure_wrong_username(client, create_test_user, user_data):
    user_data["username"] = "someusername"
    resp = client.post("/auth/login/", user_data)
    data = resp.data

    assert resp.status_code == 401
    assert data["errors"]


@pytest.mark.django_db
def test_login_failure_no_password(client, create_test_user, user_data):
    del user_data["password"]
    resp = client.post("/auth/login/", user_data)
    data = resp.data

    assert resp.status_code == 400
    assert data["errors"]


@pytest.mark.django_db
def test_login_failure_no_username(client, create_test_user, user_data):
    del user_data["username"]
    resp = client.post("/auth/login/", user_data)
    data = resp.data

    assert resp.status_code == 400
    assert data["errors"]
