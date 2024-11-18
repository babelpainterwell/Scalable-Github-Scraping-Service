# tests/test_main.py

import pytest
from app.main import app
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.models import User, Project
from app.data_access.repositories.user_repository import UserRepository
from app.data_access.repositories.project_repository import ProjectRepository
from app.external_services.github_api import GitHubAPIClient
from app.core.exceptions import NotFoundError, DatabaseError, ExternalAPIError
from datetime import datetime, timezone
from app.services.user_service import Service
from sqlalchemy.exc import SQLAlchemyError
from app.data_access.database import async_session


transport = ASGITransport(app=app)


# TEST CASES FOR /users/{username}/projects

"""
1. User exists in the database with perojects.
- status code should be 200
- response should be the list of projects
"""

@pytest.mark.asyncio
async def test_user_in_db_with_projects(mocker):
    username = "existing-user"  # Updated username without underscore
    projects = [
        Project(id=1, name="Project1", description="Test project 1", stars=10, forks=2, user_id=1),
        Project(id=2, name="Project2", description="Test project 2", stars=5, forks=1, user_id=1),
    ]
    mock_get_user = mocker.AsyncMock(return_value=User(id=1, username=username))
    mock_get_projects = mocker.AsyncMock(return_value=projects)

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(ProjectRepository, 'get_by_user_id', mock_get_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 200, f"Response content: {response.content}"
    assert response.json() == [project.model_dump(mode="json") for project in projects]



"""
2. User exists in the database with no projects.
- status code should be 200
- response should be an empty list
"""

@pytest.mark.asyncio
async def test_user_in_db_no_projects(mocker):
    username = "user-no-projects"  

    mock_get_user = mocker.AsyncMock(return_value=User(id=2, username=username))
    mock_get_projects = mocker.AsyncMock(return_value=[])

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(ProjectRepository, 'get_by_user_id', mock_get_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 200, f"Response content: {response.content}"
    assert response.json() == []




"""
3. User does not exist in the database but exists on Github with projects.
- status code should be 200
- response should be the list of projects
- user should be added to the database
- projects should be added to the database
"""

@pytest.mark.asyncio
async def test_user_not_in_db_exists_on_github_with_projects(mocker):
    username = "github-user-with-projects" 
    github_projects = [
        {
            "name": "GitHubProject1",
            "description": "GitHub test project 1",
            "stargazers_count": 15,
            "forks_count": 3,
        },
        {
            "name": "GitHubProject2",
            "description": "GitHub test project 2",
            "stargazers_count": 7,
            "forks_count": 1,
        }
    ]
    projects = [
        Project(id=1, name="GitHubProject1", description="GitHub test project 1", stars=15, forks=3, user_id=1),
        Project(id=2, name="GitHubProject2", description="GitHub test project 2", stars=7, forks=1, user_id=1),
    ]

    mock_get_user = mocker.AsyncMock(return_value=None)
    mock_fetch_projects = mocker.AsyncMock(return_value=github_projects)
    mock_create_user = mocker.AsyncMock(return_value=User(id=1, username=username))
    mock_create_projects = mocker.AsyncMock(return_value=projects)

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(GitHubAPIClient, 'fetch_user_projects', mock_fetch_projects)
    mocker.patch.object(UserRepository, 'create', mock_create_user)
    mocker.patch.object(ProjectRepository, 'create_projects', mock_create_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 200, f"Response content: {response.content}"
    assert response.json() == [project.model_dump(mode="json") for project in projects]



"""
4. User does not exist in the database but exists on Github with no projects.
- status code should be 200
- response should be an empty list
- user should be added to the database
"""

@pytest.mark.asyncio
async def test_user_not_in_db_exists_on_github_no_projects(mocker):
    username = "github-user-no-projects" 

    mock_get_user = mocker.AsyncMock(return_value=None)
    mock_fetch_projects = mocker.AsyncMock(return_value=[])
    mock_create_user = mocker.AsyncMock(return_value=User(id=1, username=username))
    mock_create_projects = mocker.AsyncMock(return_value=[])

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(GitHubAPIClient, 'fetch_user_projects', mock_fetch_projects)
    mocker.patch.object(UserRepository, 'create', mock_create_user)
    mocker.patch.object(ProjectRepository, 'create_projects', mock_create_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 200, f"Response content: {response.content}"
    assert response.json() == []


"""
5. User does not exist in the database and does not exist on Github.
- status code should be 404
- response should be {"detail": "Resource not found."}
"""
@pytest.mark.asyncio
async def test_user_not_in_db_not_on_github(mocker):
    username = "nonexistent-user" 

    mock_get_user = mocker.AsyncMock(return_value=None)
    mock_fetch_projects = mocker.AsyncMock(side_effect=NotFoundError(f"User '{username}' not found on GitHub."))

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(GitHubAPIClient, 'fetch_user_projects', mock_fetch_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 404, f"Response content: {response.content}"
    assert response.json() == {"detail": "Resource not found."}



"""
6. GitHub API fails (eg. rate limit exceeded).
- simulate a falure in the external API and raise ExternalAPIError and returns 503
"""

@pytest.mark.asyncio
async def test_github_api_failure(mocker):
    """
    - test user shouldn't exist in the database, but exists on GitHub
    """
    username = "any-user"

    mock_get_user = mocker.AsyncMock(return_value=None)
    mock_fetch_projects = mocker.AsyncMock(side_effect=ExternalAPIError("GitHub API rate limit exceeded"))

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(GitHubAPIClient, 'fetch_user_projects', mock_fetch_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 503, f"Response content: {response.content}"
    assert response.json() == {"detail": "External API error."}



# TEST CASES FOR /users/recent/{n}

"""
1. There are n users in the database.
- status code should be 200
- response should be the list of users
"""

@pytest.mark.asyncio
async def test_get_recent_users_exact_n(mocker):
    n = 3
    # add created_at field to the User model
    users = [
        User(id=1, username="user1", created_at=datetime.now(timezone.utc)),
        User(id=2, username="user2", created_at=datetime.now(timezone.utc)),
        User(id=3, username="user3", created_at=datetime.now(timezone.utc)),
    ]

    mock_get_recent_users = mocker.AsyncMock(return_value=users)

    mocker.patch.object(UserRepository, 'get_most_recent', mock_get_recent_users)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/recent/{n}")

    assert response.status_code == 200, f"Response content: {response.content}"
    # convert expected data to match response format
    # compare the response JSON to the serialized expected data
    expected_data = [user.model_dump(mode="json") for user in users]
    assert response.json() == expected_data


"""
2. There are fewer than n users in the database.
- status code should be 200
- response should be the list of users
"""

@pytest.mark.asyncio
async def test_get_recent_users_fewer_than_n(mocker):
    n = 5
    users = [
        User(id=1, username="user1", created_at=datetime.now(timezone.utc)),
        User(id=2, username="user2", created_at=datetime.now(timezone.utc)),
    ]

    mock_get_recent_users = mocker.AsyncMock(return_value=users)

    mocker.patch.object(UserRepository, 'get_most_recent', mock_get_recent_users)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/recent/{n}")

    assert response.status_code == 200, f"Response content: {response.content}"
    expected_data = [user.model_dump(mode="json") for user in users]
    assert response.json() == expected_data


"""
3. There are no users in the database.
- status code should be 200
- response should be an empty list
"""

@pytest.mark.asyncio
async def test_get_recent_users_no_users(mocker):
    n = 5

    mock_get_recent_users = mocker.AsyncMock(return_value=[])

    mocker.patch.object(UserRepository, 'get_most_recent', mock_get_recent_users)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/recent/{n}")

    assert response.status_code == 200, f"Response content: {response.content}"
    assert response.json() == []




# TEST CASES FOR /projects/most-starred/{n}

"""
1. There are n projects in the database.
- status code should be 200
- response should be the list of projects
"""

@pytest.mark.asyncio
async def test_get_most_starred_projects_exact_n(mocker):
    n = 2
    projects = [
        Project(id=1, name="Project1", description="Desc1", stars=100, forks=10, user_id=1),
        Project(id=2, name="Project2", description="Desc2", stars=80, forks=5, user_id=2),
    ]

    mock_get_projects = mocker.AsyncMock(return_value=projects)

    mocker.patch.object(ProjectRepository, 'get_most_starred', mock_get_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/projects/most-starred/{n}")

    assert response.status_code == 200, f"Response content: {response.content}"
    assert response.json() == [project.model_dump(mode="json") for project in projects]


"""
2. There are fewer than n projects in the database.
- status code should be 200
- response should be the list of projects
"""

@pytest.mark.asyncio
async def test_get_most_starred_projects_fewer_than_n(mocker):
    n = 5
    projects = [
        Project(id=1, name="Project1", description="Desc1", stars=100, forks=10, user_id=1),
    ]

    mock_get_projects = mocker.AsyncMock(return_value=projects)

    mocker.patch.object(ProjectRepository, 'get_most_starred', mock_get_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/projects/most-starred/{n}")

    assert response.status_code == 200, f"Response content: {response.content}"
    assert response.json() == [project.model_dump(mode="json") for project in projects]


"""
3. There are no projects in the database.
- status code should be 200
- response should be an empty list
"""

@pytest.mark.asyncio
async def test_get_most_starred_projects_no_projects(mocker):
    n = 5

    mock_get_projects = mocker.AsyncMock(return_value=[])

    mocker.patch.object(ProjectRepository, 'get_most_starred', mock_get_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/projects/most-starred/{n}")

    assert response.status_code == 200, f"Response content: {response.content}"
    assert response.json() == []



# TEST CASES FOR database errors


"""
1. Database error (including different scenarios)
a. user repository error in get_by_username
b. user repository error in create
c. user repository integrity error in create
d. user repository error in get_most_recent
e. unexpected user repository error occurred (three of them)
f. project repository error in get_by_user_id
g. project repository error in create
h. project repository error in get_most_recent
i. unexpected project repository error occurred (three of them)
- status code should be 500
- response should be {"detail": "Database server error."}
"""

@pytest.mark.asyncio
async def test_database_error_get_by_username(mocker):
    username = "any-user"

    mock_get_user = mocker.AsyncMock(side_effect=DatabaseError("Simulated database error in get_by_username"))

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "Database server error."}

@pytest.mark.asyncio
async def test_database_error_create_user(mocker):
    username = "new-user"

    mock_get_user = mocker.AsyncMock(return_value=None)
    mock_fetch_projects = mocker.AsyncMock(return_value=[])
    mock_create_user = mocker.AsyncMock(side_effect=DatabaseError("Simulated database error in create"))

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(GitHubAPIClient, 'fetch_user_projects', mock_fetch_projects)
    mocker.patch.object(UserRepository, 'create', mock_create_user)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "Database server error."}

@pytest.mark.asyncio
async def test_integrity_error_create_user(mocker):
    username = "duplicate-user"

    mock_get_user = mocker.AsyncMock(return_value=None)
    mock_fetch_projects = mocker.AsyncMock(return_value=[])
    mock_create_user = mocker.AsyncMock(side_effect=DatabaseError("User already exists."))

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(GitHubAPIClient, 'fetch_user_projects', mock_fetch_projects)
    mocker.patch.object(UserRepository, 'create', mock_create_user)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "Database server error."}

@pytest.mark.asyncio
async def test_database_error_get_most_recent(mocker):
    n = 5

    mock_get_recent_users = mocker.AsyncMock(side_effect=DatabaseError("Simulated database error in get_most_recent"))

    mocker.patch.object(UserRepository, 'get_most_recent', mock_get_recent_users)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/recent/{n}")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "Database server error."}


@pytest.mark.asyncio
async def test_database_error_get_by_user_id(mocker):
    username = "existing-user"

    mock_get_user = mocker.AsyncMock(return_value=User(id=1, username=username))
    mock_get_projects = mocker.AsyncMock(side_effect=DatabaseError("Simulated database error in get_by_user_id"))

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(ProjectRepository, 'get_by_user_id', mock_get_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "Database server error."}


@pytest.mark.asyncio
async def test_database_error_create_projects(mocker):
    username = "new-user-with-projects"
    github_projects = [
        {
            "name": "GitHubProject1",
            "description": "GitHub test project 1",
            "stargazers_count": 15,
            "forks_count": 3,
        }
    ]

    mock_get_user = mocker.AsyncMock(return_value=None)
    mock_fetch_projects = mocker.AsyncMock(return_value=github_projects)
    mock_create_user = mocker.AsyncMock(return_value=User(id=1, username=username))
    mock_create_projects = mocker.AsyncMock(side_effect=DatabaseError("Simulated database error in create_projects"))

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
    mocker.patch.object(GitHubAPIClient, 'fetch_user_projects', mock_fetch_projects)
    mocker.patch.object(UserRepository, 'create', mock_create_user)
    mocker.patch.object(ProjectRepository, 'create_projects', mock_create_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "Database server error."}


@pytest.mark.asyncio
async def test_database_error_get_most_starred(mocker):
    n = 5

    mock_get_projects = mocker.AsyncMock(side_effect=DatabaseError("Simulated database error in get_most_starred"))

    mocker.patch.object(ProjectRepository, 'get_most_starred', mock_get_projects)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/projects/most-starred/{n}")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "Database server error."}




# @pytest.mark.asyncio
# async def test_unexpected_error_in_user_repository(mocker):
#     username = "any-user"

#     # the way the exception is being mocked causes it to bypass the exception handling within the repository method
#     mock_get_user = mocker.AsyncMock(side_effect=Exception("Unexpected error in get_by_username"))

#     mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)

#     async with AsyncClient(transport=transport, base_url="http://test") as ac:
#         response = await ac.get(f"/users/{username}/projects")

#     assert response.status_code == 500, f"Response content: {response.content}"
#     assert response.json() == {"detail": "Database server error."}


# @pytest.mark.asyncio
# async def test_unexpected_error_in_project_repository(mocker):
#     username = "existing-user"

#     mock_get_user = mocker.AsyncMock(return_value=User(id=1, username=username))
#     mock_get_projects = mocker.AsyncMock(side_effect=Exception("Unexpected error in get_by_user_id"))

#     mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)
#     mocker.patch.object(ProjectRepository, 'get_by_user_id', mock_get_projects)

#     async with AsyncClient(transport=transport, base_url="http://test") as ac:
#         response = await ac.get(f"/users/{username}/projects")

#     # Since the exception should be converted to a DatabaseError, we expect a 500 status code and Database server error message
#     assert response.status_code == 500, f"Response content: {response.content}"
#     assert response.json() == {"detail": "Database server error."}


"""
To mock an unexpected error (General exception) in the data_access layer, 
we need to mock the the internal function within each repository method so that 
the exception can be caught to raise a DatabaseError.
"""

# THE CODE BELOW FOR MOCKING UNEXPECTED ERRORS IN THE DATA_ACCESS LAYER IS GENERATED BY CHATGPT.
# THE CODE BELOW FOR MOCKING UNEXPECTED ERRORS IN THE DATA_ACCESS LAYER IS GENERATED BY CHATGPT.
# THE CODE BELOW FOR MOCKING UNEXPECTED ERRORS IN THE DATA_ACCESS LAYER IS GENERATED BY CHATGPT.


@pytest.mark.asyncio
async def test_unexpected_error_in_user_repository(mocker):
    username = "any-user"

    # Mock the session.execute method to raise an exception within get_by_username
    async def mock_execute(*args, **kwargs):
        raise SQLAlchemyError("Unexpected error in session.execute")

    # Create a mock session that uses the mocked execute
    class MockSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def execute(self, *args, **kwargs):
            await mock_execute(*args, **kwargs)

        async def refresh(self, *args, **kwargs):
            pass

    # Define a function that returns an instance of MockSession
    async def mock_async_session():
        return MockSession()

    # Patch the async_session to return the mock session when called
    mocker.patch('app.data_access.repositories.user_repository.async_session', new=mock_async_session)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "Database server error."}


@pytest.mark.asyncio
async def test_unexpected_error_in_project_repository(mocker):
    username = "existing-user"

    mock_get_user = mocker.AsyncMock(return_value=User(id=1, username=username))

    # Mock the session.execute method to raise an exception within get_by_user_id
    async def mock_execute(*args, **kwargs):
        raise SQLAlchemyError("Unexpected error in session.execute")

    # Create a mock session that uses the mocked execute
    class MockSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def execute(self, *args, **kwargs):
            await mock_execute(*args, **kwargs)

    # Define a function that returns an instance of MockSession
    async def mock_async_session():
        return MockSession()

    # Patch the async_session to return the mock session when called
    mocker.patch('app.data_access.repositories.project_repository.async_session', new=mock_async_session)

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_user)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "Database server error."}















# TEST CASES FOR input validation
# FastAPI has a built-in exception handler for RequestValidationError
"""
1. API input validation (including different scenarios)
a. username is empty for /users/{username}/projects
b. username is too long for /users/{username}/projects
c. username contains invalid characters for /users/{username}/projects
d. n is negative for /users/recent/{n}
e. n is too large for /users/recent/{n}
f. n is negative for /projects/most-starred/{n}
g. n is too large for /projects/most-starred/{n}
- status code should be 422
"""

# the route is not matched, leading to a 404 response in fastapi
@pytest.mark.asyncio
async def test_username_empty():
    username = ""

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 404, f"Response content: {response.content}"
    assert response.json() == {"detail": "Not Found"}

@pytest.mark.asyncio
async def test_username_too_long():
    username = "a"*40  

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 422, f"Response content: {response.content}"


@pytest.mark.asyncio
async def test_username_invalid_characters():
    username = "invalid_user!"  

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 422, f"Response content: {response.content}"


@pytest.mark.asyncio
async def test_negative_n_users_recent():
    n = -1

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/recent/{n}")

    assert response.status_code == 422, f"Response content: {response.content}"

@pytest.mark.asyncio
async def test_n_too_large_users_recent():
    n = 101

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/recent/{n}")

    assert response.status_code == 422, f"Response content: {response.content}"

@pytest.mark.asyncio
async def test_negative_n_projects_most_starred():
    n = -1

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/projects/most-starred/{n}")

    assert response.status_code == 422, f"Response content: {response.content}"

@pytest.mark.asyncio
async def test_n_too_large_projects_most_starred():
    n = 101

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/projects/most-starred/{n}")

    assert response.status_code == 422, f"Response content: {response.content}"




# TEST CASES FOR unexpected errors

"""
1. Unexpected error occurred in the service.
- status code should be 500
- response should be {"detail": "An unexpected error occurred."}

Do Not Mock the Entire Service Method: 
Instead, simulate the exception within a method called by get_user_projects_service.
"""

@pytest.mark.asyncio
async def test_unexpected_get_user_projects_service_error(mocker):
    username = "any-user"

    # Mock a method called within get_user_projects_service to raise an exception
    mock_get_by_username = mocker.AsyncMock(side_effect=Exception("Unexpected error in service"))

    mocker.patch.object(UserRepository, 'get_by_username', mock_get_by_username)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/{username}/projects")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "An unexpected error occurred."}


@pytest.mark.asyncio
async def test_unexpected_get_most_recent_users_service_error(mocker):
    n = 5
    mock_get_most_recent = mocker.AsyncMock(side_effect=Exception("Unexpected error in service"))

    mocker.patch.object(UserRepository, 'get_most_recent', mock_get_most_recent)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/users/recent/{n}")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "An unexpected error occurred."}

@pytest.mark.asyncio
async def test_unexpected_get_most_starred_projects_service_error(mocker):
    n = 5
    mock_get_most_starred = mocker.AsyncMock(side_effect=Exception("Unexpected error in service"))

    mocker.patch.object(ProjectRepository, 'get_most_starred', mock_get_most_starred)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/projects/most-starred/{n}")

    assert response.status_code == 500, f"Response content: {response.content}"
    assert response.json() == {"detail": "An unexpected error occurred."}










