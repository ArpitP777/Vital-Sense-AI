import csv
import os
from datetime import datetime
from typing import Dict, List


class FeedbackStorage:
    
    def __init__(self, csv_file: str = "feedback_data.csv"):
        self.csv_file = csv_file
        self.fieldnames = ["timestamp", "satisfaction_score", "summary", "key_issues"]
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
    
    def save_feedback(self, feedback: Dict) -> bool:
        try:
            self._ensure_file_exists()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            key_issues_str = "; ".join(feedback.get("key_issues", []))
            
            row = {
                "timestamp": timestamp,
                "satisfaction_score": feedback.get("satisfaction_score", 0),
                "summary": feedback.get("summary", ""),
                "key_issues": key_issues_str
            }
            
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(row)
            
            return True
            
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def load_all_feedback(self) -> List[Dict]:
        try:
            if not os.path.exists(self.csv_file):
                return []
            
            feedback_list = []
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key_issues = row["key_issues"].split("; ") if row["key_issues"] else []
                    feedback_list.append({
                        "timestamp": row["timestamp"],
                        "satisfaction_score": int(row["satisfaction_score"]),
                        "summary": row["summary"],
                        "key_issues": key_issues
                    })
            
            return feedback_list
            
        except Exception as e:
            print(f"Error loading feedback: {e}")
            return []
