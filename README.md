<p align="center">
    <img src="./ludika-frontend/ludika-frontend/public/favicon.svg" alt="Ludika Logo" width="100"/>
</p>

<h1 align="center">Ludika</h1>
<h3 align="center">A Platform for Game-Based Learning Tools Assessment</h3>

<p align="center">
    <img src="https://img.shields.io/badge/frontend-Nuxt%204-green?logo=nuxtdotjs" alt="Nuxt 4"/>
    <img src="https://img.shields.io/badge/backend-FastAPI-blue?logo=fastapi" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/database-PostgreSQL-blue?logo=postgresql" alt="PostgreSQL"/>
    <img src="https://img.shields.io/badge/docs-LaTeX-orange?logo=latex" alt="LaTeX"/>
    <img src="https://github.com/manchineel/Ludika/actions/workflows/build-backend-docker/badge.svg" alt="GitHub Actions Status"/>
</p>



This monorepo structure contains the entire stack of the Ludika Content Management System:

- [Frontend](./ludika-frontend): Nuxt
- [Backend](./ludika-backend): FastAPI, SQLModel, LangChain
- [Database](./ludika-db): PostgreSQL
- [Documentation](./ludika-docs): LaTeX
  - [APIssima Tool](./ludika-docs/tools/apissima.py): Python script to generate LaTeX API documentation from OpenAPI specs
- [Deployment](./ludika-deployment): Docker, Docker-Compose, NGINX
- [Graphics](./ludika-graphics/Ludika.afdesign): Ludika logo (Affinity Designer project)