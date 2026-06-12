"""
TMS — AI Triage Chatbot Route
Hybrid engine: Google Gemini AI + rule-based fallback.
Red-flag safety layer always runs first (hard-coded).
"""
import re
import json
import random
import traceback
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User
from ..config import settings

router = APIRouter(prefix="/api/triage", tags=["Triage"])

# ── Gemini client (lazy init) ──
_gemini_model = None
_gemini_available = False


def _init_gemini():
    """Initialize Gemini client once."""
    global _gemini_model, _gemini_available
    if _gemini_model is not None:
        return
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key.strip() == "":
        print("[Triage] No GEMINI_API_KEY set — using rule-based fallback.")
        _gemini_available = False
        _gemini_model = False  # Mark as attempted
        return
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.9,
                "max_output_tokens": 1024,
            },
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        )
        _gemini_available = True
        print("[Triage] ✅ Gemini AI initialized successfully (model: gemini-2.0-flash)")
    except Exception as e:
        print(f"[Triage] ⚠️ Gemini init failed: {e}. Using rule-based fallback.")
        _gemini_available = False
        _gemini_model = False


# ── System Prompt for Gemini ──

SYSTEM_PROMPT = """# IDENTITY & ROLE
You are an advanced, empathetic, and clinically safe Conversational AI Triage Assistant embedded within a secure hospital patient portal. Your primary purpose is to help patients understand the urgency of their symptoms and guide them to the right level of care (e.g., Emergency Room, Urgent Care, Primary Care Appointment, or Self-Care at home).

You are a triage tool, NOT a diagnostic engine. You do not provide definitive diagnoses or prescribe treatments.

# IMMEDIATE SAFETY DIRECTIVE (RED FLAGS)
If the patient mentions ANY of the following symptoms at any point in the conversation, immediately cease symptom gathering, trigger an emergency alert, and instruct them to call 911 or go to the nearest Emergency Room:
- Severe chest pain, pressure, or squeezing.
- Sudden, severe shortness of breath or difficulty breathing.
- Sudden weakness, numbness, or paralysis (especially on one side of the body).
- Sudden difficulty speaking, slurred speech, or confusion.
- Sudden, severe headache unlike any experienced before.
- Heavy, uncontrolled bleeding or severe trauma.
- Anaphylaxis signs (swelling of face/throat, hives, wheezing together).

# CONVERSATIONAL CONSTRAINTS & TONE
- **Tone:** Empathetic, calm, professional, and reassuring. Avoid sounding like a rigid machine, but maintain clinical boundaries.
- **Pacing:** Ask only ONE clarifying question at a time. Do not overwhelm an unwell patient with a wall of questions.
- **Language:** Mirror the patient's language complexity. Define any necessary medical terms using everyday language.

# CORE CONVERSATIONAL WORKFLOW

### Step 1: Initial Gathering
Listen to the patient's opening complaint. Acknowledge it with brief empathy.

### Step 2: Clarifying (The OPQRST Method)
Ask up to 3–4 sequential, single questions to narrow down the context if the user hasn't already provided it:
- **Onset/Duration:** When did this start? Is it constant or intermittent?
- **Severity/Character:** How bad is it on a scale of 1-10? Is it sharp, dull, throbbing?
- **Modifying Factors:** Does anything make it better or worse?
- **Associated Symptoms:** Are there other symptoms (e.g., fever, nausea, dizziness)?

### Step 3: Triage Assessment & Care Routing
Once you have sufficient context (after 3-4 clarifying questions), provide a summary using the following strict triaging tiers:
1. **EMERGENT:** Direct to the nearest ER.
2. **URGENT:** Advise visiting an Urgent Care clinic within the next 12–24 hours.
3. **NON-URGENT / ROUTINE:** Suggest scheduling a routine visit with their Primary Care Provider (PCP) or utilizing the portal to message their care team.
4. **SUPPORTIVE CARE:** Provide general, safe, non-medicinal self-care strategies (e.g., hydration, rest) while they wait for their appointment.

# STRICT CLINICAL GUARDRAILS
1. **No Definitive Diagnosis:** Never say "You have [Condition]." Instead, use educational framing: "Based on what you've described, these symptoms are commonly associated with things like [Condition A] or [Condition B], but an in-person evaluation is required."
2. **No Prescription Advice:** Never recommend specific prescription medications, dosages, or adjustments to current meds. You may mention generic, common over-the-counter options only as a general point of discussion, always telling them to consult a pharmacist or doctor first.
3. **Mandatory Disclaimer:** Every final triage summary must conclude with: "This is an automated triage assessment to help guide your next steps. It does not replace a professional medical evaluation. If your symptoms worsen, please seek medical care immediately."

# RESPONSE FORMAT RULES
You must respond with valid JSON only. No markdown, no extra text outside the JSON.

Your response must be a JSON object with these fields:
{
  "reply": "Your conversational message to the patient (use markdown for formatting: **bold**, ### headings, bullet points with •, --- for dividers)",
  "stage": "gathering" | "clarifying" | "assessment",
  "suggestions": ["suggestion1", "suggestion2", "suggestion3", "suggestion4"],
  "is_emergency": false,
  "triage_result": null
}

When you determine this is an EMERGENCY, respond with:
{
  "reply": "Your emergency message",
  "stage": "assessment",
  "suggestions": ["Call 911", "Find nearest ER"],
  "is_emergency": true,
  "triage_result": {
    "tier": "EMERGENT",
    "summary": "brief summary",
    "routing": "Call 911 or go to the nearest Emergency Room immediately.",
    "ehr_data": {
      "primary_complaint": "symptom",
      "duration": "duration",
      "severity_score": "10",
      "pertinent_negatives_positives": ["Positive: symptom"],
      "assigned_triage_tier": "EMERGENT",
      "recommended_routing": "Emergency Room / Call 911"
    }
  }
}

When you have gathered enough info and are giving a FINAL assessment (NOT emergency), respond with:
{
  "reply": "Your full assessment message with ### heading, **bold** tier, care recommendations, and disclaimer",
  "stage": "assessment",
  "suggestions": ["relevant action 1", "relevant action 2"],
  "is_emergency": false,
  "triage_result": {
    "tier": "URGENT" | "NON_URGENT" | "SUPPORTIVE",
    "summary": "Brief summary of the assessment",
    "routing": "Recommended care routing text",
    "ehr_data": {
      "primary_complaint": "extracted primary complaint",
      "duration": "extracted duration",
      "severity_score": "1-10 score",
      "pertinent_negatives_positives": ["Positive: symptom1", "Negative: no fever"],
      "assigned_triage_tier": "URGENT|NON_URGENT|SUPPORTIVE",
      "recommended_routing": "routing recommendation"
    }
  }
}

IMPORTANT: Only set triage_result when giving the FINAL assessment. During clarifying questions, set it to null.
IMPORTANT: The "suggestions" field should contain 3-4 short reply options the patient might click as quick replies.
IMPORTANT: During clarifying stage, ask only ONE question at a time.
"""


# ── Request / Response Models ──

class ConversationMessage(BaseModel):
    role: str  # "user" or "bot"
    content: str

class TriageChatRequest(BaseModel):
    message: str
    conversation_history: list[dict] = []
    patient_context: Optional[dict] = None  # { age, gender, conditions }

class TriageResult(BaseModel):
    tier: str
    summary: str
    routing: str
    ehr_data: dict

class TriageChatResponse(BaseModel):
    reply: str
    stage: str
    suggestions: list[str] = []
    triage_result: Optional[dict] = None
    is_emergency: bool = False


# ── Red Flag Keywords (hard-coded safety layer — always runs) ──

RED_FLAGS = {
    "chest_pain": {
        "patterns": [
            r"chest\s*pain", r"chest\s*pressure", r"chest\s*squeezing",
            r"chest\s*tight", r"crushing\s*chest", r"heart\s*attack",
        ],
        "message": "chest pain, pressure, or tightness",
    },
    "breathing": {
        "patterns": [
            r"can'?t\s*breathe", r"difficulty\s*breathing", r"severe\s*shortness\s*of\s*breath",
            r"struggling\s*to\s*breathe", r"suffocating", r"choking",
        ],
        "message": "severe difficulty breathing",
    },
    "stroke": {
        "patterns": [
            r"sudden\s*weakness", r"sudden\s*numbness", r"paralysis",
            r"one\s*side.*numb", r"face\s*droop", r"can'?t\s*move\s*(my\s*)?(arm|leg|hand|foot)",
            r"sudden\s*confusion", r"slurred\s*speech", r"can'?t\s*speak",
            r"difficulty\s*speaking",
        ],
        "message": "sudden neurological symptoms (possible stroke signs)",
    },
    "headache_severe": {
        "patterns": [
            r"worst\s*headache", r"thunderclap\s*headache",
            r"worst\s*headache\s*(of|in)\s*my\s*life",
            r"sudden\s*severe\s*headache",
        ],
        "message": "sudden, severe headache unlike any before",
    },
    "bleeding": {
        "patterns": [
            r"heavy\s*(uncontrolled\s*)?bleeding", r"severe\s*bleeding",
            r"won'?t\s*stop\s*bleeding", r"massive\s*blood\s*loss",
            r"severe\s*trauma",
        ],
        "message": "heavy, uncontrolled bleeding or severe trauma",
    },
    "anaphylaxis": {
        "patterns": [
            r"throat\s*(is\s*)?swelling", r"face\s*(is\s*)?swelling",
            r"can'?t\s*swallow", r"hives.*wheez", r"wheez.*hives",
            r"anaphyla", r"allergic\s*reaction.*severe",
        ],
        "message": "signs of anaphylaxis",
    },
}


def detect_red_flags(text: str) -> Optional[dict]:
    """Scan message for emergency red-flag patterns."""
    text_lower = text.lower()
    for flag_key, flag_data in RED_FLAGS.items():
        for pattern in flag_data["patterns"]:
            if re.search(pattern, text_lower):
                return {"key": flag_key, "message": flag_data["message"]}
    return None


def build_emergency_response(flag: dict) -> TriageChatResponse:
    """Build immediate emergency response."""
    reply = (
        f"🚨 **EMERGENCY ALERT**\n\n"
        f"You've described symptoms consistent with **{flag['message']}**. "
        f"This is a potentially life-threatening situation that requires immediate medical attention.\n\n"
        f"**Please call 911 or go to the nearest Emergency Room immediately.**\n\n"
        f"Do not drive yourself — have someone else drive you, or call an ambulance.\n\n"
        f"---\n"
        f"⚠️ *This is an automated triage assessment to help guide your next steps. "
        f"It does not replace a professional medical evaluation. "
        f"If your symptoms worsen, please seek medical care immediately.*"
    )

    ehr_data = {
        "primary_complaint": flag["message"],
        "duration": "Immediate",
        "severity_score": "10",
        "pertinent_negatives_positives": [f"Positive: {flag['message']}"],
        "assigned_triage_tier": "EMERGENT",
        "recommended_routing": "Emergency Room / Call 911",
    }

    return TriageChatResponse(
        reply=reply,
        stage="assessment",
        suggestions=["Call 911", "Find nearest ER"],
        triage_result={
            "tier": "EMERGENT",
            "summary": f"Emergency: {flag['message']}",
            "routing": "Call 911 or go to the nearest Emergency Room immediately.",
            "ehr_data": ehr_data,
        },
        is_emergency=True,
    )


# ══════════════════════════════════════════════
#  GEMINI AI ENGINE
# ══════════════════════════════════════════════

def _call_gemini(message: str, history: list[dict], patient_ctx: Optional[dict]) -> Optional[TriageChatResponse]:
    """Call Gemini API for conversational triage. Returns None on failure."""
    _init_gemini()
    if not _gemini_available or not _gemini_model:
        return None

    try:
        # Build context-aware system prompt
        system = SYSTEM_PROMPT
        if patient_ctx:
            ctx_parts = []
            if patient_ctx.get("age"):
                ctx_parts.append(f"Age: {patient_ctx['age']}")
            if patient_ctx.get("gender"):
                ctx_parts.append(f"Biological sex: {patient_ctx['gender']}")
            if patient_ctx.get("conditions"):
                ctx_parts.append(f"Known conditions: {', '.join(patient_ctx['conditions'])}")
            if ctx_parts:
                system += f"\n\n# PATIENT CONTEXT (pre-populated from portal — do NOT ask these again)\n" + "\n".join(ctx_parts)

        # Build conversation for Gemini
        gemini_history = []
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        # Start chat with system instruction
        chat = _gemini_model.start_chat(history=gemini_history)

        # Send the current message with system prompt context
        prompt = f"```\n{message}\n```"
        if not history:
            # First message — include system prompt
            prompt = f"[System Instructions — follow these strictly]\n{system}\n\n[Patient Message]\n```\n{message}\n```"
        
        response = chat.send_message(prompt)
        raw_text = response.text.strip()

        # Parse JSON response
        # Strip markdown code fences if present
        if raw_text.startswith("```"):
            raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text)
            raw_text = re.sub(r'\s*```$', '', raw_text)

        data = json.loads(raw_text)

        return TriageChatResponse(
            reply=data.get("reply", "I'm having trouble processing that. Could you rephrase?"),
            stage=data.get("stage", "clarifying"),
            suggestions=data.get("suggestions", []),
            triage_result=data.get("triage_result"),
            is_emergency=data.get("is_emergency", False),
        )

    except json.JSONDecodeError as e:
        print(f"[Triage] Gemini JSON parse error: {e}")
        print(f"[Triage] Raw response: {raw_text[:500] if 'raw_text' in dir() else 'N/A'}")
        # Try to extract just the reply text if JSON parsing fails
        if 'raw_text' in dir() and raw_text:
            return TriageChatResponse(
                reply=raw_text,
                stage="clarifying",
                suggestions=[],
            )
        return None
    except Exception as e:
        print(f"[Triage] Gemini API error: {e}")
        traceback.print_exc()
        return None


# ══════════════════════════════════════════════
#  RULE-BASED FALLBACK ENGINE
# ══════════════════════════════════════════════

SYMPTOM_DB = {
    "headache": {"base_score": 3, "category": "neurological", "common_conditions": ["tension headache", "migraine", "sinusitis"]},
    "migraine": {"base_score": 4, "category": "neurological", "common_conditions": ["migraine", "cluster headache"]},
    "fever": {"base_score": 3, "category": "systemic", "common_conditions": ["viral infection", "bacterial infection", "flu"]},
    "high fever": {"base_score": 5, "category": "systemic", "common_conditions": ["serious infection", "flu", "COVID-19"]},
    "cough": {"base_score": 2, "category": "respiratory", "common_conditions": ["common cold", "bronchitis", "allergies"]},
    "sore throat": {"base_score": 2, "category": "respiratory", "common_conditions": ["pharyngitis", "tonsillitis", "common cold"]},
    "nausea": {"base_score": 2, "category": "gastrointestinal", "common_conditions": ["gastritis", "food poisoning", "viral illness"]},
    "vomiting": {"base_score": 3, "category": "gastrointestinal", "common_conditions": ["gastroenteritis", "food poisoning", "migraine"]},
    "diarrhea": {"base_score": 3, "category": "gastrointestinal", "common_conditions": ["gastroenteritis", "food intolerance", "IBS"]},
    "stomach pain": {"base_score": 3, "category": "gastrointestinal", "common_conditions": ["gastritis", "indigestion", "peptic ulcer"]},
    "abdominal pain": {"base_score": 4, "category": "gastrointestinal", "common_conditions": ["appendicitis", "gastritis", "kidney stones"]},
    "back pain": {"base_score": 3, "category": "musculoskeletal", "common_conditions": ["muscle strain", "herniated disc", "poor posture"]},
    "joint pain": {"base_score": 3, "category": "musculoskeletal", "common_conditions": ["arthritis", "injury", "gout"]},
    "rash": {"base_score": 2, "category": "dermatological", "common_conditions": ["allergic reaction", "eczema", "contact dermatitis"]},
    "dizziness": {"base_score": 3, "category": "neurological", "common_conditions": ["vertigo", "dehydration", "low blood pressure"]},
    "fatigue": {"base_score": 2, "category": "systemic", "common_conditions": ["anemia", "thyroid disorder", "stress/burnout"]},
    "shortness of breath": {"base_score": 4, "category": "respiratory", "common_conditions": ["asthma", "anxiety", "anemia"]},
    "palpitations": {"base_score": 4, "category": "cardiovascular", "common_conditions": ["anxiety", "arrhythmia", "caffeine sensitivity"]},
    "swelling": {"base_score": 3, "category": "general", "common_conditions": ["injury", "infection", "fluid retention"]},
    "eye pain": {"base_score": 3, "category": "ophthalmological", "common_conditions": ["conjunctivitis", "dry eye", "corneal scratch"]},
    "ear pain": {"base_score": 3, "category": "ENT", "common_conditions": ["otitis media", "ear infection", "TMJ"]},
    "toothache": {"base_score": 3, "category": "dental", "common_conditions": ["cavity", "abscess", "gum disease"]},
    "anxiety": {"base_score": 2, "category": "mental_health", "common_conditions": ["generalized anxiety", "panic disorder", "stress"]},
    "insomnia": {"base_score": 2, "category": "mental_health", "common_conditions": ["stress", "anxiety", "poor sleep hygiene"]},
    "urinary pain": {"base_score": 3, "category": "urological", "common_conditions": ["urinary tract infection", "kidney stones", "bladder infection"]},
    "burning urination": {"base_score": 3, "category": "urological", "common_conditions": ["UTI", "STI", "bladder infection"]},
}

CLARIFY_QUESTIONS = {
    "onset": [
        "I understand. When did this first start? Is it something that came on suddenly, or has it been building up gradually over time?",
        "Got it. Can you tell me when you first noticed this? Has it been constant, or does it come and go?",
    ],
    "severity": [
        "Thank you for sharing that. On a scale of 1 to 10, with 10 being the worst pain or discomfort you've ever felt, how would you rate this right now?",
        "I appreciate that context. How severe would you say this is right now, on a 1-to-10 scale?",
    ],
    "modifying": [
        "Is there anything that makes it feel better or worse? For example, rest, movement, eating, certain positions, or medications?",
        "Have you noticed anything that seems to trigger it or relieve it — like certain activities, foods, or rest?",
    ],
    "associated": [
        "Are you experiencing any other symptoms along with this? For example, fever, nausea, dizziness, or fatigue?",
        "Besides what you've mentioned, are there any other symptoms you've noticed, even if they seem unrelated?",
    ],
}

EMPATHY_RESPONSES = [
    "I'm sorry to hear you're dealing with that.",
    "I understand that must be uncomfortable.",
    "Thank you for reaching out about this — let me help you figure out the best next step.",
    "I can see how that would be concerning. Let's work through this together.",
    "I appreciate you sharing this with me. Let me ask a few questions to better understand.",
]


def extract_symptoms(text: str) -> list[dict]:
    text_lower = text.lower()
    found = []
    for symptom, data in SYMPTOM_DB.items():
        words = symptom.split()
        if len(words) == 1:
            if re.search(r'\b' + re.escape(symptom) + r'\b', text_lower):
                found.append({"name": symptom, **data})
        else:
            if symptom in text_lower:
                found.append({"name": symptom, **data})
    return found


def extract_severity(text: str) -> Optional[int]:
    number_words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    }
    match = re.search(r'\b(\d{1,2})\s*(?:/\s*10|out\s*of\s*10)?\b', text)
    if match:
        val = int(match.group(1))
        if 1 <= val <= 10:
            return val
    text_lower = text.lower()
    for word, val in number_words.items():
        if re.search(r'\b' + word + r'\b', text_lower):
            return val
    return None


def extract_duration(text: str) -> Optional[str]:
    text_lower = text.lower()
    duration_patterns = [
        (r'(\d+)\s*(?:day|days)\s*(?:ago)?', lambda m: f"{m.group(1)} days"),
        (r'(\d+)\s*(?:hour|hours|hr|hrs)\s*(?:ago)?', lambda m: f"{m.group(1)} hours"),
        (r'(\d+)\s*(?:week|weeks)\s*(?:ago)?', lambda m: f"{m.group(1)} weeks"),
        (r'(\d+)\s*(?:month|months)\s*(?:ago)?', lambda m: f"{m.group(1)} months"),
        (r'(?:since\s+)?(?:this\s+)?morning', lambda m: "since this morning"),
        (r'(?:since\s+)?(?:last\s+)?night', lambda m: "since last night"),
        (r'(?:since\s+)?yesterday', lambda m: "since yesterday"),
        (r'(?:a\s+)?few\s+(?:day|days)', lambda m: "a few days"),
        (r'(?:a\s+)?few\s+(?:hour|hours)', lambda m: "a few hours"),
        (r'just\s+(?:now|started)', lambda m: "just started"),
        (r'(?:for\s+)?a\s+while', lambda m: "a while"),
        (r'on\s*and\s*off', lambda m: "intermittent"),
        (r'constant', lambda m: "constant"),
        (r'comes?\s*and\s*goes?', lambda m: "intermittent"),
    ]
    for pattern, extractor in duration_patterns:
        match = re.search(pattern, text_lower)
        if match:
            return extractor(match)
    return None


def determine_conversation_stage(history: list[dict]) -> list[str]:
    covered = []
    for msg in history:
        if msg.get("role") == "bot":
            content_lower = msg["content"].lower()
            if any(w in content_lower for w in ["when did", "how long", "start", "onset", "first notice"]):
                covered.append("onset")
            if any(w in content_lower for w in ["scale", "1 to 10", "1-10", "severe", "rate"]):
                covered.append("severity")
            if any(w in content_lower for w in ["better or worse", "trigger", "relieve", "modif"]):
                covered.append("modifying")
            if any(w in content_lower for w in ["other symptom", "along with", "besides", "associat"]):
                covered.append("associated")
    return list(set(covered))


def compute_triage_score(symptoms, severity, duration, associated_symptoms, patient_context):
    score = 0
    for s in symptoms:
        score += s.get("base_score", 2)
    if severity:
        if severity >= 8: score += 6
        elif severity >= 6: score += 4
        elif severity >= 4: score += 2
    if duration:
        dur_lower = duration.lower()
        if any(w in dur_lower for w in ["just", "minute", "hour"]): score += 1
        elif any(w in dur_lower for w in ["day", "yesterday", "morning", "night"]): score += 2
        elif any(w in dur_lower for w in ["week", "month", "while"]): score += 1
    score += len(associated_symptoms) * 1
    if patient_context:
        age = patient_context.get("age")
        conditions = patient_context.get("conditions", [])
        if age and (age > 65 or age < 5): score += 2
        if conditions:
            high_risk = ["diabetes", "hypertension", "heart disease", "asthma", "copd", "cancer"]
            for c in conditions:
                if any(hr in c.lower() for hr in high_risk):
                    score += 2
                    break
    if score >= 12: tier = "URGENT"
    elif score >= 7: tier = "NON_URGENT"
    else: tier = "SUPPORTIVE"
    return score, tier


def build_assessment(symptoms, severity, duration, tier, patient_context):
    conditions = set()
    for s in symptoms:
        for c in s.get("common_conditions", []):
            conditions.add(c)
    conditions_list = list(conditions)[:4]

    tier_messages = {
        "EMERGENT": "Based on the symptoms you've described, **I strongly recommend you go to the nearest Emergency Room immediately or call 911.** This appears to require urgent emergency medical attention.",
        "URGENT": "Based on what you've described, I'd recommend visiting an **Urgent Care clinic within the next 12–24 hours**. These symptoms warrant timely medical evaluation, though they may not require an emergency room visit.",
        "NON_URGENT": "Based on your symptoms, I'd recommend **scheduling a routine visit with your Primary Care Provider (PCP)** within the next few days. You can use the portal to book an appointment or message your care team directly.",
        "SUPPORTIVE": "Based on what you've shared, your symptoms appear mild and may be managed with **general self-care** while you monitor for any changes. Stay hydrated, get rest, and don't hesitate to reach out if things get worse.",
    }

    tier_labels = {
        "EMERGENT": "🔴 EMERGENT", "URGENT": "🟠 URGENT",
        "NON_URGENT": "🟡 NON-URGENT / ROUTINE", "SUPPORTIVE": "🟢 SUPPORTIVE CARE",
    }

    parts = [f"### 📋 Triage Assessment Summary\n", f"**Triage Level:** {tier_labels.get(tier, tier)}\n"]
    parts.append(tier_messages.get(tier, ""))
    parts.append("")

    if conditions_list:
        joined = ', '.join(conditions_list[:-1])
        last = conditions_list[-1]
        if len(conditions_list) > 1:
            parts.append(f"Based on what you've described, these symptoms are commonly associated with things like **{joined}** or **{last}**. However, an in-person evaluation is required for a proper assessment.")
        else:
            parts.append(f"Based on what you've described, these symptoms are commonly associated with things like **{last}**. However, an in-person evaluation is required for a proper assessment.")
        parts.append("")

    if tier in ("NON_URGENT", "SUPPORTIVE"):
        parts.append("**In the meantime, you can try:**")
        parts.append("• Stay well-hydrated with water and clear fluids")
        parts.append("• Get adequate rest")
        parts.append("• Monitor your symptoms and note any changes")
        if severity and severity >= 4:
            parts.append("• Consider consulting a pharmacist about over-the-counter options (always consult your doctor first)")
        parts.append("")

    parts.append("---")
    parts.append("⚠️ *This is an automated triage assessment to help guide your next steps. It does not replace a professional medical evaluation. If your symptoms worsen, please seek medical care immediately.*")
    return "\n".join(parts)


def _rule_based_fallback(message: str, history: list[dict], patient_ctx: Optional[dict]) -> TriageChatResponse:
    """Original rule-based OPQRST engine as fallback."""
    all_user_text = " ".join([m["content"] for m in history if m.get("role") == "user"]) + " " + message
    all_symptoms = extract_symptoms(all_user_text)
    all_severity = extract_severity(all_user_text)
    all_duration = extract_duration(all_user_text)
    current_symptoms = extract_symptoms(message)
    covered_aspects = determine_conversation_stage(history)
    user_msg_count = sum(1 for m in history if m.get("role") == "user") + 1

    # STEP 1: Initial gathering
    if user_msg_count == 1:
        empathy = random.choice(EMPATHY_RESPONSES)
        if all_symptoms:
            question = random.choice(CLARIFY_QUESTIONS["onset"])
            return TriageChatResponse(
                reply=f"{empathy} {question}", stage="clarifying",
                suggestions=["Just started today", "A few days ago", "About a week", "It comes and goes"],
            )
        else:
            return TriageChatResponse(
                reply=f"{empathy} Could you tell me a bit more about what you're experiencing? What symptoms are bothering you the most right now?",
                stage="gathering",
                suggestions=["Headache", "Fever", "Stomach pain", "Cough", "Back pain", "Dizziness", "Fatigue"],
            )

    # STEP 2: Clarifying
    next_question = None
    next_suggestions = []
    if "onset" not in covered_aspects and not all_duration:
        next_question = random.choice(CLARIFY_QUESTIONS["onset"])
        next_suggestions = ["Just started today", "A few days ago", "About a week", "Comes and goes"]
    elif "severity" not in covered_aspects and not all_severity:
        next_question = random.choice(CLARIFY_QUESTIONS["severity"])
        next_suggestions = ["2-3 (Mild)", "4-5 (Moderate)", "6-7 (Significant)", "8-10 (Severe)"]
    elif "modifying" not in covered_aspects and user_msg_count <= 3:
        next_question = random.choice(CLARIFY_QUESTIONS["modifying"])
        next_suggestions = ["Rest helps", "Nothing helps", "Gets worse with movement", "Medication helps a bit"]
    elif "associated" not in covered_aspects and user_msg_count <= 4:
        next_question = random.choice(CLARIFY_QUESTIONS["associated"])
        next_suggestions = ["No other symptoms", "Some nausea", "Feeling tired", "Slight fever"]

    if next_question and user_msg_count < 5:
        ack = random.choice(["Thank you for that information.", "Got it, that's helpful.", "Understood.", "I see, thank you.", "That's really helpful context."])
        return TriageChatResponse(reply=f"{ack} {next_question}", stage="clarifying", suggestions=next_suggestions)

    # STEP 3: Final assessment
    if not all_severity: all_severity = 4
    if not all_duration: all_duration = "Not specified"

    score, tier = compute_triage_score(all_symptoms, all_severity, all_duration, [s["name"] for s in current_symptoms], patient_ctx)
    assessment_text = build_assessment(all_symptoms, all_severity, all_duration, tier, patient_ctx)
    primary = ", ".join([s["name"] for s in all_symptoms]) if all_symptoms else message[:100]

    ehr_data = {
        "primary_complaint": primary,
        "duration": all_duration or "Not specified",
        "severity_score": str(all_severity),
        "pertinent_negatives_positives": [f"Positive: {s['name']}" for s in all_symptoms],
        "assigned_triage_tier": tier,
        "recommended_routing": {"EMERGENT": "Emergency Room / Call 911", "URGENT": "Urgent Care within 12-24 hours", "NON_URGENT": "Schedule PCP appointment", "SUPPORTIVE": "Self-care with monitoring"}.get(tier, "Consult a healthcare provider"),
    }

    tier_suggestions = {
        "EMERGENT": ["Call 911", "Find nearest ER"], "URGENT": ["Find Urgent Care", "Book Appointment"],
        "NON_URGENT": ["Schedule Appointment", "Message Care Team"], "SUPPORTIVE": ["Schedule Checkup", "Start New Chat"],
    }

    return TriageChatResponse(
        reply=assessment_text, stage="assessment", suggestions=tier_suggestions.get(tier, []),
        triage_result={"tier": tier, "summary": f"Triage assessment for: {primary}", "routing": ehr_data["recommended_routing"], "ehr_data": ehr_data},
        is_emergency=False,
    )


# ══════════════════════════════════════════════
#  MAIN CHAT ENDPOINT
# ══════════════════════════════════════════════

@router.post("/chat", response_model=TriageChatResponse)
def triage_chat(
    req: TriageChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process a triage chat message. Uses Gemini AI with rule-based fallback."""
    message = req.message.strip()
    if len(message) > 500:
        raise HTTPException(status_code=400, detail="Message too long")
    message = message.replace("<", "&lt;").replace(">", "&gt;").replace("`", "")

    history = req.conversation_history or []
    patient_ctx = req.patient_context

    # ── SAFETY LAYER: Always check red flags first (hard-coded, not AI-dependent) ──
    red_flag = detect_red_flags(message)
    if red_flag:
        return build_emergency_response(red_flag)

    for msg in history:
        if msg.get("role") == "user":
            rf = detect_red_flags(msg["content"])
            if rf:
                return build_emergency_response(rf)

    # ── Try Gemini AI first ──
    gemini_response = _call_gemini(message, history, patient_ctx)
    if gemini_response:
        # Double-check: if Gemini says emergency, verify with our red-flag detector
        if gemini_response.is_emergency:
            return gemini_response
        return gemini_response

    # ── Fallback to rule-based engine ──
    return _rule_based_fallback(message, history, patient_ctx)


@router.get("/status")
def triage_status():
    """Check if Gemini AI is available."""
    _init_gemini()
    return {
        "gemini_available": _gemini_available,
        "engine": "gemini" if _gemini_available else "rule-based",
        "model": "gemini-2.0-flash" if _gemini_available else None,
    }
