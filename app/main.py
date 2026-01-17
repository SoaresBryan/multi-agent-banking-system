from fastapi import FastAPI

app = FastAPI(
    title="Multi-Agent Banking System",
    description="Sistema multiagente para operações bancárias",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
