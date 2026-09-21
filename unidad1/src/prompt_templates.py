"""Plantillas de prompting parametrizables (few-shot y chain-of-thought).

Caso de uso (consigna 1): asistente de atención al cliente de "CuotaYa", una
fintech hipotética de "comprá ahora, pagá después" (BNPL). El asistente
responde dudas sobre cuotas, límites, atrasos y seguridad de la cuenta.

Técnica elegida (consigna 3): few-shot chain-of-thought. Se combinan las dos
técnicas vistas en la unidad (Wei et al., 2022): los ejemplos resueltos le
muestran al modelo el tono, el formato y las reglas del negocio (few-shot), y
cada ejemplo incluye un razonamiento breve antes de la respuesta final
(chain-of-thought), que es lo que más ayuda en los cálculos de cuotas.

`main.py` no arma prompts a mano: llama a una de estas funciones con la
consulta del usuario y obtiene el prompt final ya armado.
"""

# --- Contexto de negocio: políticas (ficticias) que el modelo debe respetar ---
POLITICAS_CUOTAYA = """\
- Toda compra se divide en un pago inicial (en el momento) y 3 cuotas sin interés, una cada 14 días.
- El pago inicial depende del nivel del cliente: nivel 1 = 50 %, nivel 2 = 40 %, nivel 3 = 25 % del precio.
- Límite de monto financiado (precio menos pago inicial): nivel 1 = 100 USD, nivel 2 = 300 USD, nivel 3 = 800 USD.
  Si el monto financiado supera el límite, el cliente puede aumentar voluntariamente el pago inicial.
- Cuota vencida: se cobra un recargo único del 5 % sobre esa cuota y la línea queda bloqueada hasta regularizar.
- Subida de nivel: se evalúa al completar 3 compras con todas sus cuotas pagadas a tiempo.
- Se pueden adelantar cuotas sin costo; no se pueden cambiar las fechas de vencimiento.
- CuotaYa NUNCA pide claves, códigos SMS ni datos de tarjeta por WhatsApp, mail o teléfono.
- Reclamos por productos, disputas o sospecha de fraude se derivan a un agente humano."""

INSTRUCCION_SISTEMA = (
    "Sos el asistente virtual de atención al cliente de CuotaYa, una fintech de "
    "'comprá ahora, pagá después'. Respondé en español rioplatense, con tono cordial "
    "y claro. Usá solo las políticas de abajo; si algo no está cubierto o requiere "
    "ver datos de la cuenta, decilo y ofrecé derivar a un agente humano. "
    "Nunca inventes montos ni reglas."
)

INSTRUCCION_CHAIN_OF_THOUGHT = (
    "Antes de responder, pensá el problema paso a paso en un 'Razonamiento:' breve "
    "(qué regla aplica y, si hay montos, cada cálculo). Después escribí la respuesta "
    "definitiva para el cliente precedida por 'Respuesta:'."
)

# --- Ejemplos few-shot del caso de uso (consulta + razonamiento + respuesta) ---
EJEMPLOS_FEW_SHOT = [
    {
        "consulta": "Soy nivel 1 y quiero comprar unas zapatillas de 90 USD. ¿Cómo me quedan los pagos?",
        "razonamiento": (
            "Nivel 1 → inicial 50 %: 90 × 0,50 = 45 USD. Monto financiado: 90 − 45 = 45 USD, "
            "que está debajo del límite de 100 USD. Cuotas: 45 / 3 = 15 USD cada 14 días."
        ),
        "respuesta": (
            "¡Dale! Hoy pagás 45 USD de inicial y después 3 cuotas de 15 USD, una cada 14 días, "
            "sin interés. Si querés, podés adelantar cuotas sin costo."
        ),
    },
    {
        "consulta": "Estoy en nivel 2 y quiero un televisor de 800 USD. ¿Puedo?",
        "razonamiento": (
            "Nivel 2 → inicial 40 %: 800 × 0,40 = 320 USD. Monto financiado: 800 − 320 = 480 USD, "
            "que supera el límite de 300 USD. Para financiar como máximo 300 USD, el inicial "
            "tendría que ser 800 − 300 = 500 USD, y las cuotas 300 / 3 = 100 USD."
        ),
        "respuesta": (
            "Con el inicial estándar de tu nivel (320 USD) te quedarían 480 USD para financiar, "
            "y tu límite hoy es de 300 USD. Igual podés comprarlo si subís el inicial a 500 USD: "
            "así te quedan 3 cuotas de 100 USD, una cada 14 días."
        ),
    },
    {
        "consulta": "Me llegó la licuadora rota y la tienda no me contesta. ¿Tengo que seguir pagando?",
        "razonamiento": (
            "Es un reclamo por producto / posible disputa. Según las políticas, eso lo gestiona "
            "un agente humano; no tengo que prometer suspender las cuotas."
        ),
        "respuesta": (
            "Qué mala suerte, perdón por el mal momento. Los reclamos por productos los maneja "
            "nuestro equipo de disputas, así que te derivo con un agente humano para que revise "
            "tu caso y te diga qué pasa con las cuotas. [DERIVAR_A_HUMANO]"
        ),
    },
]


def formatear_contexto() -> str:
    """Devuelve el bloque fijo de instrucciones + políticas del negocio."""
    return f"{INSTRUCCION_SISTEMA}\n\nPolíticas de CuotaYa:\n{POLITICAS_CUOTAYA}"


def formatear_ejemplo(ejemplo: dict, con_razonamiento: bool) -> str:
    """Formatea un ejemplo few-shot, con o sin el paso de razonamiento."""
    bloque = f"Consulta: {ejemplo['consulta']}\n"
    if con_razonamiento:
        bloque += f"Razonamiento: {ejemplo['razonamiento']}\n"
    return bloque + f"Respuesta: {ejemplo['respuesta']}"


def construir_prompt_few_shot(consulta: str, ejemplos: list[dict] = EJEMPLOS_FEW_SHOT) -> str:
    """Arma un prompt few-shot: contexto + pares consulta/respuesta de ejemplo +
    la consulta real del usuario sin responder."""
    bloques_ejemplo = [formatear_ejemplo(ejemplo, con_razonamiento=False) for ejemplo in ejemplos]
    ejemplos_formateados = "\n\n".join(bloques_ejemplo)

    return (
        f"{formatear_contexto()}\n\n"
        f"Ejemplos:\n\n{ejemplos_formateados}\n\n"
        f"Consulta: {consulta}\n"
        "Respuesta:"
    )


def construir_prompt_chain_of_thought(consulta: str) -> str:
    """Arma un prompt chain-of-thought (zero-shot): contexto + instrucción de
    razonar paso a paso antes de dar la respuesta final."""
    return f"{formatear_contexto()}\n\n{INSTRUCCION_CHAIN_OF_THOUGHT}\n\nConsulta: {consulta}"


def construir_prompt_few_shot_cot(consulta: str, ejemplos: list[dict] = EJEMPLOS_FEW_SHOT) -> str:
    """Arma un prompt few-shot chain-of-thought (técnica elegida en la consigna 3):
    contexto + instrucción de razonar + ejemplos resueltos que muestran el
    razonamiento + la consulta real, dejando abierto el 'Razonamiento:'."""
    bloques_ejemplo = [formatear_ejemplo(ejemplo, con_razonamiento=True) for ejemplo in ejemplos]
    ejemplos_formateados = "\n\n".join(bloques_ejemplo)

    return (
        f"{formatear_contexto()}\n\n"
        f"{INSTRUCCION_CHAIN_OF_THOUGHT}\n\n"
        f"Ejemplos:\n\n{ejemplos_formateados}\n\n"
        f"Consulta: {consulta}\n"
        "Razonamiento:"
    )
