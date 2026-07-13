from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from neuer_radar.ai.providers.factory import get_llm_provider
from neuer_radar.core.models import Article, UserProfile


class AiArticleDecision(BaseModel):
    decision: Literal["keep", "skip", "maybe"]
    relevance_score: int = Field(ge=0, le=100)
    reason: str
    angle: str


ARTICLE_CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {
            "type": "string",
            "enum": ["keep", "skip", "maybe"],
        },
        "relevance_score": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100,
        },
        "reason": {
            "type": "string",
        },
        "angle": {
            "type": "string",
        },
    },
    "required": ["decision", "relevance_score", "reason", "angle"],
}


def classify_article_with_ai(
    article: Article,
    profile: UserProfile,
) -> AiArticleDecision:
    provider = get_llm_provider()

    messages = [
        {
            "role": "system",
            "content": (
                "Eres un clasificador estricto de noticias técnicas. "
                "Debes responder únicamente JSON válido. "
                "No uses markdown. No expliques fuera del JSON. "
                "Evalúa si el artículo le sirve a Santiago para sus objetivos."
            ),
        },
        {
            "role": "user",
            "content": (
                "Perfil de Santiago:\n"
                f"- Intereses: {', '.join(profile.interests)}\n"
                f"- Evitar: {', '.join(profile.avoid)}\n"
                f"- Objetivos: {', '.join(profile.goals)}\n\n"
                "Criterio:\n"
                "- Prioriza AI agents, LangGraph, DevOps automation, AWS, Python, "
                "LLMOps, RAG, platform engineering, security, observability y trabajo remoto.\n"
                "- Penaliza hype genérico, crypto sin relación, frontend puro, noticias vagas "
                "y contenido que no ayude a construir habilidades o proyectos.\n"
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
                "Devuelve JSON con estos campos:\n"
                "- decision\n"
                "- relevance_score\n"
                "- reason: explicación corta en español\n"
                "- angle: cómo Santiago podría usarlo o por qué importa"
            ),
        },
    ]

    raw_decision = provider.complete_json(
        messages=messages,
        schema=ARTICLE_CLASSIFICATION_SCHEMA,
    )

    decision = AiArticleDecision.model_validate(raw_decision)

    if not decision.reason.strip():
        decision.reason = "El modelo no explicó la razón; revisar manualmente."

    if not decision.angle.strip():
        decision.angle = "Sin ángulo claro; revisar si realmente aporta."

    return decision
