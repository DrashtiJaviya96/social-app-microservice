# Social App Microservices

This project is a small Django REST Framework social app split into two microservices:

- **User Service**: registration, login, JWT authentication, profiles, and account-related APIs
- **Post Service**: creating and managing posts

I built it as a microservice-style app, but kept it intentionally simple and practical. The goal was to only showcase production grade skill.

## Why I used two databases locally and one shared database in production

This part is important to me because it reflects the tradeoff I was making while learning.

### Local development: separate databases for each service

In my local Docker setup, I used one PostgreSQL database per service:

- `user_db`
- `post_db`

This is the cleaner model when working locally. Each service owns its own data, and there is less confusion while debugging. It also makes the architecture to  microservice boundaries, where each app can evolve independently.

For me, this was helpful because I could reason about the app much more clearly during development:

- user-related data stays with the user service
- post-related data stays with the post service
- local testing is easier and more isolated
- there is almost no accidental coupling between the databases

### Production: one shared database container

In production, I intentionally used one shared PostgreSQL container for both services.

Why? Because I wanted the deployment to stay simple, cost-freindly, and easy to manage on a single EC2 instance. At this stage, the app is small, and I was optimizing for:

- fewer moving parts
- simpler Docker setup
- lower infrastructure cost
- faster deployment and easier troubleshooting

So yes, in a bigger production system I would likely move toward separate databases per service, but for this project I chose the shared database as a practical compromise. It keeps the app lightweight while still letting me learn and ship the full flow end-to-end.

This is a conscious choice, not a mistake.

## Tech Stack

- Python 3.13
- Django and Django REST Framework
- PostgreSQL
- Docker and Docker Compose
- GitHub Actions and GitHub Container Registry
- AWS EC2 and CloudFormation
- Swagger/OpenAPI

## Local Development

Copy the example environment file and update it for your machine. Do not commit a real `.env` file with secrets.

```bash
cp .env.example .env
docker compose up --build
```

The services are available at:

- User Service: http://localhost:8000
- Post Service: http://localhost:8001

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

## CI Workflow

The two services each have their own GitHub Actions workflow.

When code is pushed to `develop`, the workflow spins up PostgreSQL, installs dependencies, runs migrations, executes tests, and then builds and pushes a Docker image to GitHub Container Registry. The images are tagged with the commit SHA:

```text
ghcr.io/<owner>/user-service:dev-<commit-sha>
ghcr.io/<owner>/post-service:dev-<commit-sha>
```

When code is pushed to `main`, the workflow runs tests but does not push a Docker image. I disabled pull request triggers to avoid duplicate CI noise when PRs are opened.

## Production Deployment

Production deployment is started manually from GitHub Actions using the `deploy-to-prod.yml` workflow. It accepts:

- `user_dev_sha`: the SHA portion of the user-service development image tag
- `post_dev_sha`: the SHA portion of the post-service development image tag
- `version`: the production version tag, such as `v1.0.0`

The workflow retags the selected development images, deploys the CloudFormation stack, and runs both services as Docker containers on an AWS EC2 instance:

- User Service: port `8000`
- Post Service: port `8001`

The production workflow currently uses a single shared PostgreSQL container for both services. I chose that setup because it is the simplest and most cost-effective approach for this project’s EC2 deployment model.

## Required GitHub Secrets

Configure these as repository secrets or production environment secrets:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
EC2_SSH_PRIVATE_KEY
PROD_DB_PASSWORD
DJANGO_SECRET_KEY
JWT_SECRET_KEY
```

`GITHUB_TOKEN` is provided automatically by GitHub Actions.

## License

MIT License. See [LICENSE](LICENSE).
