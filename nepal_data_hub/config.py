from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    USGS_API_URL: str = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    POLL_INTERVAL: int = 60  # Seconds
    APP_ENV: str = "development"
    
    # Optional: Filter for Nepal region (approx)
    # Latitude: 26.0 to 31.0, Longitude: 80.0 to 89.0
    NEPAL_MIN_LAT: float = 26.0
    NEPAL_MAX_LAT: float = 31.0
    NEPAL_MIN_LON: float = 80.0
    NEPAL_MAX_LON: float = 89.0
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
