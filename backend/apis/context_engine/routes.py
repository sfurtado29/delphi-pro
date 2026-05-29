#new code  12:19 01052026
# # routes.py
# # ─────────────────────────────────────────────────────────────
# # Two-phase conversation pipeline:
# #
# #   Phase 1 — PRODUCT UNDERSTANDING
# #     Collects product description, name, USPs, pricing tier,
# #     campaign budget, ideal buyer, market type, buyer stage.
# #
# #   Phase 2 — AUDIENCE TARGETING
# #     Collects geography, industry, job function, job level,
# #     employee size, revenue range.
# #     NOTE: industry_domain (sector) is intentionally skipped.
# #
# #   Complete → Cortex → Insight Engine → AI Validator → results
# # ─────────────────────────────────────────────────────────────

# from fastapi import APIRouter
# from pydantic import BaseModel

# from .context_memory    import (
#     get_context, update_context, reset_context,
#     is_complete, get_phase,
# )
# from .context_builder   import build_context
# from .ai_taxonomy_service import (
#     get_next_field,
#     get_conversation_phase,
#     generate_conversational_question,
#     generate_completion_message,
#     FIELD_ORDER,
#     PRODUCT_FIELDS,
#     TARGETING_FIELDS,
# )
# from .intent_analyzer   import is_off_topic, generate_off_topic_reply
# from .prompt_builder    import build_cortex_prompt
# from .cortex_service    import query_cortex_analyst
# from .insight_engine    import run_insight_engine
# from .ai_validator      import validate_and_enrich
# from .suggestion_engine import get_suggestions

# router = APIRouter(prefix="/context", tags=["Context Engine"])


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# class ResetRequest(BaseModel):
#     session_id: str


# # ══════════════════════════════════════════════════════════════
# # CHAT ENDPOINT
# # ══════════════════════════════════════════════════════════════

# @router.post("/chat")
# def chat(req: ChatRequest):
#     session_id = req.session_id
#     user_input = req.message.strip()

#     # ── Load session ──────────────────────────────────────────
#     state   = get_context(session_id)
#     context = state["context"]

#     # ── Extract context from user input (phase-aware) ─────────
#     context = build_context(user_input, context)
#     update_context(session_id, context)

#     print(f"[Session={session_id}] Phase={get_phase(session_id)} Context={context}")

#     # ── Determine next field needed ───────────────────────────
#     next_field = get_next_field(context)
#     phase      = get_conversation_phase(context)

#     # ── Off-topic guard (only in targeting phase — product
#     #    answers are free-form and shouldn't be flagged) ───────
#     if next_field and phase == "targeting" and is_off_topic(user_input):
#         from .ai_taxonomy_service import QUESTION_MAP
#         reply       = generate_off_topic_reply(user_input, context, QUESTION_MAP.get(next_field, ""))
#         suggestions = get_suggestions(context, next_field)
#         return {
#             "status":      "in_progress",
#             "phase":       phase,
#             "context":     context,
#             "response":    reply,
#             "suggestions": suggestions,
#             "next_field":  next_field,
#             "off_topic":   True,
#             "progress":    _progress(context),
#         }

#     # ── Still collecting context ──────────────────────────────
#     if next_field:
#         response    = generate_conversational_question(context, user_input, next_field)
#         # Suggestions only make sense for taxonomy/targeting fields
#         suggestions = get_suggestions(context, next_field) if phase == "targeting" else {}
#         return {
#             "status":      "in_progress",
#             "phase":       phase,
#             "context":     context,
#             "response":    response,
#             "suggestions": suggestions,
#             "next_field":  next_field,
#             "progress":    _progress(context),
#         }

#     # ══════════════════════════════════════════════════════════
#     # BOTH PHASES COMPLETE — RUN FULL PIPELINE
#     # ══════════════════════════════════════════════════════════

#     summary_msg = generate_completion_message(context)

#     # ── Step 1: Cortex query ──────────────────────────────────
#     cortex_prompt = build_cortex_prompt(context, user_input)
#     try:
#         cortex_leads = query_cortex_analyst(cortex_prompt)
#         print(f"[Cortex] Returned {len(cortex_leads)} leads")
#     except Exception as e:
#         print(f"[Cortex Error] {e}")
#         cortex_leads = []

#     if not cortex_leads:
#         return {
#             "status":     "complete",
#             "phase":      "complete",
#             "context":    context,
#             "summary":    summary_msg,
#             "response":   "Snowflake Cortex returned no leads for this criteria. Try broadening your filters.",
#             "leads":      [],
#             "validation": {"valid": False, "notes": "No leads returned from Cortex."},
#             "suggestions": {},
#         }

#     # ── Step 2: Insight Engine ────────────────────────────────
#     try:
#         scored_leads = run_insight_engine(cortex_leads)
#         print(f"[InsightEngine] {len(scored_leads)} leads passed threshold")
#     except Exception as e:
#         print(f"[InsightEngine Error] {e}")
#         scored_leads = []

#     if not scored_leads:
#         return {
#             "status":     "complete",
#             "phase":      "complete",
#             "context":    context,
#             "summary":    summary_msg,
#             "response":   "Leads were found but none scored above the quality threshold. Try adjusting your targeting.",
#             "leads":      [],
#             "validation": {"valid": False, "notes": "No leads cleared the quality threshold."},
#             "suggestions": {},
#         }

#     # ── Step 3: AI Validator + enrichment ────────────────────
#     try:
#         enriched = validate_and_enrich(context, scored_leads)
#     except Exception as e:
#         print(f"[AIValidator Error] {e}")
#         enriched = {
#             "summary":    summary_msg,
#             "validation": {"valid": True, "notes": ""},
#             "leads":      scored_leads,
#         }

#     total_fields = len(FIELD_ORDER)
#     return {
#         "status":     "complete",
#         "phase":      "complete",
#         "context":    context,
#         "summary":    enriched.get("summary", summary_msg),
#         "validation": enriched.get("validation", {}),
#         "leads":      enriched.get("leads", []),
#         "suggestions": {},
#         "progress":   {"filled": total_fields, "total": total_fields, "percent": 100},
#     }


# # ══════════════════════════════════════════════════════════════
# # UTILITY ENDPOINTS
# # ══════════════════════════════════════════════════════════════

# @router.post("/reset")
# def reset(req: ResetRequest):
#     reset_context(req.session_id)
#     return {"status": "reset", "session_id": req.session_id}


# @router.get("/context/{session_id}")
# def get_session_context(session_id: str):
#     state = get_context(session_id)
#     return {
#         "session_id":    session_id,
#         "phase":         get_phase(session_id),
#         "context":       state["context"],
#         "message_count": state.get("message_count", 0),
#         "complete":      is_complete(session_id),
#     }


# # ══════════════════════════════════════════════════════════════
# # HELPERS
# # ══════════════════════════════════════════════════════════════

# def _progress(context: dict) -> dict:
#     filled = sum(1 for f in FIELD_ORDER if context.get(f))
#     total  = len(FIELD_ORDER)
#     return {
#         "filled":  filled,
#         "total":   total,
#         "percent": round(filled / total * 100),
#     }


#14052026 13:00
# routes.py
# ─────────────────────────────────────────────────────────────
# Two-phase conversation pipeline:
#
#   Phase 1 — PRODUCT UNDERSTANDING
#     Collects product description, name, USPs, pricing tier,
#     campaign budget, ideal buyer, market type, buyer stage.
#
#   Phase 2 — AUDIENCE TARGETING
#     Collects geography, industry, job function, job level,
#     employee size, revenue range.
#
#   Complete → Cortex → Insight Engine → AI Validator → results
# ─────────────────────────────────────────────────────────────

# from fastapi import APIRouter
# from pydantic import BaseModel

# from .context_memory import (
#     get_context,
#     update_context,
#     reset_context,
#     is_complete,
# )

# from .context_builder import build_context

# from .ai_taxonomy_service import (
#     get_next_field,
#     get_conversation_phase,
#     generate_conversational_question,
#     generate_completion_message,
#     PRODUCT_FIELDS,
#     TARGETING_FIELDS,
# )

# from .intent_analyzer import (
#     is_off_topic,
#     generate_off_topic_reply,
# )

# from .prompt_builder import build_cortex_prompt
# from .cortex_service import query_cortex_analyst

# # Uncomment later when re-enabled
# # from .insight_engine import run_insight_engine
# # from .ai_validator import validate_and_enrich

# from .suggestion_engine import get_suggestions

# router = APIRouter(
#     prefix="/context",
#     tags=["Context Engine"]
# )


# # ══════════════════════════════════════════════════════════════
# # ACTIVE FIELD ORDER
# # industry_domain intentionally removed
# # ══════════════════════════════════════════════════════════════

# ACTIVE_FIELD_ORDER = [
#     *PRODUCT_FIELDS,

#     "geography",
#     "industry",
#     "job_function",
#     "job_level",
#     "employee_size",
#     "revenue_range",
# ]


# # ══════════════════════════════════════════════════════════════
# # REQUEST MODELS
# # ══════════════════════════════════════════════════════════════

# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# class ResetRequest(BaseModel):
#     session_id: str


# # ══════════════════════════════════════════════════════════════
# # CHAT ENDPOINT
# # ══════════════════════════════════════════════════════════════

# @router.post("/chat")
# def chat(req: ChatRequest):

#     session_id = req.session_id
#     user_input = req.message.strip()

#     # ──────────────────────────────────────────────────────────
#     # LOAD SESSION
#     # ──────────────────────────────────────────────────────────

#     state = get_context(session_id)
#     context = state["context"]

#     # ──────────────────────────────────────────────────────────
#     # DETERMINE CURRENT PHASE
#     # ──────────────────────────────────────────────────────────

#     phase = get_conversation_phase(context)

#     # ──────────────────────────────────────────────────────────
#     # OFF-TOPIC CHECK
#     # Only for targeting phase
#     # ──────────────────────────────────────────────────────────

#     if phase == "targeting" and is_off_topic(user_input):

#         next_field = get_next_field(context)

#         from .ai_taxonomy_service import QUESTION_MAP

#         fallback_question = QUESTION_MAP.get(next_field, "")

#         reply = generate_off_topic_reply(
#             user_input,
#             context,
#             fallback_question,
#         )

#         suggestions = (
#             get_suggestions(context, next_field)
#             if next_field else {}
#         )

#         return {
#             "status": "in_progress",
#             "phase": phase,
#             "context": context,
#             "response": reply,
#             "suggestions": suggestions,
#             "next_field": next_field,
#             "off_topic": True,
#             "progress": _progress(context),
#         }

#     # ──────────────────────────────────────────────────────────
#     # UPDATE CONTEXT
#     # ──────────────────────────────────────────────────────────

#     context = build_context(user_input, context)

#     update_context(session_id, context)

#     # Refresh phase after update
#     phase = get_conversation_phase(context)

#     print(
#         f"[Session={session_id}] "
#         f"Phase={phase} "
#         f"Context={context}"
#     )

#     # ──────────────────────────────────────────────────────────
#     # DETERMINE NEXT FIELD
#     # ──────────────────────────────────────────────────────────

#     next_field = get_next_field(context)

#     # ──────────────────────────────────────────────────────────
#     # STILL COLLECTING CONTEXT
#     # ──────────────────────────────────────────────────────────

#     if next_field:

#         response = generate_conversational_question(
#             context,
#             user_input,
#             next_field,
#         )

#         # Suggestions only for targeting phase
#         suggestions = (
#             get_suggestions(context, next_field)
#             if phase == "targeting"
#             else {}
#         )

#         return {
#             "status": "in_progress",
#             "phase": phase,
#             "context": context,
#             "response": response,
#             "suggestions": suggestions,
#             "next_field": next_field,
#             "progress": _progress(context),
#         }

#     # ══════════════════════════════════════════════════════════
#     # COMPLETE FLOW
#     # ══════════════════════════════════════════════════════════

#     summary_msg = generate_completion_message(context)

#     # ──────────────────────────────────────────────────────────
#     # STEP 1 — BUILD CORTEX PROMPT
#     # ──────────────────────────────────────────────────────────

#     cortex_prompt = build_cortex_prompt(
#         context,
#         user_input,
#     )

#     # ──────────────────────────────────────────────────────────
#     # STEP 2 — QUERY CORTEX
#     # ──────────────────────────────────────────────────────────

#     try:

#         cortex_leads = query_cortex_analyst(cortex_prompt)

#         print(
#             f"[Cortex] Returned "
#             f"{len(cortex_leads)} leads"
#         )

#     except Exception as e:

#         print(f"[Cortex Error] {e}")

#         cortex_leads = []

#     # ──────────────────────────────────────────────────────────
#     # NO LEADS FOUND
#     # ──────────────────────────────────────────────────────────

#     if not cortex_leads:

#         return {
#             "status": "complete",
#             "phase": "complete",
#             "context": context,
#             "summary": summary_msg,
#             "response": (
#                 "Snowflake Cortex returned no leads "
#                 "for this criteria. "
#                 "Try broadening your filters."
#             ),
#             "leads": [],
#             "validation": {
#                 "valid": False,
#                 "notes": "No leads returned from Cortex.",
#             },
#             "suggestions": {},
#             "progress": {
#                 "filled": len(ACTIVE_FIELD_ORDER),
#                 "total": len(ACTIVE_FIELD_ORDER),
#                 "percent": 100,
#             },
#         }

#     # ══════════════════════════════════════════════════════════
#     # FUTURE PIPELINE
#     # ══════════════════════════════════════════════════════════

#     # ── Insight Engine ────────────────────────────────────────
#     #
#     # try:
#     #     scored_leads = run_insight_engine(cortex_leads)
#     #
#     # except Exception as e:
#     #     print(f"[InsightEngine Error] {e}")
#     #     scored_leads = cortex_leads
#     #
#     # ── AI Validator ──────────────────────────────────────────
#     #
#     # try:
#     #     enriched = validate_and_enrich(
#     #         context,
#     #         scored_leads,
#     #     )
#     #
#     # except Exception as e:
#     #     print(f"[AIValidator Error] {e}")
#     #
#     #     enriched = {
#     #         "summary": summary_msg,
#     #         "validation": {
#     #             "valid": True,
#     #             "notes": "",
#     #         },
#     #         "leads": scored_leads,
#     #     }

#     # ══════════════════════════════════════════════════════════
#     # FINAL RESPONSE
#     # ══════════════════════════════════════════════════════════

#     total_fields = len(ACTIVE_FIELD_ORDER)

#     return {
#         "status": "complete",
#         "phase": "complete",
#         "context": context,
#         "summary": summary_msg,
#         "validation": {
#             "valid": True,
#             "notes": "Cortex results returned successfully.",
#         },
#         "leads": cortex_leads,
#         "suggestions": {},
#         "progress": {
#             "filled": total_fields,
#             "total": total_fields,
#             "percent": 100,
#         },
#     }


# # ══════════════════════════════════════════════════════════════
# # RESET SESSION
# # ══════════════════════════════════════════════════════════════

# @router.post("/reset")
# def reset(req: ResetRequest):

#     reset_context(req.session_id)

#     return {
#         "status": "reset",
#         "session_id": req.session_id,
#     }


# # ══════════════════════════════════════════════════════════════
# # GET SESSION CONTEXT
# # ══════════════════════════════════════════════════════════════

# @router.get("/context/{session_id}")
# def get_session_context(session_id: str):

#     state = get_context(session_id)

#     context = state["context"]

#     return {
#         "session_id": session_id,
#         "phase": get_conversation_phase(context),
#         "context": context,
#         "message_count": state.get("message_count", 0),
#         "complete": is_complete(session_id),
#     }


# # ══════════════════════════════════════════════════════════════
# # HELPERS
# # ══════════════════════════════════════════════════════════════

# def _progress(context: dict) -> dict:

#     filled = sum(
#         1 for field in ACTIVE_FIELD_ORDER
#         if context.get(field)
#     )

#     total = len(ACTIVE_FIELD_ORDER)

#     return {
#         "filled": filled,
#         "total": total,
#         "percent": round((filled / total) * 100),
#     }


#new code  12:19 01052026
# # routes.py
# # ─────────────────────────────────────────────────────────────
# # Two-phase conversation pipeline:
# #
# #   Phase 1 — PRODUCT UNDERSTANDING
# #     Collects product description, name, USPs, pricing tier,
# #     campaign budget, ideal buyer, market type, buyer stage.
# #
# #   Phase 2 — AUDIENCE TARGETING
# #     Collects geography, industry, job function, job level,
# #     employee size, revenue range.
# #     NOTE: industry_domain (sector) is intentionally skipped.
# #
# #   Complete → Cortex → Insight Engine → AI Validator → results
# # ─────────────────────────────────────────────────────────────

# from fastapi import APIRouter
# from pydantic import BaseModel

# from .context_memory    import (
#     get_context, update_context, reset_context,
#     is_complete, get_phase,
# )
# from .context_builder   import build_context
# from .ai_taxonomy_service import (
#     get_next_field,
#     get_conversation_phase,
#     generate_conversational_question,
#     generate_completion_message,
#     FIELD_ORDER,
#     PRODUCT_FIELDS,
#     TARGETING_FIELDS,
# )
# from .intent_analyzer   import is_off_topic, generate_off_topic_reply
# from .prompt_builder    import build_cortex_prompt
# from .cortex_service    import query_cortex_analyst
# from .insight_engine    import run_insight_engine
# from .ai_validator      import validate_and_enrich
# from .suggestion_engine import get_suggestions

# router = APIRouter(prefix="/context", tags=["Context Engine"])


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# class ResetRequest(BaseModel):
#     session_id: str


# # ══════════════════════════════════════════════════════════════
# # CHAT ENDPOINT
# # ══════════════════════════════════════════════════════════════

# @router.post("/chat")
# def chat(req: ChatRequest):
#     session_id = req.session_id
#     user_input = req.message.strip()

#     # ── Load session ──────────────────────────────────────────
#     state   = get_context(session_id)
#     context = state["context"]

#     # ── Extract context from user input (phase-aware) ─────────
#     context = build_context(user_input, context)
#     update_context(session_id, context)

#     print(f"[Session={session_id}] Phase={get_phase(session_id)} Context={context}")

#     # ── Determine next field needed ───────────────────────────
#     next_field = get_next_field(context)
#     phase      = get_conversation_phase(context)

#     # ── Off-topic guard (only in targeting phase — product
#     #    answers are free-form and shouldn't be flagged) ───────
#     if next_field and phase == "targeting" and is_off_topic(user_input):
#         from .ai_taxonomy_service import QUESTION_MAP
#         reply       = generate_off_topic_reply(user_input, context, QUESTION_MAP.get(next_field, ""))
#         suggestions = get_suggestions(context, next_field)
#         return {
#             "status":      "in_progress",
#             "phase":       phase,
#             "context":     context,
#             "response":    reply,
#             "suggestions": suggestions,
#             "next_field":  next_field,
#             "off_topic":   True,
#             "progress":    _progress(context),
#         }

#     # ── Still collecting context ──────────────────────────────
#     if next_field:
#         response    = generate_conversational_question(context, user_input, next_field)
#         # Suggestions only make sense for taxonomy/targeting fields
#         suggestions = get_suggestions(context, next_field) if phase == "targeting" else {}
#         return {
#             "status":      "in_progress",
#             "phase":       phase,
#             "context":     context,
#             "response":    response,
#             "suggestions": suggestions,
#             "next_field":  next_field,
#             "progress":    _progress(context),
#         }

#     # ══════════════════════════════════════════════════════════
#     # BOTH PHASES COMPLETE — RUN FULL PIPELINE
#     # ══════════════════════════════════════════════════════════

#     summary_msg = generate_completion_message(context)

#     # ── Step 1: Cortex query ──────────────────────────────────
#     cortex_prompt = build_cortex_prompt(context, user_input)
#     try:
#         cortex_leads = query_cortex_analyst(cortex_prompt)
#         print(f"[Cortex] Returned {len(cortex_leads)} leads")
#     except Exception as e:
#         print(f"[Cortex Error] {e}")
#         cortex_leads = []

#     if not cortex_leads:
#         return {
#             "status":     "complete",
#             "phase":      "complete",
#             "context":    context,
#             "summary":    summary_msg,
#             "response":   "Snowflake Cortex returned no leads for this criteria. Try broadening your filters.",
#             "leads":      [],
#             "validation": {"valid": False, "notes": "No leads returned from Cortex."},
#             "suggestions": {},
#         }

#     # ── Step 2: Insight Engine ────────────────────────────────
#     try:
#         scored_leads = run_insight_engine(cortex_leads)
#         print(f"[InsightEngine] {len(scored_leads)} leads passed threshold")
#     except Exception as e:
#         print(f"[InsightEngine Error] {e}")
#         scored_leads = []

#     if not scored_leads:
#         return {
#             "status":     "complete",
#             "phase":      "complete",
#             "context":    context,
#             "summary":    summary_msg,
#             "response":   "Leads were found but none scored above the quality threshold. Try adjusting your targeting.",
#             "leads":      [],
#             "validation": {"valid": False, "notes": "No leads cleared the quality threshold."},
#             "suggestions": {},
#         }

#     # ── Step 3: AI Validator + enrichment ────────────────────
#     try:
#         enriched = validate_and_enrich(context, scored_leads)
#     except Exception as e:
#         print(f"[AIValidator Error] {e}")
#         enriched = {
#             "summary":    summary_msg,
#             "validation": {"valid": True, "notes": ""},
#             "leads":      scored_leads,
#         }

#     total_fields = len(FIELD_ORDER)
#     return {
#         "status":     "complete",
#         "phase":      "complete",
#         "context":    context,
#         "summary":    enriched.get("summary", summary_msg),
#         "validation": enriched.get("validation", {}),
#         "leads":      enriched.get("leads", []),
#         "suggestions": {},
#         "progress":   {"filled": total_fields, "total": total_fields, "percent": 100},
#     }


# # ══════════════════════════════════════════════════════════════
# # UTILITY ENDPOINTS
# # ══════════════════════════════════════════════════════════════

# @router.post("/reset")
# def reset(req: ResetRequest):
#     reset_context(req.session_id)
#     return {"status": "reset", "session_id": req.session_id}


# @router.get("/context/{session_id}")
# def get_session_context(session_id: str):
#     state = get_context(session_id)
#     return {
#         "session_id":    session_id,
#         "phase":         get_phase(session_id),
#         "context":       state["context"],
#         "message_count": state.get("message_count", 0),
#         "complete":      is_complete(session_id),
#     }


# # ══════════════════════════════════════════════════════════════
# # HELPERS
# # ══════════════════════════════════════════════════════════════

# def _progress(context: dict) -> dict:
#     filled = sum(1 for f in FIELD_ORDER if context.get(f))
#     total  = len(FIELD_ORDER)
#     return {
#         "filled":  filled,
#         "total":   total,
#         "percent": round(filled / total * 100),
#     }


#new code  12:19 01052026
# # routes.py
# # ─────────────────────────────────────────────────────────────
# # Two-phase conversation pipeline:
# #
# #   Phase 1 — PRODUCT UNDERSTANDING
# #     Collects product description, name, USPs, pricing tier,
# #     campaign budget, ideal buyer, market type, buyer stage.
# #
# #   Phase 2 — AUDIENCE TARGETING
# #     Collects geography, industry, job function, job level,
# #     employee size, revenue range.
# #     NOTE: industry_domain (sector) is intentionally skipped.
# #
# #   Complete → Cortex → Insight Engine → AI Validator → results
# # ─────────────────────────────────────────────────────────────

# from fastapi import APIRouter
# from pydantic import BaseModel

# from .context_memory    import (
#     get_context, update_context, reset_context,
#     is_complete, get_phase,
# )
# from .context_builder   import build_context
# from .ai_taxonomy_service import (
#     get_next_field,
#     get_conversation_phase,
#     generate_conversational_question,
#     generate_completion_message,
#     FIELD_ORDER,
#     PRODUCT_FIELDS,
#     TARGETING_FIELDS,
# )
# from .intent_analyzer   import is_off_topic, generate_off_topic_reply
# from .prompt_builder    import build_cortex_prompt
# from .cortex_service    import query_cortex_analyst
# from .insight_engine    import run_insight_engine
# from .ai_validator      import validate_and_enrich
# from .suggestion_engine import get_suggestions

# router = APIRouter(prefix="/context", tags=["Context Engine"])


# class ChatRequest(BaseModel):
#     session_id: str
#     message: str


# class ResetRequest(BaseModel):
#     session_id: str


# # ══════════════════════════════════════════════════════════════
# # CHAT ENDPOINT
# # ══════════════════════════════════════════════════════════════

# @router.post("/chat")
# def chat(req: ChatRequest):
#     session_id = req.session_id
#     user_input = req.message.strip()

#     # ── Load session ──────────────────────────────────────────
#     state   = get_context(session_id)
#     context = state["context"]

#     # ── Extract context from user input (phase-aware) ─────────
#     context = build_context(user_input, context)
#     update_context(session_id, context)

#     print(f"[Session={session_id}] Phase={get_phase(session_id)} Context={context}")

#     # ── Determine next field needed ───────────────────────────
#     next_field = get_next_field(context)
#     phase      = get_conversation_phase(context)

#     # ── Off-topic guard (only in targeting phase — product
#     #    answers are free-form and shouldn't be flagged) ───────
#     if next_field and phase == "targeting" and is_off_topic(user_input):
#         from .ai_taxonomy_service import QUESTION_MAP
#         reply       = generate_off_topic_reply(user_input, context, QUESTION_MAP.get(next_field, ""))
#         suggestions = get_suggestions(context, next_field)
#         return {
#             "status":      "in_progress",
#             "phase":       phase,
#             "context":     context,
#             "response":    reply,
#             "suggestions": suggestions,
#             "next_field":  next_field,
#             "off_topic":   True,
#             "progress":    _progress(context),
#         }

#     # ── Still collecting context ──────────────────────────────
#     if next_field:
#         response    = generate_conversational_question(context, user_input, next_field)
#         # Suggestions only make sense for taxonomy/targeting fields
#         suggestions = get_suggestions(context, next_field) if phase == "targeting" else {}
#         return {
#             "status":      "in_progress",
#             "phase":       phase,
#             "context":     context,
#             "response":    response,
#             "suggestions": suggestions,
#             "next_field":  next_field,
#             "progress":    _progress(context),
#         }

#     # ══════════════════════════════════════════════════════════
#     # BOTH PHASES COMPLETE — RUN FULL PIPELINE
#     # ══════════════════════════════════════════════════════════

#     summary_msg = generate_completion_message(context)

#     # ── Step 1: Cortex query ──────────────────────────────────
#     cortex_prompt = build_cortex_prompt(context, user_input)
#     try:
#         cortex_leads = query_cortex_analyst(cortex_prompt)
#         print(f"[Cortex] Returned {len(cortex_leads)} leads")
#     except Exception as e:
#         print(f"[Cortex Error] {e}")
#         cortex_leads = []

#     if not cortex_leads:
#         return {
#             "status":     "complete",
#             "phase":      "complete",
#             "context":    context,
#             "summary":    summary_msg,
#             "response":   "Snowflake Cortex returned no leads for this criteria. Try broadening your filters.",
#             "leads":      [],
#             "validation": {"valid": False, "notes": "No leads returned from Cortex."},
#             "suggestions": {},
#         }

#     # ── Step 2: Insight Engine ────────────────────────────────
#     try:
#         scored_leads = run_insight_engine(cortex_leads)
#         print(f"[InsightEngine] {len(scored_leads)} leads passed threshold")
#     except Exception as e:
#         print(f"[InsightEngine Error] {e}")
#         scored_leads = []

#     if not scored_leads:
#         return {
#             "status":     "complete",
#             "phase":      "complete",
#             "context":    context,
#             "summary":    summary_msg,
#             "response":   "Leads were found but none scored above the quality threshold. Try adjusting your targeting.",
#             "leads":      [],
#             "validation": {"valid": False, "notes": "No leads cleared the quality threshold."},
#             "suggestions": {},
#         }

#     # ── Step 3: AI Validator + enrichment ────────────────────
#     try:
#         enriched = validate_and_enrich(context, scored_leads)
#     except Exception as e:
#         print(f"[AIValidator Error] {e}")
#         enriched = {
#             "summary":    summary_msg,
#             "validation": {"valid": True, "notes": ""},
#             "leads":      scored_leads,
#         }

#     total_fields = len(FIELD_ORDER)
#     return {
#         "status":     "complete",
#         "phase":      "complete",
#         "context":    context,
#         "summary":    enriched.get("summary", summary_msg),
#         "validation": enriched.get("validation", {}),
#         "leads":      enriched.get("leads", []),
#         "suggestions": {},
#         "progress":   {"filled": total_fields, "total": total_fields, "percent": 100},
#     }


# # ══════════════════════════════════════════════════════════════
# # UTILITY ENDPOINTS
# # ══════════════════════════════════════════════════════════════

# @router.post("/reset")
# def reset(req: ResetRequest):
#     reset_context(req.session_id)
#     return {"status": "reset", "session_id": req.session_id}


# @router.get("/context/{session_id}")
# def get_session_context(session_id: str):
#     state = get_context(session_id)
#     return {
#         "session_id":    session_id,
#         "phase":         get_phase(session_id),
#         "context":       state["context"],
#         "message_count": state.get("message_count", 0),
#         "complete":      is_complete(session_id),
#     }


# # ══════════════════════════════════════════════════════════════
# # HELPERS
# # ══════════════════════════════════════════════════════════════

# def _progress(context: dict) -> dict:
#     filled = sum(1 for f in FIELD_ORDER if context.get(f))
#     total  = len(FIELD_ORDER)
#     return {
#         "filled":  filled,
#         "total":   total,
#         "percent": round(filled / total * 100),
#     }


# routes.py
# ─────────────────────────────────────────────────────────────
# Two-phase conversation pipeline:
#
#   Phase 1 — PRODUCT UNDERSTANDING
#     Collects product description, name, USPs, pricing tier,
#     campaign budget, ideal buyer, market type, buyer stage.
#
#   Phase 2 — AUDIENCE TARGETING
#     Collects geography, industry, job function, job level,
#     employee size, revenue range.
#
#   Complete → Cortex → Insight Engine → AI Validator → results
# ─────────────────────────────────────────────────────────────

from fastapi import APIRouter
from pydantic import BaseModel

from .context_memory import (
    get_context,
    update_context,
    reset_context,
    is_complete,
    force_update_field,
    set_pending_edit,
    get_pending_edit,
    clear_pending_edit,
)

from .context_builder import build_context

from .ai_taxonomy_service import (
    get_next_field,
    get_conversation_phase,
    generate_conversational_question,
    generate_completion_message,
    PRODUCT_FIELDS,
    TARGETING_FIELDS,
    QUESTION_MAP,
    FIELD_LABELS,
)

from .intent_analyzer import (
    is_off_topic,
    generate_off_topic_reply,
    detect_edit_intent,
    extract_new_value_for_field,
)

from .openai_service import ask_gpt

from .prompt_builder import build_cortex_prompt
from .cortex_service import query_cortex_analyst

# Uncomment later when re-enabled
# from .insight_engine import run_insight_engine
# from .ai_validator import validate_and_enrich

from .suggestion_engine import get_suggestions

router = APIRouter(
    prefix="/context",
    tags=["Context Engine"]
)


# ══════════════════════════════════════════════════════════════
# ACTIVE FIELD ORDER
# industry_domain intentionally removed
# ══════════════════════════════════════════════════════════════

ACTIVE_FIELD_ORDER = [
    *PRODUCT_FIELDS,

    "geography",
    "industry",
    "job_function",
    "job_level",
    "employee_size",
    "revenue_range",
]


# ══════════════════════════════════════════════════════════════
# REQUEST MODELS
# ══════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ResetRequest(BaseModel):
    session_id: str


# ══════════════════════════════════════════════════════════════
# CHAT ENDPOINT
# ══════════════════════════════════════════════════════════════

@router.post("/chat")
def chat(req: ChatRequest):

    session_id = req.session_id
    user_input = req.message.strip()

    # ──────────────────────────────────────────────────────────
    # LOAD SESSION
    # ──────────────────────────────────────────────────────────

    state   = get_context(session_id)
    context = state["context"]
    phase   = get_conversation_phase(context)

    # ══════════════════════════════════════════════════════════
    # EDIT FLOW — intercept FIRST, before any other processing
    # ══════════════════════════════════════════════════════════

    # Case A: We previously asked "what's the new value?" and are
    #         now receiving the user's answer.
    pending_field = get_pending_edit(session_id)

    if pending_field:
        new_value = extract_new_value_for_field(user_input, pending_field)
        if new_value:
            force_update_field(session_id, pending_field, new_value)
            clear_pending_edit(session_id)
            # Reload context after write
            context = get_context(session_id)["context"]
            phase   = get_conversation_phase(context)
            next_field = get_next_field(context)

            field_label = FIELD_LABELS.get(pending_field, pending_field)
            confirm_msg = _generate_edit_confirmation(
                field_label, new_value, context, user_input
            )

            suggestions = (
                get_suggestions(context, next_field)
                if next_field and phase == "targeting" else {}
            )
            return {
                "status":      "in_progress" if next_field else "complete",
                "phase":       phase,
                "context":     context,
                "response":    confirm_msg,
                "suggestions": suggestions,
                "next_field":  next_field,
                "edit_applied": {"field": pending_field, "value": new_value},
                "progress":    _progress(context),
            }
        else:
            # They still didn't give a value — ask again
            field_label = FIELD_LABELS.get(pending_field, pending_field)
            return {
                "status":     "in_progress",
                "phase":      phase,
                "context":    context,
                "response":   f"What would you like to change {field_label} to?",
                "next_field": pending_field,
                "progress":   _progress(context),
            }

    # Case B: User is sending an edit request in a normal turn.
    #         Detect it before build_context runs so we don't accidentally
    #         overwrite the old value with a partial extraction.
    edit_field = detect_edit_intent(user_input)

    if edit_field:
        # Try to extract a new value from the same message
        # (e.g. "change budget to $50K" — value is right there)
        new_value = extract_new_value_for_field(user_input, edit_field)

        if new_value:
            force_update_field(session_id, edit_field, new_value)
            context    = get_context(session_id)["context"]
            phase      = get_conversation_phase(context)
            next_field = get_next_field(context)
            field_label = FIELD_LABELS.get(edit_field, edit_field)
            confirm_msg = _generate_edit_confirmation(
                field_label, new_value, context, user_input
            )
            suggestions = (
                get_suggestions(context, next_field)
                if next_field and phase == "targeting" else {}
            )
            return {
                "status":      "in_progress" if next_field else "complete",
                "phase":       phase,
                "context":     context,
                "response":    confirm_msg,
                "suggestions": suggestions,
                "next_field":  next_field,
                "edit_applied": {"field": edit_field, "value": new_value},
                "progress":    _progress(context),
            }
        else:
            # They said "change X" but didn't give the new value — ask for it
            set_pending_edit(session_id, edit_field)
            field_label = FIELD_LABELS.get(edit_field, edit_field)
            return {
                "status":     "in_progress",
                "phase":      phase,
                "context":    context,
                "response":   f"Sure — what would you like to change {field_label} to?",
                "next_field": edit_field,
                "progress":   _progress(context),
            }

    # ──────────────────────────────────────────────────────────
    # NORMAL FLOW — update context, then check off-topic
    # build_context runs first so targeting info volunteered in
    # the very first message is never lost to an early return.
    # ──────────────────────────────────────────────────────────

    context = build_context(user_input, context, current_phase=phase)
    update_context(session_id, context)

    # Refresh phase after extraction
    phase = get_conversation_phase(context)

    # ──────────────────────────────────────────────────────────
    # OFF-TOPIC CHECK (targeting phase only)
    # ──────────────────────────────────────────────────────────

    if phase == "targeting" and is_off_topic(user_input):

        next_field = get_next_field(context)

        from .ai_taxonomy_service import QUESTION_MAP

        fallback_question = QUESTION_MAP.get(next_field, "")

        reply = generate_off_topic_reply(
            user_input,
            context,
            fallback_question,
        )

        suggestions = (
            get_suggestions(context, next_field)
            if next_field else {}
        )

        return {
            "status": "in_progress",
            "phase": phase,
            "context": context,
            "response": reply,
            "suggestions": suggestions,
            "next_field": next_field,
            "off_topic": True,
            "progress": _progress(context),
        }

    print(
        f"[Session={session_id}] "
        f"Phase={phase} "
        f"Context={context}"
    )

    # ──────────────────────────────────────────────────────────
    # DETERMINE NEXT FIELD
    # ──────────────────────────────────────────────────────────

    next_field = get_next_field(context)

    # ──────────────────────────────────────────────────────────
    # STILL COLLECTING CONTEXT
    # ──────────────────────────────────────────────────────────

    if next_field:

        response = generate_conversational_question(
            context,
            user_input,
            next_field,
        )

        # Suggestions only for targeting phase
        suggestions = (
            get_suggestions(context, next_field)
            if phase == "targeting"
            else {}
        )

        return {
            "status": "in_progress",
            "phase": phase,
            "context": context,
            "response": response,
            "suggestions": suggestions,
            "next_field": next_field,
            "progress": _progress(context),
        }

    # ══════════════════════════════════════════════════════════
    # COMPLETE FLOW
    # ══════════════════════════════════════════════════════════

    summary_msg = generate_completion_message(context)

    # ──────────────────────────────────────────────────────────
    # STEP 1 — BUILD CORTEX PROMPT
    # ──────────────────────────────────────────────────────────

    cortex_prompt = build_cortex_prompt(
        context,
        user_input,
    )

    # ──────────────────────────────────────────────────────────
    # STEP 2 — QUERY CORTEX
    # ──────────────────────────────────────────────────────────

    try:

        cortex_leads = query_cortex_analyst(cortex_prompt)

        print(
            f"[Cortex] Returned "
            f"{len(cortex_leads)} leads"
        )

    except Exception as e:

        print(f"[Cortex Error] {e}")

        cortex_leads = []

    # ──────────────────────────────────────────────────────────
    # NO LEADS FOUND
    # ──────────────────────────────────────────────────────────

    if not cortex_leads:

        return {
            "status": "complete",
            "phase": "complete",
            "context": context,
            "summary": summary_msg,
            "response": (
                "Snowflake Cortex returned no leads "
                "for this criteria. "
                "Try broadening your filters."
            ),
            "leads": [],
            "validation": {
                "valid": False,
                "notes": "No leads returned from Cortex.",
            },
            "suggestions": {},
            "progress": {
                "filled": len(ACTIVE_FIELD_ORDER),
                "total": len(ACTIVE_FIELD_ORDER),
                "percent": 100,
            },
        }

    # ══════════════════════════════════════════════════════════
    # FUTURE PIPELINE
    # ══════════════════════════════════════════════════════════

    # ── Insight Engine ────────────────────────────────────────
    #
    # try:
    #     scored_leads = run_insight_engine(cortex_leads)
    #
    # except Exception as e:
    #     print(f"[InsightEngine Error] {e}")
    #     scored_leads = cortex_leads
    #
    # ── AI Validator ──────────────────────────────────────────
    #
    # try:
    #     enriched = validate_and_enrich(
    #         context,
    #         scored_leads,
    #     )
    #
    # except Exception as e:
    #     print(f"[AIValidator Error] {e}")
    #
    #     enriched = {
    #         "summary": summary_msg,
    #         "validation": {
    #             "valid": True,
    #             "notes": "",
    #         },
    #         "leads": scored_leads,
    #     }

    # ══════════════════════════════════════════════════════════
    # FINAL RESPONSE
    # ══════════════════════════════════════════════════════════

    total_fields = len(ACTIVE_FIELD_ORDER)

    return {
        "status": "complete",
        "phase": "complete",
        "context": context,
        "summary": summary_msg,
        "validation": {
            "valid": True,
            "notes": "Cortex results returned successfully.",
        },
        "leads": cortex_leads,
        "suggestions": {},
        "progress": {
            "filled": total_fields,
            "total": total_fields,
            "percent": 100,
        },
    }


# ══════════════════════════════════════════════════════════════
# RESET SESSION
# ══════════════════════════════════════════════════════════════

@router.post("/reset")
def reset(req: ResetRequest):

    reset_context(req.session_id)

    return {
        "status": "reset",
        "session_id": req.session_id,
    }


# ══════════════════════════════════════════════════════════════
# GET SESSION CONTEXT
# ══════════════════════════════════════════════════════════════

@router.get("/context/{session_id}")
def get_session_context(session_id: str):

    state = get_context(session_id)

    context = state["context"]

    return {
        "session_id": session_id,
        "phase": get_conversation_phase(context),
        "context": context,
        "message_count": state.get("message_count", 0),
        "complete": is_complete(session_id),
    }


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def _progress(context: dict) -> dict:

    filled = sum(
        1 for field in ACTIVE_FIELD_ORDER
        if context.get(field)
    )

    total = len(ACTIVE_FIELD_ORDER)

    return {
        "filled": filled,
        "total": total,
        "percent": round((filled / total) * 100),
    }


def _generate_edit_confirmation(
    field_label: str,
    new_value: str,
    context: dict,
    user_input: str,
) -> str:
    """
    Generate a brief, natural confirmation that the field was updated,
    then flow into the next question if one exists.
    """
    next_field = get_next_field(context)
    next_q = QUESTION_MAP.get(next_field, "") if next_field else ""

    prompt = f"""You are Delphi, a sharp B2B campaign assistant.

The user just updated a field in their campaign profile.
Updated: {field_label} → "{new_value}"

{"Next question to ask: " + next_q if next_q else "All fields are now complete."}

Write ONE short response (1-2 sentences) that:
1. Briefly confirms the update (don't just say "Updated!" — be natural)
2. Either asks the next question naturally, or confirms everything is set

Rules: no filler, no bullet points, sound like a consultant."""

    try:
        return ask_gpt(prompt, temperature=0.5, max_tokens=100)
    except Exception:
        base = f"{field_label} updated to \"{new_value}\"."
        return f"{base} {next_q}" if next_q else base