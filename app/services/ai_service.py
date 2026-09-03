"""
AI Chat Service and Context Injection Engine.

Orchestrates:
1. Retrieval of current energy summary from Firestore data via EnergyDataService.
2. Building an anti-hallucination System Prompt with injected JSON summary context.
3. Querying OpenAI Chat Completions API with error handling and fallback modes.
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.models.chat_models import ChatRequest, ChatResponse
from app.services.data_service import EnergyDataService

logger = logging.getLogger("app.services.ai_service")


def build_system_prompt(summary_data: Dict[str, Any]) -> str:
    """
    Constructs the system prompt with strict anti-hallucination rules and injected energy summary.
    """
    summary_json_str = json.dumps(summary_data, indent=2)

    prompt = f"""You are an intelligent, precise AI personal electricity-consumption assistant.
Your goal is to answer the user's questions about their historical electricity usage data accurately.

=== ENERGY CONSUMPTION SUMMARY CONTEXT ===
{summary_json_str}
==========================================

STRICT ANTI-HALLUCINATION RULES:
1. Rely ONLY on the information provided in the summary above.
2. Do NOT fabricate, invent, or extrapolate numeric values, dates, trends, averages, or costs.
3. Do NOT provide or estimate a specific day's consumption (e.g. "What was my usage on July 14?") unless that specific day is explicitly stated in the summary (such as in 'extremes'). If the specific date is not in the summary, explicitly inform the user that this specific date's detail is not in the high-level summary and would require a direct database lookup.
4. If a user asks about dates outside the analysis period ({summary_data.get('period', {}).get('start_date', '2026-03-01')} to {summary_data.get('period', {}).get('end_date', '2026-08-31')}), clearly state that data is only available for the recorded period.
5. Always use "kWh" or "kWh/day" as the unit for electricity consumption.
6. If discussing costs, clearly state that the cost values are "estimated costs" based on unit rates and do NOT represent confirmed or final utility bills.
7. Do not infer a missing value as zero or make assumptions about unlisted metrics.
8. Maintain a helpful, polite, and data-grounded tone. Answer in the same language as the user's question (e.g. Korean if asked in Korean, English if asked in English).
"""
    return prompt


class AIChatService:
    @staticmethod
    def _get_openai_client():
        try:
            from openai import OpenAI
            if not settings.OPENAI_API_KEY:
                return None
            return OpenAI(api_key=settings.OPENAI_API_KEY)
        except ImportError:
            logger.warning("openai package not installed.")
            return None

    @classmethod
    async def process_chat(cls, request: ChatRequest) -> ChatResponse:
        """
        Executes the context-injected chat flow.
        """
        # 1. Generate current energy summary from database
        summary_response = EnergyDataService.get_summary()
        summary_data = summary_response.model_dump()

        # 2. Build anti-hallucination system prompt with injected context
        system_prompt = build_system_prompt(summary_data)

        # 3. Generate conversation ID if absent
        conv_id = request.conversation_id or str(uuid.uuid4())

        # 4. Check OpenAI API availability
        client = cls._get_openai_client()
        now_str = datetime.now(timezone.utc).isoformat()

        if client is None or not settings.OPENAI_API_KEY:
            # Deterministic local rule-based response when OpenAI API Key is not set
            reply = cls._generate_mock_or_offline_reply(request.message, summary_data)
            return ChatResponse(
                conversation_id=conv_id,
                reply=reply,
                used_summary=True,
                created_at=now_str
            )

        try:
            # Call OpenAI Chat Completion
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.message}
                ],
                temperature=0.1,  # Low temperature for factual precision
                max_tokens=800
            )
            reply = response.choices[0].message.content.strip()

            return ChatResponse(
                conversation_id=conv_id,
                reply=reply,
                used_summary=True,
                created_at=now_str
            )

        except Exception as e:
            logger.error(f"OpenAI API invocation failed: {e}")
            # Graceful error handling
            return ChatResponse(
                conversation_id=conv_id,
                reply=f"AI service temporarily unavailable due to upstream provider error: {str(e)}",
                used_summary=True,
                created_at=now_str
            )

    @staticmethod
    def _generate_mock_or_offline_reply(user_msg: str, summary: Dict[str, Any]) -> str:
        """
        Offline fallback matching anti-hallucination rules for testing environments without active API keys.
        """
        msg = user_msg.lower()
        overall = summary.get("overall", {})
        extremes = summary.get("extremes", {})
        period = summary.get("period", {})
        trend = summary.get("trend", {})
        dow = summary.get("day_of_week", {})
        ww = summary.get("weekday_weekend", {})
        monthly = summary.get("monthly", {})
        cost = summary.get("cost", {})

        if "month" in msg or "월별" in msg or "월" in msg:
            h_month = monthly.get("highest_total_month", {})
            return f"The month with the highest electricity usage was {h_month.get('month')} with a total of {h_month.get('total_consumption_kwh')} kWh."

        if "average" in msg or "평균" in msg:
            return f"Your overall average daily electricity consumption is {overall.get('average_daily_consumption_kwh')} kWh/day across {period.get('duration_days')} days ({period.get('start_date')} to {period.get('end_date')})."

        if "highest" in msg or "maximum" in msg or "최대" in msg or "가장 많이" in msg:
            max_day = extremes.get("maximum_day", {})
            return f"Your highest consumption day was {max_day.get('date')} ({max_day.get('day_of_week')}) with {max_day.get('consumption_kwh')} kWh."

        if "lowest" in msg or "minimum" in msg or "최소" in msg or "가장 적게" in msg:
            min_day = extremes.get("minimum_day", {})
            return f"Your lowest consumption day was {min_day.get('date')} ({min_day.get('day_of_week')}) with {min_day.get('consumption_kwh')} kWh."

        if "weekend" in msg or "weekday" in msg or "주말" in msg or "평일" in msg:
            return f"Your weekday average is {ww.get('weekday_average_kwh')} kWh/day and weekend average is {ww.get('weekend_average_kwh')} kWh/day ({ww.get('pattern_description')})."

        if "trend" in msg or "추세" in msg or "트렌드" in msg:
            st = trend.get("short_term_trend", {})
            ot = trend.get("overall_trend", {})
            return f"Short-term trend (last 7 days): {st.get('direction')} ({st.get('percentage_change')}%), Overall trend: {ot.get('direction')} (linear slope: {ot.get('linear_slope_kwh_per_day')} kWh/day)."

        if "cost" in msg or "비용" in msg or "요금" in msg:
            return f"Total estimated cost is £{cost.get('total_estimated_cost_gbp')} ({cost.get('total_estimated_cost_pence')}p). Note: {cost.get('disclaimer')}."

        # Specific dates or outside range
        return (
            f"I only have access to high-level summary metrics for the period {period.get('start_date')} to {period.get('end_date')}. "
            "Specific single-day details or data outside this period are not included in the summary and require a direct database query."
        )
