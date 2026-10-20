from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.schemas import GrammarErrorDetail, AICoreOutput, ScaffoldOutput




#  Mock AI/NLP Core MCP Client

class MockAINLPCoreClient:
    """
    Simulates the AI/NLP Core tool `analyze_text`.
    Spec: analyze(text) -> {is_correct, errors: [{span, rule_id, explanation_sw, explanation_en, correction}]}
    """
    def analyze_text(self, text: str) -> AICoreOutput:
        normalized = text.strip().lower()

        # Simulated test case 1: Subject-verb agreement (noun class m-/wa-)
        if "watoto anasoma" in normalized:
            return AICoreOutput(
                is_correct=False,
                errors=[
                    GrammarErrorDetail(
                        span="anasoma",
                        rule_id="rule_m_wa_01",
                        explanation_sw="Ngeli ya m-/wa- hutumika kwa majina ya watu. Umoja ni m- na wingi ni wa-.",
                        explanation_en="The m-/wa- class is for people. Singular takes m-, plural takes wa-.",
                        correction="wanasoma"
                    )
                ]
            )

        # Simulated test case 2: Tense marker error
        if "mimi kusoma sasa" in normalized:
            return AICoreOutput(
                is_correct=False,
                errors=[
                    GrammarErrorDetail(
                        span="kusoma",
                        rule_id="rule_tense_na_01",
                        explanation_sw="Wakati uliopo hutumia kiambishi -na-. Mfano: ninasoma.",
                        explanation_en="The present tense uses the marker -na-. Example: ninasoma (I am reading).",
                        correction="ninasoma"
                    )
                ]
            )

        return AICoreOutput(is_correct=True, errors=[])


# : Mock Pedagogical Engine MCP Client
class MockPedagogicalEngineClient:
    """
    Simulates the deterministic Pedagogical Engine tool `scaffold`.
    Spec: scaffold(learner_id, ai_core_output) -> {formatted_response, next_difficulty_level}
    """
    def scaffold(self, learner_id: str, ai_output: AICoreOutput, current_level: int = 1) -> ScaffoldOutput:
        # If the AI core found no errors, progress the learner
        if ai_output.is_correct or not ai_output.errors:
            return ScaffoldOutput(
                scaffold_type="passed",
                next_difficulty_level=current_level + 1,
                prompt_instruction="Praise the learner and present a challenge at the new level."
            )

        # For errors, simulate deterministic rule branching:
        # Beginners (level 1): explain rule with examples
        # Higher levels: provide hint only
        if current_level == 1:
            scaffold_type = "explain_rule"
            prompt_instruction = "Provide a full rule explanation with an example."
        else:
            scaffold_type = "hint_only"
            prompt_instruction = "Provide a hint without giving away the full correction."

        return ScaffoldOutput(
            scaffold_type=scaffold_type,
            next_difficulty_level=current_level,
            prompt_instruction=prompt_instruction
        )