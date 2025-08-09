# Ludika Deployment Guide

This guide explains how to deploy the Ludika application using Docker Compose. It covers the setup of the frontend, backend, and Nginx reverse proxy, as well as environment configuration.

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- SSL certificates for HTTPS (see below)

## Directory Structure
```
ludika-deployment/
├── docker-compose.yml
├── nginx.conf
├── certs/
│   ├── fullchain.pem
│   └── privkey.pem
├── README.md
└── app/
    ├── static/
    └── config.ini
```

## Configuration

### Backend Configuration
Copy the example config file and update values:
```sh
mkdir -p ./app/static
cp ../ludika-backend/config.ini.example ./app/config.ini
```
Edit `config.ini` with your database credentials, API keys, and other secrets and third-party services. Example:
```ini
[Database]
user=ludika
dbname=ludika
password={YOUR_DB_PASSWORD}
host=postgres
port=5432

[Authentication]
secret_key={YOUR_SECRET_KEY}
access_token_expire_minutes=43200

[GenerativeAI]
ai_main_provider=google
ai_user_id={RANDOM_UUID}
tavily_api_key={YOUR_TAVILY_API_KEY}
nvidia_model=meta/llama-3.1-405b-instruct
rate_limit_llm=False
google_gemini_api_key={YOUR_GEMINI_API_KEY}
nvidia_api_key={YOUR_NVIDIA_API_KEY}
google_custom_search_api_key={YOUR_CUSTOM_SEARCH_API_KEY}
reddit_client_id={YOUR_REDDIT_CLIENT_ID}
reddit_client_secret={YOUR_REDDIT_CLIENT_SECRET}
enable_reddit_scraping=true
```

where:
- `{YOUR_DB_PASSWORD}` is the password for the PostgreSQL user
- `{YOUR_SECRET_KEY}` is a secret key used for password hashing (can be any random string)
- `{YOUR_TAVILY_API_KEY}` is your API key for the [Tavily API](https://tavily.com)
- `{YOUR_NVIDIA_API_KEY}` is your API key for the [NVIDIA NIM API](https://build.nvidia.com/)
- `{YOUR_GEMINI_API_KEY}` is your API key for the [Google Gemini API](https://cloud.google.com/gemini)
- `{YOUR_REDDIT_API_KEY}` and `{YOUR_REDDIT_CLIENT_SECRET}` are your API credentials for the [Reddit API](https://www.reddit.com/prefs/apps)
- `{RANDOM_UUID}` is a unique identifier for the AI user, which can be generated using e.g. `uuidgen`

### SSL Certificates
Place your SSL certificates in the `certs/` directory. The Nginx service expects them at `/etc/nginx/certs`.

## Usage

### 1. Start Services

In the `ludika-deployment` directory, adjust your `docker-compose.yml` as needed (set and take note of the database credentials), then run:
```sh
docker compose up -d
```
This will start:
- **frontend**: Ludika frontend on port 3051
- **backend**: Ludika backend on port 8000
- **nginx**: Reverse proxy and static asset serving on port 443 (HTTPS)
- **postgres**: PostgreSQL database on port 5432

### 2. Set database schema from `schema.sql` and AI user configuration

In the `ludika-deployment` directory, run:
```sh
docker compose exec postgres psql -U ludika -d ludika -f /app/schema.sql
docker compose exec postgres psql -U ludika -d ludika -c "INSERT INTO users (uuid, visible_name, email, user_role) VALUES ('{RANDOM_UUID}', 'AI User', 'ai_user@example.com', 'user');"
```

with the desired UUID for the AI user from the `config.ini`.

For good measure, you should also restart the backend service:
```sh
docker compose restart backend
```

### 3. Done! 🎉

You should now be able to access the application at `https://localhost` and the interactive API documentation at `https://localhost/api/v1/docs`.