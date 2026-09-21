"""Punto de entrada del proyecto.

Orquesta el flujo completo: lee MODEL_PROVIDER del entorno, instancia el
proveedor correspondiente (vía el factory), ejecuta un set de consultas de
ejemplo aplicando la técnica de prompting elegida y vuelca prompt + respuesta
de cada una a evidencias.md.

Este archivo NO implementa detalles de ninguna API: eso vive en
src/providers/. Tampoco arma prompts a mano: eso vive en
src/prompt_templates.py.
"""

import os

from dotenv import load_dotenv

from src.prompt_templates import construir_prompt_few_shot_cot
from src.providers.factory import get_provider

# --- Constantes del script (nada de "magic strings/numbers" inline) ---
MODEL_PROVIDER_ENV_VAR = "MODEL_PROVIDER"
EVIDENCIAS_FILE_PATH = "evidencias.md"

# Técnica de prompting elegida en la consigna 3: few-shot chain-of-thought
# (ejemplos resueltos que incluyen el razonamiento paso a paso).
CONSTRUIR_PROMPT = construir_prompt_few_shot_cot

# Consultas representativas del caso de uso (consigna 1): un cálculo de cuotas,
# una cuota vencida, una duda sobre el nivel y un intento de fraude.
CONSULTAS_DE_EJEMPLO = [
    "Soy nivel 2 y quiero comprar un celular de 450 USD. ¿Cuánto pago hoy y cuánto en cada cuota?",
    "Tenía una cuota de 60 USD que venció hace 4 días y no la pagué. ¿Cuánto tengo que pagar ahora y qué pasa con mi cuenta?",
    "Pago siempre a tiempo desde hace dos meses. ¿Por qué sigo en nivel 1?",
    "Me escribieron por WhatsApp de parte de CuotaYa pidiéndome el código que me llegó por SMS para validar mi cuenta. ¿Se lo paso?",
]


def leer_proveedor_configurado() -> str:
    """Lee MODEL_PROVIDER del entorno y falla con un mensaje claro si falta."""
    proveedor = os.environ.get(MODEL_PROVIDER_ENV_VAR)
    if not proveedor:
        raise ValueError(
            f"Falta la variable de entorno {MODEL_PROVIDER_ENV_VAR}. "
            "Definila en tu archivo .env como 'groq' o 'gemini'."
        )
    return proveedor


def ejecutar_consulta(provider, consulta: str) -> tuple[str, str]:
    """Arma el prompt para una consulta y devuelve (prompt, respuesta)."""
    prompt = CONSTRUIR_PROMPT(consulta)
    respuesta = provider.generate(prompt)
    return prompt, respuesta


def escribir_evidencias(resultados: list[tuple[str, str, str]]) -> None:
    """Vuelca consulta, prompt y respuesta de cada ejecución a un archivo Markdown."""
    lineas = ["# Evidencias de ejecución\n"]
    for numero, (consulta, prompt, respuesta) in enumerate(resultados, start=1):
        lineas.append(f"## Consulta {numero}\n")
        lineas.append(f"**Consulta original:** {consulta}\n")
        lineas.append(f"**Prompt enviado al modelo:**\n\n```\n{prompt}\n```\n")
        lineas.append(f"**Respuesta del modelo:**\n\n{respuesta}\n")

    with open(EVIDENCIAS_FILE_PATH, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))


def main() -> None:
    load_dotenv()

    proveedor_configurado = leer_proveedor_configurado()
    provider = get_provider(proveedor_configurado)

    resultados = []
    for consulta in CONSULTAS_DE_EJEMPLO:
        prompt, respuesta = ejecutar_consulta(provider, consulta)
        resultados.append((consulta, prompt, respuesta))
        print(f"Consulta: {consulta}\nRespuesta: {respuesta}\n")

    escribir_evidencias(resultados)
    print(f"Evidencias guardadas en {EVIDENCIAS_FILE_PATH}")


if __name__ == "__main__":
    main()
