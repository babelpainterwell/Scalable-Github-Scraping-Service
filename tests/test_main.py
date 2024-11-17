from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

fake_db = {

}

def test_read_item():
    response = client.get("/items/foo")
    assert response.status_code == 200
    assert response.json() == {"item_id": "foo", "name": "Fighters", "description": "Fighters are great!"}



# TEST CASES FOR /users/{username}/projects

"""
1. User exists in the database with perojects.
- status code should be 200
- response should be the list of projects
"""

"""
2. User exists in the database with no projects.
- status code should be 200
- response should be an empty list
"""

"""
3. User does not exist in the database but exists on Github with projects.
- status code should be 200
- response should be the list of projects
- user should be added to the database
- projects should be added to the database
"""

"""
4. User does not exist in the database but exists on Github with no projects.
- status code should be 200
- response should be an empty list
- user should be added to the database
"""


"""
5. User does not exist in the database and does not exist on Github.
- status code should be 404
- response should be {"detail": "Resource not found."}
"""

"""
6. GitHub API fails (eg. rate limit exceeded).
- simulate a falure in the external API and raise ExternalAPIError and returns 503
"""


# TEST CASES FOR /users/recent/{n}

"""
1. There are n users in the database.
- status code should be 200
- response should be the list of users
"""

"""
2. There are fewer than n users in the database.
- status code should be 200
- response should be the list of users
"""

"""
3. There are no users in the database.
- status code should be 200
- response should be an empty list
"""



# TEST CASES FOR /projects/most-starred/{n}

"""
1. There are n projects in the database.
- status code should be 200
- response should be the list of projects
"""

"""
2. There are fewer than n projects in the database.
- status code should be 200
- response should be the list of projects
"""

"""
3. There are no projects in the database.
- status code should be 200
- response should be an empty list
"""



# TEST CASES FOR database errors


"""
1. Database error (including different scenarios)
a. user repository error in get_by_username
b. user repository error in create
c. user repository integrity error in create
d. user repository error in get_most_recent
e. unexpected user repository error occurred
f. project repository error in get_by_user_id
g. project repository error in create
h. project repository error in get_most_recent
i. unexpected project repository error occurred
- status code should be 500
- response should be {"detail": "Internal server error."}
"""

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


# TEST CASES FOR unexpected errors

"""
1. Unexpected error occurred in the service.
- status code should be 500
- response should be {"detail": "An unexpected error occurred."}
"""








