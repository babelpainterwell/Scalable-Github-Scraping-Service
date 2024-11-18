# Scalable-Github-Scraping-Service

**_A scalable system to scrape GitHub data, store it in a database, and provide a RESTful interface and CLI tool for querying repository information._**

###### Keywords

FASTapi, Pydantic, Error handiling, Unit/Integration Test, Asynchrounous Architecture Design, logging, auto-scaling if possible

---

### To get started

##### Using the Command-Line Tool

To interact with the RESTful API through the command-line tool, follow these steps:

1. **Activate the Poetry Shell:**
   Ensure you have Poetry installed. Navigate to your project directory and activate the virtual environment using:

   ```bash
    poetry install
    poetry shell
   ```

   This command activates the virtual environment managed by Poetry, ensuring all dependencies are correctly loaded.

2. **Run the CLI Tool:**

   Available Commands:

   - Retrieve User Projects - To retrieve and display projects for a given GitHub username
     ```bash
     python cli.py get-user-projects <username>
     ```
   - Get N Most Recent Users - Return N most recent users saved in the database
     ```bash
     python cli.py get-recent-users [N]
     ```
     **Example:** To get the 5 most recent users saved in the database:
     ```bash
      python cli.py get-recent-users 5
     ```
   - Retrieve N Most Starred Projects - Return N most starred projects saved in the database

     ```bash
     python cli.py get-most-starred-projects [N]
     ```

     **Example:** To get the 10 most starred projects saved in the database:

     ```bash
      python cli.py get-most-starred-projects 10
     ```

     **Note:** The optional argument `[N]` is the number of users or projects to retrieve. If not provided, the default value is 5.
     <br>

     **Example:** To get the projects for the user 'babelpainterwell':

     ```bash
      python cli.py get-user-projects babelpainterwell
      Projects for user 'babelpainterwell':
      - Adam-Optimizer-Implementation: None
        Stars: 0, Forks: 0

      - Attention_Detector: None
        Stars: 0, Forks: 0

      - Backprop-Implementation: None
        Stars: 0, Forks: 0
     ```

     **Example:** To get the 5 most recent users saved in the database:

     ```bash
      python cli.py get-recent-users 5
      Most recent 5 users:
      - northeastern (ID: 3)
      - luoshuaiqing (ID: 2)
      - babelpainterwell (ID: 1)
     ```

     **Example:** To get the 10 most starred projects saved in the database:

     ```bash
       python cli.py get-most-starred-projects 10
       Top 10 most starred projects:
       - Avengers-V.S.-Thanos by User ID 2
         Stars: 2, Forks: 0

       - TutorSpace by User ID 1
         Stars: 1, Forks: 0

       - coronaHub by User ID 2
         Stars: 1, Forks: 0

       - Scrabble by User ID 2
         Stars: 1, Forks: 0

       - Adam-Optimizer-Implementation by User ID 1
         Stars: 0, Forks: 0
     ```

3. **Run the API Server:**
   Before using the CLI tool, make sure the FastAPI server is running:
   ```bash
   make start
   ```

---

**Scalability** in this project is achieved primarily through the use of asynchronous operations and optimized database interactions and layered architecture.

### Asynchronous Programming & Efficient Database Access

- **Async Endpoints and Services**
  By using async functions in FastAPI endpoints and service methods, the application can handle many concurrent requests without blocking.

- **Async Database Operations**
  The database interactions use asynchronous sessions (AsyncSession), allowing queries to run without holding up the event loop. This improves throughput and response times.

- **Async External Calls**
  The GitHub API client uses httpx.AsyncClient, enabling the application to make external HTTP requests without waiting synchronously, thus also improving throughput.

- **Indexed Fields**
  Indexing the username field in the User model speeds up lookup times.

### Layered Architecture

The project is designed with a layered architecture to keep things organized and maintainable. At the top, we have the **API layer** using FastAPI, which handles incoming HTTP requests and routes them to the correct endpoints. The **service layer** contains the business logic in the Service class; it orchestrates the interactions between the repositories and external services like the GitHub API. For database interactions, we have the **repository layer** with `UserRepository` and `ProjectRepository`, which abstract away the database details and provide clean methods for data access. We also have a **GitHub API client** (GitHubAPIClient) that takes care of fetching data from GitHub when needed. Our data models (User and Project) define the structure of the data we work with. Lastly, there's a **command-line interface** built with Typer that lets users interact with the API directly from the terminal.

##### Client Layer (API client)

- The CLI tool that users interact with.
- Sends HTTP requests to the RESTful API endpoints.
- Only communicates with the API layer.

##### API Layer

- Serves as the intermediary between the client and the backend logic.
- Handles incoming HTTP requests
- Returns HTTP responses to the client layer.

I delegate the core business logic to the service layer without embedding it in the api layer considering the needs for better scalability, seperation of concerns and testability.

- Endpoints
  - `GET /users/{username}/projects` - retrieves projects for a given GitHub username.
  - `GET /users/recent/{n}` - retrieves the N most recent users saved in the database.
  - `GET /projects/most-starred/{n}` - retrieves the N most starred projects saved in the database.
- For more details, see the API documentation at [API DOCUMENTATION](http://127.0.0.1:8000/docs) while the server is running.

##### Service Layer

- Implements the main functionalities, such as retrieving user projects, getting recent users and fetching most starred prohecrs.
- Decides whether to fetch data from the database or call external APIs (Github)
- Process and manimulate data.

##### Data Access Layer

- Focuses solely on interacting with the database so that we make future changes in the database schema only affect this layer.

~~When using SQLALchemy~~ Now using **SQLModel** for similicity and avoiding potential validation error, I implemented a repository pattern to abstract the database operations from the service layer, which is, similarly as we did with the external service layer, to make the code more testable and maintainable.

##### External Service Layer

- Encapsulates all interactions with external APIs.

##### Trade-offs and Design Decisions

**1. Repository Pattern**

- Implemented repositories for data access to abstract the database operations from the service layer, which makes the code more testable and maintainable. The trade-off is that it adds an extra layer of complexity.

---

### Data Models

The project defines two primary data models in `app/models.py`:

- **User Model (User class):**

  - Fields:
    - id: An auto-incremented primary key (integer).
    - username: The GitHub username, indexed and unique for fast lookups.
    - created_at: Timestamp when the user was added to the database, defaults to the current UTC time.
    - projects: A list of related Project instances (one-to-many relationship).

- **Project Model (Project class):**

  - Fields:
    - id: An auto-incremented primary key (integer).
    - name: The name of the project.
    - description: An optional description of the project.
    - stars: Number of stars the project has on GitHub.
    - forks: Number of times the project has been forked.
    - user_id: Foreign key linking to the User model.
    - user: A reference back to the associated User instance.

These models use **SQLModel**, which combines features of Pydantic and SQLAlchemy, providing both data validation and ORM capabilities.

---

### Error Handling

In this project, error handling for all API endpoints is centralized through the exception handlers defined in the `app/main.py` file. Each endpoint in `app/api/routes.py` performs its specific operations and, if any exceptions occur—such as NotFoundError, DatabaseError, or ExternalAPIError—these are not handled directly within the route functions. Instead, they propagate up to the global exception handlers in `app/main.py`.

1. **Custom Exception Classes**

   - **NotFoundError**: Raised when a resource (user) is not found.
   - **DatabaseError**: Raised when an error occurs while interacting with the database.
   - **ExternalAPIError**: Raised when an error occurs while interacting with an external API (GitHub).

2. **Exception Handlers in FastAPI**
   In `app/main.py`, custom exception handlers are registered to catch these exceptions and return appropriate HTTP responses:

   - **NotFoundError Handler**: Returns a 404 status code with a message indicating that the resource was not found.
   - **DatabaseError Handler**: Returns a 500 status code with a message indicating a server error related to the database.
   - **ExternalAPIError Handler**: Returns a 503 status code with a message indicating an external API error.
   - **General Exception Handler**: Catches any other unhandled exceptions, logs the error, and returns a 500 status code with a generic error message.

3. **Error Handling Implementation in Repositories and Services**

- **Repositories:**

  - The `UserRepository` and `ProjectRepository` classes interact with the database. They catch exceptions like `SQLAlchemyError` and raise `DatabaseError` with a relevant message.
  - Example: If a `SQLAlchemyError` occurs while fetching a user, it is caught and a `DatabaseError` is raised with a message.

- **Services:**

  - The `Service` class methods use repositories and handle exceptions raised by them.
  - They catch specific exceptions like `NotFoundError`, `DatabaseError`, and `ExternalAPIError`, log the error, and re-raise the exception for the FastAPI exception handlers to process.

4. **External API Client Error Handling**

- The `GitHubAPIClient` handles communication with the GitHub API.
- It catches HTTP errors from httpx and raises appropriate exceptions:
  - If the GitHub API returns a 404, meaning the user with input username doesn't exist on Github, a `NotFoundError` is raised.
  - For other HTTP errors, an `ExternalAPIError` is raised.
  - Any unexpected exceptions are caught, logged, and an `ExternalAPIError` is raised.

5. **Validation Errors**

- FastAPI automatically handles validation errors for request parameters.
- If a request fails validation (e.g., a negative number where only positive numbers are allowed), FastAPI returns a 422 status code with details about the validation error.

6. **Logging**

- Logging is configured to capture error messages and stack traces and stored in a log file.

---

### Testing Strategy and Test Coverage

Mocking is employed in the tests to simulate the behavior of components that the unit under test interacts with, without relying on actual implementations. In this project, mocking is used extensively to:

- **Simulate Database Operations**: The methods of `UserRepository` and `ProjectRepository` are mocked to return predefined results or raise exceptions without accessing the real database. This isolates the tests from database dependencies.

- **Mock External API Calls**: The `GitHubAPIClient` methods are mocked to simulate responses from the GitHub API.

- **Simulate Exceptions**: By mocking methods to raise exceptions, tests verify that error handling mechanisms work correctly, ensuring that appropriate exceptions are caught.

**Testing Framework**

- Pytest: Used for writing and executing test cases.
- Asyncio Support: Tests are marked with `@pytest.mark.asyncio` to support asynchronous code.

**Test Coverage**

1. **Tests for `/users/{username}/projects` Endpoint:**
   - a. User Exists in Database with Projects - verifies that the API returns a 200 status code and the correct list of projects.
   - b. User Exists in Database with No Projects - ensures the API returns a 200 status code and an empty list.
   - c. User Not in Database but Exists on GitHub with Projects - simulates fetching projects from GitHub, storing them, and returning the project list.
   - d. User Not in Database but Exists on GitHub with No Projects - verifies that the API handles users with no projects correctly.
   - e. User Not in Database and Not on GitHub - ensures that a 404 status code is returned when the user doesn't exist on GitHub.
   - f. GitHub API Failure - simulates an external API failure and checks that a 503 status code is returned.
2. **Tests for `/users/recent/{n}` Endpoint:**
   - a. Exactly N Users in Database - checks that the API returns the correct number of recent users.
   - b. Fewer Than N Users in Database - ensures the API returns all available users when fewer than N exist.
   - c. No Users in Database - verifies that the API returns an empty list when no users are present.
3. **Tests for `/projects/most-starred/{n}` Endpoint:**
   - a. Exactly N Projects in Database - checks that the API returns the correct number of most starred projects.
   - b. Fewer Than N Projects in Database - ensures the API returns all available projects when fewer than N exist.
   - c. No Projects in Database - verifies that the API returns an empty list when no projects are present.
4. **Tests for Database Errors:** - this part is generated by ChatGPT
   - a. Simulated Database Errors in User Repository - mocks database exceptions to ensure the application handles them gracefully. Custom mock sessions are created to simulate exceptions within database sessions.
   - b. Simulated Database Errors in Project Repository - similar to above but focuses on project-related database operations.
5. **Tests for Input Validation:**
   - a. Invalid Username Scenarios - empty username, overly long username, and usernames with invalid characters are tested to ensure proper validation and error responses.
   - b. Invalid n Values for Pagination - negative numbers and excessively large numbers for n are tested to confirm that the API returns a 422 status code for invalid input.

**Running Tests**

- Execute tests using:
  ```bash
  pytest
  ```

---

### Refenrece Links

- Poetry Documentation - https://python-poetry.org/docs/
- Typer Documentation - https://typer.tiangolo.com/
- FastAPI Documentation - https://fastapi.tiangolo.com/
