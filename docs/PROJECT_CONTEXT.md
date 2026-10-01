# Neuer Radar AI — Project Context

## Qué es

Neuer Radar AI es un proyecto personal de aprendizaje, portafolio y utilidad real.

Tiene tres objetivos:

1. Construir un radar personal de información técnica relevante.
2. Servir como laboratorio práctico para aprender ingeniería con LLMs y agentes.
3. Convertirse en un proyecto de portafolio que demuestre conocimientos de Python, AI Engineering, DevOps, LLMOps, agentes y arquitectura de software.

No se busca agregar complejidad porque sí. Cada nueva pieza debe enseñar un concepto y resolver un problema real del proyecto.

---

## Objetivo funcional

El sistema recolecta información técnica desde fuentes como:

- Hacker News
- GitHub Trending

y determina qué contenido es relevante según el perfil y objetivos del usuario.

Perfil de interés general:

- AI Agents
- LangGraph / LangChain
- DevOps automation
- AWS
- Cloud / Platform Engineering
- Security
- Python backend
- LLMOps
- RAG
- MCP
- Remote engineering roles

El objetivo final es producir un digest técnico con alto signal-to-noise.

---

## Arquitectura actual

Flujo principal:

Collector  
→ Article  
→ heuristic scoring  
→ LLM classifier  
→ router  
→ optional tool investigation  
→ final decision  
→ storage  
→ digest

### Collectors

Obtienen artículos desde las fuentes y los normalizan al modelo `Article`.

Actualmente se mantienen pocas fuentes deliberadamente para entender bien el sistema antes de escalarlo.

### Heuristic scoring

Filtro determinista y barato basado en:

- keywords
- intereses
- categorías
- penalizaciones
- threshold

Su función es evitar enviar contenido obviamente irrelevante al LLM.

### LLM classifier

Usa un modelo local mediante Ollama.

Modelo actual:

`qwen3.5:9b`

Devuelve structured output:

```json
{
  "decision": "keep | maybe | skip",
  "relevance_score": 0,
  "reason": "...",
  "angle": "..."
}
```

La respuesta es validada con Pydantic.

Regla aproximada:

- 0–39 → skip
- 40–69 → maybe
- 70–100 → keep

`decision` es la señal principal. `relevance_score` sirve principalmente para ordenar; no debe interpretarse como una probabilidad científica.

---

## Provider de LLM

Existe una abstracción `LLMProvider`.

Actualmente:

`OllamaProvider`

pero la arquitectura debe permitir posteriormente:

- OpenAI
- Anthropic
- AWS Bedrock
- otros modelos locales

El provider de Ollama soporta actualmente:

- structured output
- tool calling
- configurable model
- temperature
- seed
- context window (`num_ctx`)
- keep alive
- timeout
- debug
- métricas de tokens
- métricas de latencia

Configuración recomendada actual para clasificación:

```env
LLM_TEMPERATURE=0
LLM_SEED=42
LLM_NUM_CTX=8192
LLM_THINK=false
LLM_DEBUG=true
```

Los prints/debug son intencionales durante la fase de aprendizaje y serán retirados o reemplazados por logging/observabilidad posteriormente.

---

## Tool Calling

Ya existe la primera tool:

`get_github_readme`

El modelo NO ejecuta funciones directamente.

Flujo:

LLM  
→ devuelve `tool_calls`  
→ Python valida que la tool esté registrada  
→ Python ejecuta la función  
→ resultado vuelve al LLM como mensaje `role="tool"`  
→ modelo continúa

Las tools utilizan una whitelist/registry.

Actualmente el router sigue aproximadamente esta lógica:

- `keep` → terminar clasificación
- `skip` → terminar clasificación
- `maybe + GitHub` → investigar con tools

No se debe forzar una tool si el modelo ya tiene suficiente información.

Tool calling y MCP NO son lo mismo.

Tool calling es la capacidad del modelo de solicitar funciones.

MCP se estudiará posteriormente como protocolo estandarizado para exponer y consumir herramientas, recursos y capacidades.

---

## Context enrichment

Se experimentó con README de GitHub.

El README:

- se descarga
- se limpia de HTML, badges e información visual inútil
- se trunca para evitar desperdiciar contexto

Valor aproximado utilizado en pruebas:

`MAX_README_CHARS = 4000`

Principio aprendido:

Más contexto ≠ automáticamente mejor respuesta.

La calidad del contexto importa más que simplemente enviar muchos tokens.

---

## Conceptos aprendidos hasta ahora

### Nivel 1 — Fundamentos LLM

Implementados/practicados:

- prompts
- system/user roles
- tokens
- context window
- temperature
- seed/sampling
- structured outputs
- JSON Schema
- Pydantic validation
- limitaciones por contexto insuficiente
- latencia / cold start / warm model

### Nivel 2 — Integración seria

En progreso:

- tool/function calling
- routing
- gestión de contexto

Pendiente posteriormente:

- tool loop genérico
- caching
- embeddings
- RAG
- memoria/context management

### Nivel 3 — Agentes

Posteriormente:

- LangGraph
- state
- conditional routing
- checkpoints
- human-in-the-loop
- subagentes
- MCP

No introducir LangGraph antes de comprender manualmente los flujos que después LangGraph abstraerá.

---

## Filosofía de desarrollo

Preferir:

simple → observable → entendido → mejorado

sobre:

complejo → abstracto → difícil de entender

Durante el aprendizaje explicar principalmente:

- qué responsabilidad tiene cada archivo
- qué recibe una función
- qué hace
- qué devuelve
- quién la llama
- dónde encaja en el flujo general

Evitar explicaciones línea por línea salvo cuando sean necesarias.

Avanzar aproximadamente un 10% más rápido cuando el contexto ya esté entendido.

---

## Estado actual

El pipeline funciona end-to-end.

Se recolectan artículos, se filtran, se clasifican con el LLM y se genera el digest.

La clasificación ya funciona razonablemente.

El principal problema actual no es decidir qué artículos conservar, sino que el contenido final del digest todavía es pobre.

---

## Próximo objetivo

Separar claramente:

CLASSIFICATION  
“¿Vale la pena leer esto?”

de:

ENRICHMENT / SUMMARIZATION  
“¿Qué tiene de importante y qué debería aprender de esto?”

Para artículos `KEEP`:

KEEP  
→ obtener contexto técnico adicional  
→ README / contenido relevante  
→ Summarizer LLM  
→ resumen técnico útil  
→ digest

El summarizer debería producir aproximadamente:

- qué es
- qué problema resuelve
- arquitectura/patrones interesantes
- por qué importa para el perfil del usuario
- qué debería revisar o aprender
- enlace original

El classifier, investigator y summarizer deben permanecer como responsabilidades separadas.

---

## Regla para otro modelo colaborador

Antes de modificar arquitectura:

1. Entender el flujo actual.
2. No agregar frameworks innecesariamente.
3. Mantener compatibilidad con el pipeline funcionando.
4. Explicar qué problema resuelve cada cambio.
5. Favorecer componentes reemplazables.
6. Mantener debug visible mientras el proyecto siga siendo educativo.
7. No saltar directamente a LangGraph/MCP/RAG sin conectar el concepto con un problema real del proyecto.
