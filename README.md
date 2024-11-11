# Scalable-Github-Scraping-Service

###### FASTapi, Pydantic, Error handiling!, Unit Test (Tesing), Documentation, Asynchrounous Design, Caching, auto-scaling if possible,

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

##### External Service Layer

- Encapsulates all interactions with external APIs.

### Refenrece Links

Poetry Documentation - https://python-poetry.org/docs/
Typer Documentation - https://typer.tiangolo.com/
FastAPI Documentation - https://fastapi.tiangolo.com/

### Q & A

1. who are the real users? hiring manager? the number of potential users that will use this service? (the need for scalability however is required.)
