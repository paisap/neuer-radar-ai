from __future__ import annotations

from neuer_radar.core.models import Article, UserProfile

SYSTEM_PROMPT = (
    "Estamos probando tool calling.\n"
    "Debes usar la herramienta get_github_readme "
    "cuando el usuario te pida leer un repositorio. "
    "No inventes el contenido del README."
    # "Eres un clasificador estricto de noticias técnicas. "
    # "Debes responder únicamente JSON válido. "
    # "No uses markdown. No expliques fuera del JSON. "
    # "Evalúa si el artículo le sirve a Santiago para sus objetivos."
)


def build_classification_prompt(article: Article, profile: UserProfile) -> str:
    return (
        "Lee el README de este repositorio usando "
        "get_github_readme:\n"
        #"https://github.com/alibaba/open-code-review\n\n"
        "Necesito información técnica del proyecto."
        # "Criterio:\n"
        # "- Prioriza AI agents, LangGraph, DevOps automation, AWS, Python, "
        # "LLMOps, RAG, platform engineering, security, observability y trabajo remoto.\n"
        # "- Penaliza hype genérico, crypto sin relación, frontend puro, noticias vagas "
        # "y contenido que no ayude a construir habilidades o proyectos.\n"
        # "Si la información disponible no es suficiente para tomar una decisión fuerte, "
        # "usa 'maybe' en lugar de asumir 'skip'.\n"
        # "No exijas que el contenido sea un tutorial ni que utilice Python. Proyectos en "
        # "otros lenguajes pueden ser relevantes si contienen arquitecturas, patrones o "
        # "técnicas transferibles a los objetivos del usuario.\n"
        # "- Si el artículo proviene de GitHub y la metadata no contiene"
        # "información suficiente para evaluar su arquitectura o utilidad,"
        # "usa la herramienta get_github_readme antes de tomar una decisión.\n"
        # "- No solicites la herramienta si la metadata ya permite tomar una"
        # " decisión clara.\n"
        # "Metricas de decisión:\n"
        # "- relevance_score entre 0 y 39 implica 'skip'.\n"
        # "- relevance_score entre 40 y 69 implica 'maybe'.\n"
        # "- relevance_score entre 70 y 100 implica 'keep'.\n"
        # "- decision y relevance_score deben ser coherentes.\n"
        # "- Usa 'keep' solo si realmente vale la pena leerlo.\n"
        # "- Usa 'maybe' si podría servir pero falta contexto.\n"
        # "- Usa 'skip' si no aporta.\n\n"
        # "Si la metadata no permite comprender qué hace técnicamente"
        # "un repositorio GitHub, utiliza get_github_readme antes"
        # "de decidir.\n\n"
        # "Artículo:\n"
        # f"- Título: {article.title}\n"
        # f"- Fuente: {article.source_name}\n"
        # f"- Categoría: {article.source_category}\n"
         f"- URL: {article.link}\n"
        # f"- Resumen/metadata: {article.summary}\n"
        # f"- Tags: {', '.join(article.tags)}\n\n"
        # "Contenido ampliado:\n"
        # f"{article.content_excerpt}\n\n"
        
        # "Devuelve JSON con estos campos:\n"
        # "- decision\n"
        # "- relevance_score\n"
        # "- reason: explicación corta en español\n"
        # "- angle: cómo Santiago podría usarlo o por qué importa"
    )
