#!/usr/bin/env python3
"""
Website Text Change Monitor

This script monitors a website for changes in specific text content.
It fetches the webpage, extracts text, and compares it with previously saved content.
"""

import requests
import hashlib
import time
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup


class WebsiteMonitor:
    def __init__(self, url, target_text=None, storage_file="website_data.json"):
        """
        Initialize the website monitor.
        
        Args:
            url (str): The URL of the website to monitor
            target_text (str, optional): Specific text to monitor. If None, monitors entire page.
            storage_file (str): File to store previous website state
        """
        self.url = url
        self.target_text = target_text
        self.storage_file = storage_file
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_website(self):
        """
        Fetch the website content.
        
        Returns:
            str: The HTML content of the website
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching website: {e}")
            return None
    
    def extract_text(self, html_content):
        """
        Extract text from HTML content.
        
        Args:
            html_content (str): Raw HTML content
            
        Returns:
            str: Extracted text
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def find_target_text(self, full_text):
        """
        Check if target text exists in the full text.
        
        Args:
            full_text (str): The full text content
            
        Returns:
            dict: Information about the target text presence and context
        """
        if self.target_text is None:
            return {"found": True, "content": full_text}
        
        if self.target_text in full_text:
            # Find the context around the target text
            index = full_text.find(self.target_text)
            context_start = max(0, index - 100)
            context_end = min(len(full_text), index + len(self.target_text) + 100)
            context = full_text[context_start:context_end]
            
            return {
                "found": True,
                "content": self.target_text,
                "context": context
            }
        else:
            return {"found": False, "content": None}
    
    def calculate_hash(self, content):
        """
        Calculate MD5 hash of content.
        
        Args:
            content (str): Content to hash
            
        Returns:
            str: MD5 hash
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def load_previous_state(self):
        """
        Load the previous website state from storage.
        
        Returns:
            dict: Previous state or None if not found
        """
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return None
        return None
    
    def save_current_state(self, state):
        """
        Save the current website state to storage.
        
        Args:
            state (dict): Current state to save
        """
        with open(self.storage_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def check_changes(self):
        """
        Check if the website content has changed.
        
        Returns:
            dict: Change detection results
        """
        # Fetch current website
        html_content = self.fetch_website()
        if html_content is None:
            return {"error": "Failed to fetch website"}
        
        # Extract text
        full_text = self.extract_text(html_content)
        
        # Find target text or use full text
        target_result = self.find_target_text(full_text)
        
        if not target_result["found"]:
            return {
                "changed": None,
                "message": f"Target text '{self.target_text}' not found on page",
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate hash of monitored content
        content_to_monitor = target_result.get("content", full_text)
        current_hash = self.calculate_hash(content_to_monitor)
        
        # Load previous state
        previous_state = self.load_previous_state()
        
        # Prepare current state
        current_state = {
            "url": self.url,
            "hash": current_hash,
            "timestamp": datetime.now().isoformat(),
            "target_text": self.target_text,
            "content_preview": content_to_monitor[:200] if len(content_to_monitor) > 200 else content_to_monitor
        }
        
        # Check for changes
        if previous_state is None:
            # First time checking
            self.save_current_state(current_state)
            return {
                "changed": False,
                "message": "First time monitoring. Baseline saved.",
                "current_state": current_state
            }
        
        if current_hash != previous_state.get("hash"):
            # Content changed
            self.save_current_state(current_state)
            return {
                "changed": True,
                "message": "Content has changed!",
                "previous_state": previous_state,
                "current_state": current_state,
                "context": target_result.get("context")
            }
        else:
            # No change
            return {
                "changed": False,
                "message": "No changes detected.",
                "last_checked": current_state["timestamp"],
                "last_changed": previous_state.get("timestamp")
            }


def main():
    """
    Example usage of the WebsiteMonitor class.
    """
    # Example 1: Monitor entire website
    print("Example 1: Monitoring entire website")
    monitor1 = WebsiteMonitor(
        url="https://example.com",
        storage_file="example_full.json"
    )
    result1 = monitor1.check_changes()
    print(json.dumps(result1, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Example 2: Monitor specific text
    print("Example 2: Monitoring specific text")
    monitor2 = WebsiteMonitor(
        url="https://example.com",
        target_text="Example Domain",
        storage_file="example_specific.json"
    )
    result2 = monitor2.check_changes()
    print(json.dumps(result2, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Example 3: Continuous monitoring with interval
    print("Example 3: Continuous monitoring (press Ctrl+C to stop)")
    monitor3 = WebsiteMonitor(
        url="https://example.com",
        target_text="Example Domain",
        storage_file="example_continuous.json"
    )
    
    try:
        while True:
            result = monitor3.check_changes()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {result['message']}")
            
            if result.get('changed'):
                print("⚠️  ALERT: Content has changed!")
                print(json.dumps(result, indent=2))
            
            # Wait 60 seconds before next check
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()
