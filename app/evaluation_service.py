import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer

class ExerciseEvaluator:
    def __init__(self, json_path: str):
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.exercises = json.load(f)
        self.embedding_model = SentenceTransformer('BAAI/bge-m3', device='cpu')
        
    def _normalize_text(self, text: str) -> str:
        """Kusafisha maandishi kwa kuondoa herufi kubwa na alama za vituo."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def get_exercise_by_id(self, exercise_id: str) -> dict:
        """Tafuta swali kulingana na ID yake."""
        for ex in self.exercises:
            if ex["exercise_id"] == exercise_id:
                return ex
        return None

    def evaluate_answer(self, exercise_id: str, student_answer: str) -> dict:
        """Tathmini jibu la mwanafunzi kulingana na JSON."""
        exercise = self.get_exercise_by_id(exercise_id)
        if not exercise:
            return {"status": "error", "message": "Swali halikupatikana."}

        expected_answers = exercise["expected_answers"]
        norm_student = self._normalize_text(student_answer)
        
        for expected in expected_answers:
            
            clean_expected = re.sub(r'\\', '', expected)
            norm_expected = self._normalize_text(clean_expected)
            
            if norm_student == norm_expected or norm_expected in norm_student:
                return {
                    "is_correct": True, 
                    "method": "exact_match",
                    "feedback": f"Vizuri sana! Jibu sahihi ni: {clean_expected}"
                }

    
        student_emb = self.embedding_model.encode(norm_student)
        
        best_score = 0
        best_match = ""
        
        for expected in expected_answers:
            clean_expected = re.sub(r'\\', '', expected)
            expected_emb = self.embedding_model.encode(self._normalize_text(clean_expected))
            
            
            similarity = np.dot(student_emb, expected_emb) / (np.linalg.norm(student_emb) * np.linalg.norm(expected_emb))
            if similarity > best_score:
                best_score = similarity
                best_match = clean_expected
                
        
        if best_score >= 0.85:
            return {
                "is_correct": True,
                "method": "semantic_similarity",
                "score": float(best_score),
                "feedback": f"Sahihi! Umeeleza vizuri. Kwa ufupi: {best_match}"
            }
        else:
            return {
                "is_correct": False,
                "method": "semantic_similarity",
                "score": float(best_score),
                "feedback": f"Siyo sahihi. Jibu sahihi linapaswa kuwa: {expected_answers[0]}"
            }