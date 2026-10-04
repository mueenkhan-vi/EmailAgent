from langchain_openai import ChatOpenAI
from config.settings import settings

def get_llm():
    provider = settings.llm_provider.strip().lower()

    if provider == "openai":
        return ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.openai_api_key,
        )

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )