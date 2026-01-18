from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    serpapi_key: str = ""

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "banking_agents"

    app_name: str = "Multi-Agent Banking System"
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
