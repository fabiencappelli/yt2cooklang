import json
import requests
from pydantic import BaseModel


OLLAMA_URL = "http://localhost:11434/api/chat"


def call_ollama_structured(
    model: str,
    system_prompt: str,
    user_prompt: str,
    schema_model: type[BaseModel],
) -> dict:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0,
            "num_predict": 1800,
            "num_ctx": 8192,
        },
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=None)
    response.raise_for_status()

    content = response.json()["message"]["content"]
    content = response.json()["message"]["content"]

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        print("\n--- RÉPONSE BRUTE DU MODÈLE ---\n", flush=True)
        print(content[:4000], flush=True)
        print("\n--- FIN RÉPONSE BRUTE ---\n", flush=True)
        raise exc

    return schema_model.model_validate(data).model_dump()

    return schema_model.model_validate(data).model_dump()