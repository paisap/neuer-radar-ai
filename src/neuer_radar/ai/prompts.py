from __future__ import annotations

from neuer_radar.core.models import Article, UserProfile

SYSTEM_PROMPT = (
    "Eres un clasificador estricto de noticias técnicas. "
    "Debes responder únicamente JSON válido. "
    "No uses markdown. No expliques fuera del JSON. "
    "Evalúa si el artículo le sirve a Santiago para sus objetivos."
)


def build_classification_prompt(article: Article, profile: UserProfile) -> str:
    return (
        "Perfil de Santiago:\n"
        f"- Intereses: {', '.join(profile.interests)}\n"
        f"- Evitar: {', '.join(profile.avoid)}\n"
        f"- Objetivos: {', '.join(profile.goals)}\n\n"
        "Criterio:\n"
        "- Prioriza AI agents, LangGraph, DevOps automation, AWS, Python, "
        "LLMOps, RAG, platform engineering, security, observability y trabajo remoto.\n"
        "- Penaliza hype genérico, crypto sin relación, frontend puro, noticias vagas "
        "y contenido que no ayude a construir habilidades o proyectos.\n"
        "Si la información disponible no es suficiente para tomar una decisión fuerte, "
        "usa 'maybe' en lugar de asumir 'skip'.\n"
        "No exijas que el contenido sea un tutorial ni que utilice Python. Proyectos en "
        "otros lenguajes pueden ser relevantes si contienen arquitecturas, patrones o "
        "técnicas transferibles a los objetivos del usuario.\n"
        "- Usa 'keep' solo si realmente vale la pena leerlo.\n"
        "- Usa 'maybe' si podría servir pero falta contexto.\n"
        "- Usa 'skip' si no aporta.\n\n"
        "Artículo:\n"
        f"- Título: {article.title}\n"
        f"- Fuente: {article.source_name}\n"
        f"- Categoría: {article.source_category}\n"
        f"- URL: {article.link}\n"
        f"- Resumen/metadata: {article.summary}\n"
        f"- Tags: {', '.join(article.tags)}\n\n"
        "Contenido ampliado:\n"
        f"{article.content_excerpt}\n\n"
        
        "Devuelve JSON con estos campos:\n"
        "- decision\n"
        "- relevance_score\n"
        "- reason: explicación corta en español\n"
        "- angle: cómo Santiago podría usarlo o por qué importa"
    )
