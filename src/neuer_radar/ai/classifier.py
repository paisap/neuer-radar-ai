from __future__ import annotations

from typing import Literal

from mypy import messages
from pydantic import BaseModel, Field

from neuer_radar.ai.providers.factory import get_llm_provider
from neuer_radar.core.models import Article, UserProfile
from neuer_radar.core.models import Article, ScoredArticle, UserProfile


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
    print("soy el profile")

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

    print("\n================ PROMPT ===================")

    for message in messages:
        print(f"\nROLE: {message['role'].upper()}")
        print(message["content"])

    print("===========================================\n")
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

def refine_articles_with_ai(
    scored_articles: list[ScoredArticle],
    profile: UserProfile,
) -> list[ScoredArticle]:

    refined: list[ScoredArticle] = []

    for item in scored_articles:
    
        # Si el filtro barato ya considera que no sirve,
        # no gastamos una llamada al LLM.
        if item.decision == "skip":
            refined.append(item)
            continue

        ai_decision = classify_article_with_ai(
            article=item.article,
            profile=profile,
        )

        # # Temporalmente "maybe" lo tratamos como skip.
        # # Luego podemos modelarlo correctamente.
        # final_decision = (
        #     "keep"
        #     if ai_decision.decision == "keep"
        #     else "skip"
        # )
        print("\n================ AI RESULT ================")
        print(f"TITLE: {item.article.title}")
        print(f"HEURISTIC SCORE: {item.relevance_score}")
        print(f"AI DECISION: {ai_decision.decision}")
        print(f"AI SCORE: {ai_decision.relevance_score}")
        print(f"REASON: {ai_decision.reason}")
        print(f"ANGLE: {ai_decision.angle}")
        print("===========================================\n")

        refined.append(
            ScoredArticle(
                article=item.article,
                relevance_score=ai_decision.relevance_score,
                reason=(
                    f"{ai_decision.reason} "
                    f"| Angle: {ai_decision.angle} "
                    f"| Heuristic score: {item.relevance_score}"
                ),
                decision=ai_decision.decision,
            )
        )


    return sorted(
        refined,
        key=lambda item: item.relevance_score,
        reverse=True,
    )