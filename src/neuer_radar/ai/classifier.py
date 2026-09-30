from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, Field

from neuer_radar.ai.prompts import SYSTEM_PROMPT, build_classification_prompt
from neuer_radar.ai.providers.factory import get_llm_provider
from neuer_radar.ai.tools.registry import (
    AVAILABLE_TOOL_SCHEMAS,
    execute_tool,
)
from neuer_radar.core.models import Article, ScoredArticle, UserProfile


# ============================================================
# MODELO DE SALIDA DEL LLM
# ============================================================

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
    "required": [
        "decision",
        "relevance_score",
        "reason",
        "angle",
    ],
}


# ============================================================
# DEBUG
# ============================================================

def _print_messages(
    title: str,
    messages: list[dict[str, Any]],
) -> None:

    print(f"\n================ {title} ================")

    for index, message in enumerate(messages, start=1):
        print(f"\nMESSAGE {index}")
        print(f"ROLE: {message.get('role', '').upper()}")

        content = message.get("content")

        if content:
            print(content)

        tool_calls = message.get("tool_calls")

        if tool_calls:
            print("\nTOOL CALLS:")
            print(
                json.dumps(
                    tool_calls,
                    indent=2,
                    ensure_ascii=False,
                )
            )

    print("===========================================\n")


def _print_decision(
    title: str,
    decision: AiArticleDecision,
) -> None:

    print(f"\n================ {title} ================")
    print(f"DECISION: {decision.decision}")
    print(f"SCORE: {decision.relevance_score}")
    print(f"REASON: {decision.reason}")
    print(f"ANGLE: {decision.angle}")
    print("===========================================\n")


# ============================================================
# VALIDACIÓN / NORMALIZACIÓN
# ============================================================

def _normalize_decision(
    decision: AiArticleDecision,
) -> AiArticleDecision:
    """
    Evita incoherencias como:
        keep + score 9
        skip + score 95

    El score determina la categoría final.
    """

    score = decision.relevance_score

    if score >= 70:
        expected = "keep"
    elif score >= 40:
        expected = "maybe"
    else:
        expected = "skip"

    if decision.decision != expected:

        print("\n========== DECISION NORMALIZATION ==========")
        print(
            f"Model returned: "
            f"{decision.decision} / {decision.relevance_score}"
        )
        print(
            f"Normalized to: "
            f"{expected} / {decision.relevance_score}"
        )
        print("=============================================\n")

        decision.decision = expected

    return decision


def _validate_ai_decision(
    raw_decision: dict[str, Any],
) -> AiArticleDecision:

    decision = AiArticleDecision.model_validate(
        raw_decision
    )

    if not decision.reason.strip():
        decision.reason = (
            "El modelo no explicó la razón; revisar manualmente."
        )

    if not decision.angle.strip():
        decision.angle = (
            "Sin ángulo claro; revisar si realmente aporta."
        )

    return _normalize_decision(decision)


# ============================================================
# 1. CLASIFICACIÓN NORMAL
# ============================================================

def classify_article_with_ai(
    article: Article,
    profile: UserProfile,
) -> AiArticleDecision:
    """
    Primera clasificación.

    Aquí NO hay tools.

    Article + Profile
            ↓
           LLM
            ↓
       keep/maybe/skip
    """

    provider = get_llm_provider()

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": build_classification_prompt(
                article,
                profile,
            ),
        },
    ]

    _print_messages(
        "INITIAL CLASSIFICATION PROMPT",
        messages,
    )

    raw_decision = provider.complete_json(
        messages=messages,
        schema=ARTICLE_CLASSIFICATION_SCHEMA,
    )

    print("\n========== RAW INITIAL DECISION ==========")
    print(
        json.dumps(
            raw_decision,
            indent=2,
            ensure_ascii=False,
        )
    )
    print("==========================================\n")

    decision = _validate_ai_decision(
        raw_decision
    )

    _print_decision(
        "INITIAL AI DECISION",
        decision,
    )

    return decision


# ============================================================
# 2. INVESTIGACIÓN CON TOOLS
# ============================================================

def investigate_article_with_tools(
    article: Article,
    profile: UserProfile,
    initial_decision: AiArticleDecision,
) -> AiArticleDecision:
    """
    Solo llegamos aquí cuando la primera clasificación
    no tiene suficiente certeza.

    MAYBE
      ↓
    preguntar al modelo si necesita tools
      ↓
    ejecutar tool
      ↓
    devolver resultado al modelo
      ↓
    clasificación final
    """

    provider = get_llm_provider()

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "Eres un investigador técnico. "
                "Una clasificación inicial determinó que "
                "el proyecto es incierto. "
                "Puedes utilizar herramientas para obtener "
                "evidencia adicional antes de tomar una "
                "decisión final. "
                "No inventes información. "
                "Si necesitas comprender mejor un repositorio "
                "GitHub, utiliza get_github_readme."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Repositorio: {article.title}\n"
                f"URL: {article.link}\n"
                f"Metadata: {article.summary}\n\n"

                "Clasificación inicial:\n"
                f"- Decision: {initial_decision.decision}\n"
                f"- Score: {initial_decision.relevance_score}\n"
                f"- Reason: {initial_decision.reason}\n\n"

                "Perfil:\n"
                f"- Intereses: {', '.join(profile.interests)}\n"
                f"- Objetivos: {', '.join(profile.goals)}\n\n"

                "Investiga solamente si necesitas información "
                "adicional para tomar una decisión mejor."
            ),
        },
    ]

    _print_messages(
        "INVESTIGATION PROMPT",
        messages,
    )

    print("\n========== AVAILABLE TOOLS ==========")

    print(
        json.dumps(
            AVAILABLE_TOOL_SCHEMAS,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("=====================================\n")

    tool_message = provider.chat_with_tools(
        messages=messages,
        tools=AVAILABLE_TOOL_SCHEMAS,
    )

    print("\n========== RAW TOOL MESSAGE ==========")

    print(
        json.dumps(
            tool_message,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("======================================\n")

    tool_calls = tool_message.get(
        "tool_calls",
        [],
    )

    # --------------------------------------------------------
    # MODELO DECIDIÓ NO USAR TOOLS
    # --------------------------------------------------------

    if not tool_calls:

        print("\n========== TOOL ROUTE ==========")
        print("MODEL DECISION: NO TOOL")
        print("Returning initial MAYBE decision.")
        print("================================\n")

        return initial_decision

    # --------------------------------------------------------
    # MODELO DECIDIÓ USAR TOOLS
    # --------------------------------------------------------

    print("\n========== TOOL ROUTE ==========")
    print(
        f"MODEL DECISION: USE TOOL "
        f"({len(tool_calls)} requested)"
    )
    print("================================\n")

    # Guardamos el mensaje del assistant que pidió la tool.
    messages.append(tool_message)

    for index, call in enumerate(
        tool_calls,
        start=1,
    ):

        function = call.get(
            "function",
            {},
        )

        tool_name = function.get(
            "name",
        )

        arguments = function.get(
            "arguments",
            {},
        )

        if isinstance(arguments, str):
            arguments = json.loads(
                arguments
            )

        print(
            f"\n========== EXECUTING TOOL #{index} =========="
        )

        print(f"NAME: {tool_name}")

        print(
            "ARGUMENTS:",
            json.dumps(
                arguments,
                indent=2,
                ensure_ascii=False,
            ),
        )

        result = execute_tool(
            name=tool_name,
            arguments=arguments,
        )

        print(f"\nRESULT CHARS: {len(result)}")

        print("\n--- RESULT PREVIEW ---")
        print(result[:1500])

        if len(result) > 1500:
            print("\n...[debug preview truncated]")

        print(
            "\n=============================================\n"
        )

        # La respuesta REAL de Python vuelve al LLM.
        messages.append(
            {
                "role": "tool",
                "tool_name": tool_name,
                "content": result,
            }
        )

    # --------------------------------------------------------
    # AHORA EL MODELO TIENE NUEVA INFORMACIÓN
    # --------------------------------------------------------

    messages.append(
        {
            "role": "user",
            "content": (
                "Ahora que tienes la información obtenida "
                "por las herramientas, realiza la clasificación "
                "final.\n\n"
                "Usa estas reglas:\n"
                "- 0-39 = skip\n"
                "- 40-69 = maybe\n"
                "- 70-100 = keep\n"
                "- decision y relevance_score deben ser "
                "coherentes.\n"
                "- Basa tu decisión en la evidencia disponible."
            ),
        }
    )

    _print_messages(
        "FINAL CLASSIFICATION AFTER TOOLS",
        messages,
    )

    raw_decision = provider.complete_json(
        messages=messages,
        schema=ARTICLE_CLASSIFICATION_SCHEMA,
    )

    print("\n========== RAW FINAL DECISION ==========")

    print(
        json.dumps(
            raw_decision,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("========================================\n")

    decision = _validate_ai_decision(
        raw_decision
    )

    _print_decision(
        "FINAL AI DECISION",
        decision,
    )

    return decision


# ============================================================
# 3. ROUTER / ORQUESTADOR
# ============================================================

def refine_articles_with_ai(
    scored_articles: list[ScoredArticle],
    profile: UserProfile,
) -> list[ScoredArticle]:
    """
    Coordina todo el proceso:

    heurística
        ↓
    clasificación LLM
        ↓
    router
        ↓
    maybe + GitHub → tools
    keep/skip      → finish
    """

    refined: list[ScoredArticle] = []

    for item in scored_articles:

        print("\n\n############################################")
        print(f"ARTICLE: {item.article.title}")
        print(f"HEURISTIC SCORE: {item.relevance_score}")
        print(f"HEURISTIC DECISION: {item.decision}")
        print("############################################\n")

        # El filtro barato ya lo descartó.
        if item.decision == "skip":

            print(
                "ROUTE: HEURISTIC SKIP → "
                "NO LLM / NO TOOL\n"
            )

            refined.append(item)

            continue

        # ----------------------------------------------------
        # Primera evaluación por IA
        # ----------------------------------------------------

        initial_decision = classify_article_with_ai(
            article=item.article,
            profile=profile,
        )

        print("\n========== ROUTER ==========")
        print(f"Article: {item.article.title}")
        print(
            f"Initial decision: "
            f"{initial_decision.decision}"
        )
        print(
            f"Initial score: "
            f"{initial_decision.relevance_score}"
        )

        # ----------------------------------------------------
        # MAYBE + GitHub → investigar
        # ----------------------------------------------------

        if (
            initial_decision.decision == "maybe"
            and item.article.source_category
            == "github-trending"
        ):

            print(
                "Route selected: "
                "INVESTIGATE_WITH_TOOLS"
            )

            final_decision = investigate_article_with_tools(
                article=item.article,
                profile=profile,
                initial_decision=initial_decision,
            )

        # ----------------------------------------------------
        # KEEP / SKIP / maybe no GitHub → terminar
        # ----------------------------------------------------

        else:

            print(
                "Route selected: FINISH"
            )

            final_decision = initial_decision

        print("================================\n")

        # ----------------------------------------------------
        # Resultado final del artículo
        # ----------------------------------------------------

        print("\n================ FINAL RESULT ================")
        print(f"TITLE: {item.article.title}")
        print(
            f"HEURISTIC SCORE: "
            f"{item.relevance_score}"
        )
        print(
            f"FINAL AI DECISION: "
            f"{final_decision.decision}"
        )
        print(
            f"FINAL AI SCORE: "
            f"{final_decision.relevance_score}"
        )
        print(
            f"REASON: "
            f"{final_decision.reason}"
        )
        print(
            f"ANGLE: "
            f"{final_decision.angle}"
        )
        print("==============================================\n")

        refined.append(
            ScoredArticle(
                article=item.article,
                relevance_score=(
                    final_decision.relevance_score
                ),
                reason=(
                    f"{final_decision.reason} "
                    f"| Angle: {final_decision.angle} "
                    f"| Heuristic score: "
                    f"{item.relevance_score}"
                ),
                decision=final_decision.decision,
            )
        )

    return sorted(
        refined,
        key=lambda item: item.relevance_score,
        reverse=True,
    )
