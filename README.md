# Social App Microservices

A small social app backend built with Django REST Framework. It has two independent services:

- **Users**: registration, login, JWT authentication, and profiles
- **Posts**: creating and managing posts

Each service has its own PostgreSQL database.

## Tech Stack

Python, Django, Django REST Framework, PostgreSQL, JWT, Docker Compose, and Swagger/OpenAPI.

## Quick Start
Copy the .env.example file to create a .env file, then update the values with your own configuration. The .env.example file is intentionally included to demonstrate which variables are required and what values they should contain, but you must replace them with your own values.

```bash
cp .env.example .env
docker compose up --build
```

## API Docs

- Users: http://localhost:8000/users/api/docs/
- Posts: http://localhost:8001/posts/api/docs/

API roots:

- http://localhost:8000/users/api/v1/
- http://localhost:8001/posts/api/v1/

## Tests

```bash
docker compose exec user_service python manage.py test
docker compose exec post_service python manage.py test
```

## License

MIT License. See [LICENSE](LICENSE).
