from functools import lru_cache

from django.conf import settings
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider


def get_openrouter_model_name() -> str:
    provider_prefix = "openrouter:"
    model_name = settings.PYDANTIC_AI_MODEL

    if model_name.startswith(provider_prefix):
        return model_name.removeprefix(provider_prefix)

    return model_name


@lru_cache(maxsize=1)
def get_openrouter_model() -> OpenRouterModel:
    return OpenRouterModel(
        get_openrouter_model_name(),
        provider=OpenRouterProvider(
            api_key=settings.OPENROUTER_API_KEY,
            app_url=settings.SITE_URL,
            app_title="Built with Django",
        ),
    )
