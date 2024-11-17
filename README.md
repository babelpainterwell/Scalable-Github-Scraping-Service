# Scalable-Github-Scraping-Service

###### FASTapi, Pydantic, Error handiling!, Unit Test (Tesing), Documentation, Asynchrounous Design, Caching, logging, auto-scaling if possible,

### Architecture

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

##### Service Layer

- Implements the main functionalities, such as retrieving user projects, getting recent users and fetching most starred prohecrs.
- Decides whether to fetch data from the database or call external APIs (Github)
- Process and manimulate data.

##### Data Access Layer

- Focuses solely on interacting with the database so that we make future changes in the database schema only affect this layer.

~~When using SQLALchemy~~ Now using SQLModel for similicity and avoiding potential validation error, I implemented a repository pattern to abstract the database operations from the service layer, which is, similarly as we did with the external service layer, to make the code more testable and maintainable.

##### External Service Layer

- Encapsulates all interactions with external APIs.

### Trade-offs and Design Decisions

##### 1. Asynchronous Code

- Chose to use asynchronous code throughout to better align with FASTapi's async capabilities and improve performance for I/O bound operations such as database queries and HTTP requests.

##### 2. Repository Pattern

- Implemented repositories for data access to abstract the database operations from the service layer, which makes the code more testable and maintainable. The trade-off is that it adds an extra layer of complexity.

##### 3. Error Handling and Data Validation

- Used Pydantic models for data validation. SQLModel is chosen for the ORM models to work with Pydantic models.

### Refenrece Links

- Poetry Documentation - https://python-poetry.org/docs/
- Typer Documentation - https://typer.tiangolo.com/
- FastAPI Documentation - https://fastapi.tiangolo.com/

### Error Handling

allow the errors from different layers to propagate up to the API layer, where they are caught and handled.
Docs: different types of errors that can occur in the application, and how to handle them.

### Challenges

1. To let SQLAlchemy ORM models to work with Pydantic models, later realized that FASTapi has built-in SQLModel which is a Pydantic model with SQLAlchemy support.
2. Cannot call sync methods such as `create_engine` using an async engion.
3. `User repository error in get_by_username: Class 'sqlalchemy.engine.row.Row' is not mapped`, however, a User object is expected.
4. For non-existant user, the github rest api returns a 404 status code.

### Q & A & Todo

1. who are the real users? hiring manager? the number of potential users that will use this service? (the need for scalability however is required.)
2. `create_async_engine` from SQLAlchemy works for SQLModel?
3. To distinguish between a user not found and a user with no public repositories.
4. To test the github_api module.
5. no such api defined? having problems creating insert empty projects???
