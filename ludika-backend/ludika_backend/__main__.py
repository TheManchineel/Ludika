import uvicorn

if __name__ == "__main__":
    uvicorn.run("ludika_backend.api:app", host="::1", port=8000, log_level="info", reload=True)
