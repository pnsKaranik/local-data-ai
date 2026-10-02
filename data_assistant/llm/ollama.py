import httpx

from data_assistant.config import get_settings

from typing import TypeVar

from pydantic import BaseModel

ModelT = TypeVar(
    "ModelT",
    bound=BaseModel,
)

class OllamaClient:
    def __init__(self) -> None:
        settings = get_settings()

        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model

    def generate(self, prompt: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120.0,
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]

def generate_structured(
    self,
    prompt: str,
    response_model: type[ModelT],
) -> ModelT:
    response = httpx.post(
        f"{self.base_url}/api/generate",
        json={
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": response_model.model_json_schema(),
            "options": {
                "temperature": 0,
            },
        },
        timeout=120.0,
    )

    response.raise_for_status()

    data = response.json()

    return response_model.model_validate_json(
        data["response"]
    )