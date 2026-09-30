import json
import time
from google import genai
from google.genai import types
from ..core.config import settings, get_content_config

# Models to try in order — if one is overloaded (503) or rate-limited (429), try next
FALLBACK_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-flash-lite-latest",
]


class AIService:
    @staticmethod
    def _get_client():
        if not settings.GEMINI_API_KEY:
            raise Exception("Gemini API key is missing. Set GEMINI_API_KEY in your .env file.")
        return genai.Client(api_key=settings.GEMINI_API_KEY)

    @staticmethod
    def _generate_with_fallback(client, contents: str, temperature: float = 0.2) -> str:
        """Try each model in FALLBACK_MODELS until one succeeds."""
        last_error = None
        for model_name in FALLBACK_MODELS:
            try:
                print(f"  Trying model: {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(temperature=temperature),
                )
                text = response.text.strip() if response.text else ""
                if text:
                    print(f"  Success with {model_name}")
                    return text
            except Exception as e:
                error_str = str(e)
                print(f"  {model_name} failed: {error_str[:100]}")
                last_error = e
                if "429" in error_str:
                    time.sleep(2)
                continue
        raise Exception(f"All Gemini models failed. Last error: {last_error}")

    @staticmethod
    def research_topic(topic: str, content_type: str, articles: list):
        config = get_content_config(content_type)
        client = AIService._get_client()

        if config["research_depth"] == "light":
            depth = (
                "Keep it concise. Focus on the single most important recent development "
                "and 2-3 key supporting facts."
            )
        else:
            depth = (
                "Be thorough and comprehensive. Cover multiple recent developments, "
                "provide historical context, build a detailed timeline, and note any "
                "conflicting reports between sources."
            )

        source_text = "\n\n".join(
            [f"SOURCE {i+1}: {a.get('title', '')}\n{a.get('content', '')}"
             for i, a in enumerate(articles)]
        )

        prompt = f"""You are an expert news researcher. Analyze these provided articles about: "{topic}"

{depth}

ARTICLES:
{source_text}

Structure your response clearly with these sections:
- SUMMARY: Brief overview of the current situation
- LATEST DEVELOPMENTS: Most recent news items (use bullet points)
- KEY FACTS: Important numbers, dates, statistics, quotes
- TIMELINE: Recent events in chronological order
- CONTEXT: Background information for understanding the story

Be factual and specific. Include dates and name your sources where possible."""

        return AIService._generate_with_fallback(client, prompt, temperature=0.2)

    @staticmethod
    def generate_script(topic: str, research_text: str, content_type: str) -> str:
        config = get_content_config(content_type)
        client = AIService._get_client()

        if config["script_depth"] == "short":
            fmt = """Format: TikTok / Instagram Reels / YouTube Shorts.
Target Length: Exactly 1 MINUTE when read aloud (approximately 150-180 words).

Structure:
HOOK — ek attention-grabbing opening line
KYA HUA — news ko 1-2 sentences mein batao
KYUN ZAROORI HAI — chhoti si context
KEY FACT — ek striking statistic ya quote
ENDING — call to action ya cliffhanger

Style: Punchy, fast-paced, conversational. Short sentences use karo.
The script MUST be approximately 150-180 words total — not more, not less."""
        else:
            fmt = """Format: YouTube explainer video.
Target Length: 7 to 10 MINUTES when read aloud (approximately 1000-1400 words).

Structure:
HOOK — compelling opening jo viewers ko attract kare
INTRODUCTION — topic set up karo
MAIN DEVELOPMENT — abhi kya ho raha hai, detail mein
CONTEXT — background aur history
KEY FACTS & FIGURES — important data points
TIMELINE — events ka chronological walkthrough
ANALYSIS — ye kyun important hai, implications
CONCLUSION — summary aur aage kya hoga

Style: Detailed but natural for spoken delivery. Conversational tone rakho.
The script MUST be approximately 1000-1400 words total — not more, not less."""

        prompt = f"""You are an expert scriptwriter for video content creators.
Topic: {topic}

IMPORTANT LANGUAGE INSTRUCTION: 
Write the ENTIRE script in ROMAN URDU (Urdu language written in English/Latin alphabet).
Example: "Assalam o alaikum doston, aaj hum baat karenge ek bohot hi interesting topic ke baare mein..."
Do NOT use Urdu script (نستعلیق). Use ONLY English letters to write Urdu words.
Mix common English words naturally where a Pakistani creator would (like "actually", "basically", "subscribe", etc.)

Based ONLY on the research provided below, write a compelling video script.

{fmt}

Write ONLY the script text. No stage directions, no markdown formatting, no [SECTION] labels.
The script should flow naturally as if a Pakistani YouTuber/content creator is speaking directly to camera.

RESEARCH:
{research_text}"""

        return AIService._generate_with_fallback(client, prompt, temperature=0.7)
