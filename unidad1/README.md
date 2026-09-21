# Unidad 1: Asistente de atención al cliente BNPL con un Foundation Model

**Alumno:** Julian Rachitzky · **Materia:** Seminario de Ciencia de Datos II (UCAECE) · **Actividad:** TP Individual, Unidad 1

## Caso de uso

Un asistente virtual de atención al cliente para **CuotaYa**, una fintech hipotética de
"comprá ahora, pagá después" (BNPL). Responde las consultas más repetidas de los clientes:
cuánto se paga de inicial y en cada cuota, qué pasa si una cuota vence, cómo se sube de
nivel y qué hacer ante intentos de fraude. Los casos que necesitan a una persona
(reclamos, disputas, fraude) los deriva a un agente humano.

## Modelo elegido

**`openai/gpt-oss-20b`**, un modelo de **pesos abiertos** (licencia Apache 2.0) que se usa
a través de la API gratuita de **Groq**. Lo elegí porque tiene pesos abiertos: los datos
financieros de los clientes son sensibles, y con un modelo abierto se puede pasar más
adelante a un despliegue propio (self-hosting) sin cambiar de modelo. Además, el costo
por consulta es bajo y la latencia de Groq es baja.

## Estrategia de adaptación

**Prompt engineering avanzado: few-shot chain-of-thought.** No hay fine-tuning. El prompt
(`src/prompt_templates.py`) tiene cuatro partes:

1. Un rol y el tono esperado.
2. Las **políticas del negocio** (porcentaje de inicial, límites, recargos, seguridad).
3. **3 ejemplos resueltos**. Cada uno tiene un `Razonamiento:` con la regla aplicada y los
   cálculos, y después una `Respuesta:` para el cliente.
4. La consulta real, con el `Razonamiento:` abierto para que el modelo lo complete.

La temperatura es 0,2, porque en atención al cliente importa más la consistencia que la
creatividad.

## Cómo ejecutarlo

1. Crear el Codespace con **Code → Codespaces → ... → New with options** y elegir la
   config `unidad1-seminario-cd2`.
2. Configurar la API key. El `.env` está en `.gitignore` y nunca se sube.
   ```bash
   cp .env.example .env
   # editar .env:  MODEL_PROVIDER=groq  y  GROQ_API_KEY=<tu key de console.groq.com>
   ```
3. Ejecutar (las dependencias de `requirements.txt` se instalan solas al crear el Codespace):
   ```bash
   python -m src.main
   ```
4. El script corre 4 consultas de ejemplo, imprime las respuestas y genera
   **`evidencias.md`** con el prompt completo y la respuesta de cada una.

> Si Groq devuelve `404 model_not_found`, listá los modelos vigentes con
> `curl -s -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models`
> y actualizá `GROQ_MODEL_NAME` en `src/providers/groq_provider.py`.

## Estructura

```
unidad1/
├── src/
│   ├── main.py               # orquesta: lee config, corre las consultas, escribe evidencias.md
│   ├── prompt_templates.py   # contexto de CuotaYa + ejemplos + técnica few-shot CoT
│   └── providers/            # Groq y Gemini, elegidos por MODEL_PROVIDER (factory)
├── evidencias.md             # generado por la ejecución
├── requirements.txt
└── .env.example
```
