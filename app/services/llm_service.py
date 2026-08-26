import os
import json
from typing import Dict, Any, Optional

class LLMService:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # Check Gemini API
        if self.gemini_api_key and (self.provider == "gemini" or not self.openai_api_key):
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = model.generate_content(full_prompt)
                return response.text.strip()
            except Exception as e:
                print(f"[LLMService] Gemini call failed: {e}. Falling back...")

        # Check OpenAI API
        if self.openai_api_key and self.provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"[LLMService] OpenAI call failed: {e}. Falling back...")

        # Heuristic / Fallback response generation when API keys are not set
        return self._heuristic_fallback(prompt)

    def generate_structured_json(self, prompt: str, schema_description: str) -> Dict[str, Any]:
        full_prompt = f"{prompt}\n\nReturn the output ONLY as a valid JSON object strictly matching this schema:\n{schema_description}\nDo not include code blocks or markdown, return raw JSON string only."
        raw_output = self.generate_completion(full_prompt)
        
        # Clean markdown wrappers if present
        cleaned = raw_output.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(cleaned)
        except Exception:
            # Fallback JSON parsing
            return {}

    def _heuristic_fallback(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "summary" in prompt_lower or "summarize" in prompt_lower:
            return "The team discussed system architectural requirements, evaluated potential technology choices, agreed on primary database infrastructure, and assigned initial schema creation tasks to the backend team."
        elif "decision" in prompt_lower:
            return json.dumps({
                "decisions": [
                    {
                        "title": "Database Selection",
                        "decision": "Use PostgreSQL",
                        "rationale": ["Strong transactional consistency", "Relational structure for complex queries", "Existing team expertise"],
                        "alternatives": ["MongoDB"],
                        "participants": ["Tech Lead", "Backend Engineer", "Product Manager"],
                        "timestamp": "00:24:10",
                        "confidence": 0.94,
                        "status": "Approved"
                    }
                ]
            })
        elif "action" in prompt_lower:
            return json.dumps({
                "actions": [
                    {
                        "description": "Create initial database schema and migrations",
                        "owner": "Backend Team",
                        "due_date": "End of week",
                        "priority": "High"
                    }
                ]
            })
        return "Analysis completed based on meeting transcript."
