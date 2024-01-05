# RESTful API Demonstration using DRF

A basic RESTful API built with Django Rest Framework, demonstrating user authentication with JWT, rate limiting, blacklisting, and CRUD operations, leveraging PostgreSQL for database and Redis for in-memory caching.

## API Endpoints:

### Authentication Endpoints:
- **POST /api/auth/signup:** Creates a new user account.
- **POST /api/auth/login:** Logs in to an existing user account and receives an access token.

### Note Endpoints:
- **GET /api/notes:** Retrieves a list of all notes for the authenticated user.
- **GET /api/notes/:id:** Retrieves a note by ID for the authenticated user.
- **POST /api/notes:** Creates a new note for the authenticated user.
- **PUT /api/notes/:id:** Updates an existing note by ID for the authenticated user.
- **DELETE /api/notes/:id:** Deletes a note by ID for the authenticated user.
- **POST /api/notes/:id/share:** Shares a note with another user for the authenticated user.
- **GET /api/search?q=:query:** Searches for notes based on keywords for the authenticated user.

### Building and Running the Project:

1. Build the Docker containers:

    ```bash
    docker-compose up --build
    ```

2. Apply migrations:

    ```bash
    docker-compose run web python manage.py makemigrations accounts
    docker-compose run web python manage.py makemigrations note_app
    docker-compose run web python manage.py migrate
    ```

### Running Tests:

Run tests for each app:

```bash
docker-compose run web python manage.py test Notes
docker-compose run web python manage.py test note_app
docker-compose run web python manage.py test accounts
```


### Implementation Details:

**Framework - Django REST Framework:**
DRF offers a feature-rich toolkit for rapid API development, providing flexibility with customizable components for tailored API solutions. The well-maintained documentation ensures ease of use, while an active community ensures ongoing support.

**Database - PostgreSQL:**
PostgreSQL was chosen for its reliability, stability, and advanced features. The django.contrib.postgres.search library provides powerful search tools out of the box. Tools like SearchVector, SearchQuery, and SearchRank can be combined in a myriad of ways to create powerful searches.

**Caching with Redis:**
Redis is utilized as an in-memory caching system to enhance the performance and responsiveness of certain middleware components.

