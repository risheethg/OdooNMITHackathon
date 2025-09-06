from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Loads and validates application settings from environment variables.
    """
    # Load settings from a .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')
    
    LOGGER: int = 20
    
    # MongoDB Settings
    ME_CONFIG_MONGODB_URL: str = "mongodb://localhost:27017/"
    MONGODB_DB: str = "odoohack"
    GEMINI_API_KEY: str = "" 
    #jira key
    JIRA_URL:str=""
    JIRA_USERNAME:str=""
    JIRA_API_KEY:str=""

# Create a single, importable instance of the settings
settings = Settings()