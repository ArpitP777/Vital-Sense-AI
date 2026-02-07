from typing import Dict, List, Any


class FeedbackAnalyzer:
    
    @staticmethod
    def validate_score(score: Any, min_val: int = 1, max_val: int = 5) -> int:
        try:
            score_int = int(float(score))
            return max(min_val, min(max_val, score_int))
        except (ValueError, TypeError):
            return (min_val + max_val) // 2
    
    @staticmethod
    def clean_text(text: Any) -> str:
        if text is None:
            return ""
        cleaned = str(text).strip()
        cleaned = " ".join(cleaned.split())
        return cleaned
    
    @staticmethod
    def validate_confidence(value: Any) -> str:
        if value is None:
            return "partial"
        val_str = str(value).lower().strip()
        if val_str in ["yes", "y", "true", "1"]:
            return "yes"
        elif val_str in ["no", "n", "false", "0"]:
            return "no"
        return "partial"
    
    @staticmethod
    def validate_radar_metrics(metrics: Any) -> Dict[str, int]:
        default_metrics = {
            "felt_heard": 3,
            "concerns_addressed": 3,
            "clear_communication": 3,
            "respect_shown": 3,
            "time_given": 3
        }
        
        if not isinstance(metrics, dict):
            return default_metrics
        
        validated = {}
        for key in default_metrics.keys():
            validated[key] = FeedbackAnalyzer.validate_score(
                metrics.get(key, 3)
            )
        
        return validated
    
    @staticmethod
    def validate_bullets(bullets: Any) -> List[str]:
        if bullets is None:
            return ["No specific feedback provided."]
        
        if isinstance(bullets, str):
            bullets = [b.strip() for b in bullets.split(",") if b.strip()]
        
        if isinstance(bullets, list):
            cleaned = []
            for bullet in bullets[:5]:
                text = FeedbackAnalyzer.clean_text(bullet)
                if text:
                    cleaned.append(text)
            return cleaned if cleaned else ["No specific feedback provided."]
        
        return ["No specific feedback provided."]
    
    @staticmethod
    def process_llm_output(llm_response: Dict) -> Dict:
        if not isinstance(llm_response, dict):
            llm_response = {}
        
        satisfaction_score = FeedbackAnalyzer.validate_score(
            llm_response.get("satisfaction_score", 3)
        )
        
        radar_metrics = FeedbackAnalyzer.validate_radar_metrics(
            llm_response.get("radar_metrics", {})
        )
        
        confidence_in_treatment = FeedbackAnalyzer.validate_confidence(
            llm_response.get("confidence_in_treatment", "partial")
        )
        
        duration_satisfaction = FeedbackAnalyzer.validate_score(
            llm_response.get("duration_satisfaction", 3)
        )
        
        staff_behavior = FeedbackAnalyzer.validate_score(
            llm_response.get("staff_behavior", 3)
        )
        
        summary_bullets = FeedbackAnalyzer.validate_bullets(
            llm_response.get("summary_bullets", [])
        )
        
        feedback = {
            "satisfaction_score": satisfaction_score,
            "radar_metrics": radar_metrics,
            "confidence_in_treatment": confidence_in_treatment,
            "duration_satisfaction": duration_satisfaction,
            "staff_behavior": staff_behavior,
            "summary_bullets": summary_bullets
        }
        
        return feedback
    
    @staticmethod
    def format_feedback_display(feedback: Dict) -> str:
        score = feedback.get("satisfaction_score", 3)
        stars = "⭐" * score + "☆" * (5 - score)
        
        lines = [
            "\n" + "=" * 60,
            "FEEDBACK ANALYSIS COMPLETE",
            "=" * 60,
            f"\nSatisfaction Score: {score}/5 {stars}",
            f"\nConfidence in Treatment: {feedback.get('confidence_in_treatment', 'N/A').upper()}",
            f"Duration Satisfaction: {feedback.get('duration_satisfaction', 3)}/5",
            f"Staff Behavior: {feedback.get('staff_behavior', 3)}/5",
            "\nKey Points:"
        ]
        
        for i, bullet in enumerate(feedback.get("summary_bullets", []), 1):
            lines.append(f"  {i}. {bullet}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
