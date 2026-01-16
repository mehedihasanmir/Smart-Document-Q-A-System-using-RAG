import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class Settings:
    """Configuration settings for the application.
    
    Attributes:
        OPENAI_API_KEY: OpenAI API key for LLM operations
        PINECONE_API_KEY: Pinecone API key for vector database operations
        PINECONE_ENVIRONMENT: Pinecone environment identifier
        PINECONE_INDEX_NAME: Name of the Pinecone index to use
        OPENAI_EMBEDDING_MODEL: Model to use for embeddings
        OPENAI_LLM_MODEL: Model to use for LLM responses
        CHUNK_SIZE: Size of text chunks for processing
        CHUNK_OVERLAP: Overlap between consecutive chunks
        TOP_K_RESULTS: Number of top search results to retrieve
    """
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_LLM_MODEL: str = os.getenv("OPENAI_LLM_MODEL", "gpt-4-turbo")
    
    # Pinecone Configuration
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "smart-rag")
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", 5))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def validate(self) -> None:
        """Validate all required configuration settings are set.
        
        Raises:
            ValueError: If required configuration is missing
        """
        required_keys = [
            ("OPENAI_API_KEY", self.OPENAI_API_KEY),
            ("PINECONE_API_KEY", self.PINECONE_API_KEY),
            ("PINECONE_ENVIRONMENT", self.PINECONE_ENVIRONMENT),
        ]
        
        missing_keys = [key for key, value in required_keys if not value]
        
        if missing_keys:
            error_message = f"Missing required environment variables: {', '.join(missing_keys)}"
            logger.error(error_message)
            raise ValueError(error_message)
        
        logger.info("Configuration validation successful")


# Create settings instance
settings = Settings()

# Validate settings on module load
try:
    settings.validate()
except ValueError as e:
    logger.critical(f"Configuration validation failed: {e}")
    raise