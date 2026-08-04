import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise RuntimeError(
        "OPENAI_API_KEY no está configurada. Define esta variable en un archivo .env "
        "(ver .env.example) o en el entorno antes de iniciar el backend."
    )


def analyze_ticket(text: str):
    prompt = f"""
    Analiza este mensaje SAP:
    {text}

    Devuelve JSON:
    {{
      "modulo": "",
      "transaccion": "",
      "urgencia": 1-5,
      "impacto": 1-5
    }}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]
