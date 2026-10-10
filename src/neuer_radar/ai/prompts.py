from __future__ import annotations

from neuer_radar.core.models import Article, UserProfile

# Un "skip" es definitivo: el router no enriquece ni investiga ese artículo.
# Un falso skip pierde contenido valioso; un falso "maybe" solo cuesta un README extra.
SYSTEM_PROMPT = """
Eres un clasificador de artículos técnicos para un radar personal.
Tu única tarea: asignar un relevance_score (0-100) y la decision que corresponde.

Reglas obligatorias:
- Responde únicamente con JSON válido. Sin markdown ni texto fuera del JSON.
- No llames herramientas. No tienes acceso a herramientas.
- Usa solo la información que aparece en el artículo. No inventes detalles.
- La decision se deriva del relevance_score según los rangos indicados.
- Un "skip" es definitivo. Si dudas entre skip y maybe, elige maybe.
- "keep" es solo para contenido claramente valioso, accionable o estratégico.
- reason: máximo 2 frases. angle: 1 frase.
""".strip()


def build_classification_prompt(
    article: Article, profile: UserProfile | None = None
) -> str:
    # `profile` se acepta por compatibilidad con el pipeline, pero este prompt aún
    # no lo usa: los criterios están escritos abajo.
    tags = ", ".join(dict.fromkeys(article.tags)) or "-"
    excerpt = (article.content_excerpt or "").strip() or "(sin contenido ampliado)"

    return f"""
    Clasifica el siguiente artículo para el radar técnico del usuario.

    TEMAS PRIORITARIOS:
    AI agents, LangGraph, LLMOps, RAG, MCP, AWS, DevOps automation, platform
    engineering, Python backend, security, observability, trabajo remoto.

    TEMAS A PENALIZAR:
    hype genérico, crypto sin relación, frontend puro, tutoriales básicos,
    noticias vagas y contenido que no ayude a construir habilidades o proyectos.

    RÚBRICA:
    - 70-100 => "keep": el tema central es prioritario y el artículo muestra
      sustancia técnica (arquitectura, patrones, código o resultados reales).
    - 40-69  => "maybe": el tema central es prioritario pero falta sustancia visible
      (metadata escasa, sin detalles), o es un caso dudoso.
    - 0-39   => "skip": fuera de los temas prioritarios, o es ruido.

    REGLAS ESPECIALES:
    - Si es un repositorio de GitHub y su tema central es prioritario, el score
      mínimo es 40, aunque la metadata no permita ver su arquitectura. El pipeline
      lo enriquecerá con el README después.
    - No exijas que sea un tutorial ni que use Python. Otros lenguajes valen si
      aportan arquitectura o patrones transferibles.
    - decision y relevance_score deben ser coherentes con la rúbrica.

    EJEMPLOS:
    - Repo en Rust: "runtime seguro para agentes autónomos", sin README
      => maybe, 58 (agentes y seguridad; falta ver la arquitectura).
    - Librería de componentes React => skip, 8 (frontend puro).

    ARTÍCULO:
    - Título: {article.title}
    - Fuente: {article.source_name}
    - Categoría: {article.source_category}
    - URL: {article.link}
    - Resumen/metadata: {article.summary}
    - Tags: {tags}

    CONTENIDO AMPLIADO:
    {excerpt}

    Devuelve JSON con exactamente estos campos:
    - decision: "skip" | "maybe" | "keep"
    - relevance_score: número entero entre 0 y 100
    - reason: explicación corta en español (máximo 2 frases)
    - angle: cómo podría usarlo el usuario o por qué importa (1 frase)
    """.strip()


# ============================================================
# INVESTIGACIÓN CON TOOLS  (usado por investigate_article_with_tools)
# ============================================================

INVESTIGATION_SYSTEM_PROMPT = """
Eres un investigador técnico de repositorios de GitHub.
Contexto: una primera clasificación marcó este repositorio como "maybe"
porque la metadata no alcanza para juzgarlo.

Tu única tarea en este paso: conseguir la evidencia que falta. Para eso
puedes pedir el README con la herramienta get_github_readme.

Reglas:
- Por defecto, llama a get_github_readme con la URL del repositorio.
- Omite la herramienta solo si la metadata ya describe con claridad qué hace
  el proyecto y cómo está construido.
- No inventes información.
- No clasifiques todavía: la decisión final se pide en un paso posterior.
""".strip()


def build_investigation_prompt(
    article: Article,
    profile: UserProfile,
    initial_decision: str,
    initial_score: int,
    initial_reason: str,
) -> str:
    # Recibe valores sueltos (no AiArticleDecision) para no importar classifier.py
    # desde aquí y evitar un import circular.
    return (
        f"Repositorio: {article.title}\n"
        f"URL: {article.link}\n"
        f"Metadata: {article.summary}\n\n"
        "Clasificación inicial:\n"
        f"- Decision: {initial_decision}\n"
        f"- Score: {initial_score}\n"
        f"- Reason: {initial_reason}\n\n"
        "Perfil:\n"
        f"- Intereses: {', '.join(profile.interests)}\n"
        f"- Objetivos: {', '.join(profile.goals)}\n\n"
        "Obtén el README para evaluar la arquitectura y la utilidad real del "
        "proyecto, salvo que la metadata ya sea suficiente."
    )


# Se agrega como último mensaje de usuario, después de los resultados de las tools.
FINAL_CLASSIFICATION_PROMPT = """
Ya tienes la información obtenida por las herramientas.
Realiza ahora la clasificación final del repositorio.

Rúbrica:
- 70-100 => "keep": el tema es relevante para el perfil y la evidencia muestra
  sustancia técnica (arquitectura, patrones, código o uso real).
- 40-69  => "maybe": solo si, incluso con el README, sigue sin estar claro lo
  importante.
- 0-39   => "skip": no aporta al perfil o es ruido.

Reglas:
- Basa tu decisión únicamente en la evidencia disponible (README y metadata).
- No inventes información.
- decision y relevance_score deben ser coherentes con la rúbrica.
- reason: máximo 2 frases. angle: 1 frase.

Devuelve JSON con exactamente estos campos:
decision, relevance_score, reason, angle.
""".strip()
