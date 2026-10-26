from __future__ import annotations

import logging
from typing import Any

from adapters.llm import BaseLLMAdapter, get_llm_adapter

from .facts_builder import build_evaluation_facts
from .models import AdvisoryOutput
from .templates import generate_template_advisory
from .validator import validate_advisory_numbers

logger = logging.getLogger(__name__)

PROMPT_VERSION = "v1.0-2026-04"


async def generate_advisory_for_evaluation(
    case_id: int,
    eval_output: dict[str, Any],
    input_snapshot: dict[str, Any],
    language: str = "mr",
    adapter: BaseLLMAdapter | None = None,
) -> tuple[AdvisoryOutput, bool, str]:
    """
    Generate an AI advisory report grounded strictly in evaluation facts.
    Workflow:
      1. Extract evaluation facts.
      2. Call LLM adapter.
      3. Validate output numbers against allowed facts.
      4. If invalid: retry generation once with targeted error feedback.
      5. If retry fails or LLM errors: fall back to guaranteed template generator.
    Returns: (AdvisoryOutput, validator_passed, model_source)
    """
    llm = adapter or get_llm_adapter()
    facts = build_evaluation_facts(
        case_id=case_id,
        eval_output=eval_output,
        input_snapshot=input_snapshot,
        language=language,
    )

    village_name = facts.village_name or "गावात"

    # Attempt 1: Initial LLM Generation
    try:
        raw_advisory = await llm.generate_advisory_text(
            facts=facts.model_dump(),
            language=language,
        )
        is_valid, bad_nums = validate_advisory_numbers(raw_advisory, facts.allowed_numbers)
        if is_valid:
            return AdvisoryOutput.model_validate(raw_advisory), True, "llm"

        logger.warning(
            f"Advisory generation attempt 1 failed validation for case {case_id}: unauthorized numbers {bad_nums}"
        )

        # Attempt 2: One Regeneration Retry with Feedback
        feedback = f"The previous output contained unauthorized numbers not in facts: {bad_nums}. Use ONLY facts."
        retry_advisory = await llm.generate_advisory_text(
            facts=facts.model_dump(),
            language=language,
            retry_feedback=feedback,
        )
        retry_valid, retry_bad_nums = validate_advisory_numbers(retry_advisory, facts.allowed_numbers)
        if retry_valid:
            return AdvisoryOutput.model_validate(retry_advisory), True, "llm_retry"

        logger.warning(
            f"Advisory generation attempt 2 failed validation for case {case_id}: {retry_bad_nums}. Triggering template fallback."
        )

    except Exception as e:
        logger.error(f"Error during LLM advisory generation for case {case_id}: {e}. Triggering template fallback.")

    # Fallback: Guaranteed deterministic template generator
    fallback_output = generate_template_advisory(
        eval_output=eval_output,
        village_name=village_name,
        language=language,
    )
    return fallback_output, True, "template_fallback"
