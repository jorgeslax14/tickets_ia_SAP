import openai
import os

openai.api_key = "REDACTED-ROTATED-OPENAI-KEY"

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