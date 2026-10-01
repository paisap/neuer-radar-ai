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
