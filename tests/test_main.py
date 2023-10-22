from app.app import app
from app import models
from fastapi.testclient import TestClient
import pytest
import httpx
from dotenv import dotenv_values
import os
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

config = {**dotenv_values(".env"), **os.environ}
MYSQL_USER = config["MYSQL_USER"]
MYSQL_PASSWORD = config["MYSQL_PASSWORD"]
MYSQL_HOST = config["MYSQL_HOST"]
MYSQL_PORT = config["MYSQL_PORT"]
MYSQL_DBNAME = config["MYSQL_DBNAME"]

engine = create_async_engine(
    f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DBNAME}"
)
SessionLocal = async_sessionmaker(engine)


@pytest.fixture(scope="session")
def get_client():
    with TestClient(app) as client:
        response: httpx.Response = client.post(
            "/token", data={"username": "root", "password": "123"}
        )
        client.headers = {
            "Authorization": f"Bearer {(response.json())['access_token']}"
        }
        yield client


class TestUsers:
    @pytest.fixture(autouse=True)
    def get_client(self, get_client):
        self.client: TestClient = get_client

    def test_get_users(self):
        response: httpx.Response = self.client.get("/users/")
        assert response.status_code == 200
        assert response.json() == [
            {"name": "root", "permission": 0, "id": 1, "email": None}
        ]

    def test_send_email(self):
        response: httpx.Response = self.client.post(
            "/sendEmail", json={"option": "BIND", "email": "llleigoing@outlook.com"}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "SUCCESS"}

    def test_bind_email_with_wrong_token(self):
        response: httpx.Response = self.client.put(
            "/users/1",
            json={"email": "llleigoing@outlook.com"},
            headers={"email-token": "123456"},
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Wrong email token"}

    @pytest.mark.asyncio
    async def test_bind_email(self):
        async with SessionLocal() as db:
            token = (await db.scalars(select(models.Confirmation))).first().token
        print(token)
        response: httpx.Response = self.client.put(
            "/users/1",
            json={"email": "llleigoing@outlook.com"},
            headers={"email-token": f"{token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "name": "root",
            "permission": 0,
            "id": 1,
            "email": "llleigoing@outlook.com",
        }

    def test_post_user(self):
        response: httpx.Response = self.client.post(
            "/users/",
            json={"name": "admin", "permission": 1, "password": "123"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "name": "admin",
            "permission": 1,
            "id": 2,
            "email": None,
        }

    def test_get_user(self):
        response: httpx.Response = self.client.get("/users/2")
        assert response.status_code == 200
        assert response.json() == {
            "name": "admin",
            "permission": 1,
            "id": 2,
            "email": None,
        }

    def test_put_user(self):
        response: httpx.Response = self.client.put("/users/2", json={"name": "admin1"})
        assert response.status_code == 200
        assert response.json() == {
            "name": "admin1",
            "permission": 1,
            "id": 2,
            "email": None,
        }

    def test_delete_user(self):
        response: httpx.Response = self.client.delete("/users/2")
        assert response.status_code == 200
        assert response.json() == {"detail": "SUCCESS"}


class TestProblems:
    @pytest.fixture(autouse=True)
    def get_client(self, get_client):
        self.client: TestClient = get_client

    def test_post_problem(self):
        response: httpx.Response = self.client.post(
            "/problems/",
            json={
                "name": "que1",
                "description": "que1",
                "answer": "123",
                "score_initial": 1000,
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "name": "que1",
            "description": "que1",
            "answer": "123",
            "score_initial": 1000,
            "score_now": 1000,
            "owner_id": 1,
            "id": 1,
        }

    def test_post_problem(self):
        response: httpx.Response = self.client.post(
            "/problems/",
            json={
                "name": "que1",
                "description": "que1",
                "answer": "123",
                "score_initial": 1000,
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "name": "que1",
            "description": "que1",
            "answer": "123",
            "score_initial": 1000,
            "score_now": 1000,
            "owner_id": 1,
            "id": 1,
        }

    def test_get_problems(self):
        response: httpx.Response = self.client.get("/problems/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "name": "que1",
                "description": "que1",
                "answer": "123",
                "score_initial": 1000,
                "score_now": 1000,
                "owner_id": 1,
                "id": 1,
            }
        ]

    def test_put_problem(self):
        response: httpx.Response = self.client.put(
            "/problems/1", json={"description": "a question"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "name": "que1",
            "description": "a question",
            "answer": "123",
            "score_initial": 1000,
            "score_now": 1000,
            "owner_id": 1,
            "id": 1,
        }

    def test_get_problem(self):
        response: httpx.Response = self.client.get("/problems/1")
        assert response.status_code == 200
        assert response.json() == {
            "name": "que1",
            "description": "a question",
            "answer": "123",
            "score_initial": 1000,
            "score_now": 1000,
            "owner_id": 1,
            "id": 1,
        }

    def test_delete_problem(self):
        response: httpx.Response = self.client.delete("/problems/1")
        assert response.status_code == 200
        assert response.json() == {"detail": "SUCCESS"}


class TestOthers:
    @pytest.fixture(autouse=True)
    def get_client(self, get_client):
        self.client: TestClient = get_client

    def test_get_me(self):
        response: httpx.Response = self.client.get("/me")
        assert response.status_code == 200
        assert response.json() == {
            "name": "root",
            "permission": 0,
            "id": 1,
            "email": "llleigoing@outlook.com",
        }

    def test_answer_wrong(self):
        response: httpx.Response = self.client.post(
            "/problems/",
            json={
                "name": "que1",
                "description": "que1",
                "answer": "123",
                "score_initial": 1000,
            },
        )
        response: httpx.Response = self.client.post(
            "/users/1/problems/2", json={"answer": "45"}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "WRONG"}

    def test_answer_accepted(self):
        response: httpx.Response = self.client.post(
            "/users/1/problems/2", json={"answer": "123"}
        )
        assert response.status_code == 200
        assert response.json() == {"detail": "ACCEPTED"}

    def test_get_rank(self):
        response: httpx.Response = self.client.get("/users/rank")
        assert response.status_code == 200
        assert response.json() == [{"id": 1, "name": "root", "total_score": 900}]
