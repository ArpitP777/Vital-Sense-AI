"""
storage.py

Saves structured feedback into a CSV file.
Appends new entries with timestamp.
Handles file creation if CSV doesn't exist.
"""

import csv
import os
from datetime import datetime
from typing import Dict, List


class FeedbackStorage:
    """Handles storage of feedback data to CSV files."""
    
    def __init__(self, csv_file: str = "feedback_data.csv"):
        """
        Initialize storage manager.
        
        Args:
            csv_file: Path to the CSV file for storing feedback
        """
        self.csv_file = csv_file
        self.fieldnames = ["timestamp", "satisfaction_score", "summary", "key_issues"]
    
    def _ensure_file_exists(self):
        """Create CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
    
    def save_feedback(self, feedback: Dict) -> bool:
        """
        Save feedback entry to CSV file.
        
        Args:
            feedback: Feedback dictionary with satisfaction_score, summary, and key_issues
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            self._ensure_file_exists()
            
            # Prepare row data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            key_issues_str = "; ".join(feedback.get("key_issues", []))
            
            row = {
                "timestamp": timestamp,
                "satisfaction_score": feedback.get("satisfaction_score", 0),
                "summary": feedback.get("summary", ""),
                "key_issues": key_issues_str
            }
            
            # Append to CSV
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(row)
            
            return True
            
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False
    
    def load_all_feedback(self) -> List[Dict]:
        """
        Load all feedback entries from CSV.
        
        Returns:
            List of feedback dictionaries
        """
        try:
            if not os.path.exists(self.csv_file):
                return []
            
            feedback_list = []
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse key issues back to list
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


