from fastapi.testclient import TestClient

from demo.app import app
from demo.database import get_session
from demo.database import Base
from demo.database import Account
from tests.database import Session
from tests.database import get_session as get_test_session
from tests.database import engine


client = TestClient(app)


def test_get_account():
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_session] = get_test_session
    url = '/get-account/1'

    with Session() as session:
        session.add(
            Account(
                email='test',
                username='test123',
                password='qwerty',
            )
        )
        session.commit()

    response = client.get(url)
    response_json = response.json()

    assert response.status_code == 200
    assert response_json['id'] == 1
