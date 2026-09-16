"""
Interactive Annotation Application
Allows human annotators to review customer tweets, select an empirical intent,
assign expected policy action (Auto-handle / Escalate), document reasoning,
and save verified ground-truth labels directly to data/golden_set.csv.
Run with: python frontend/annotation_app.py
"""

import os
import sys
import csv
import json
import http.server
import socketserver
import urllib.parse
import pandas as pd

PORT = 8501
CSV_PATH = "data/golden_set.csv"
CORPUS_PATH = "data/samples/apple_support_clean.parquet"

INTENTS = [
    "software_update_os_bug",
    "battery_power_charging",
    "account_apple_id_icloud",
    "hardware_physical_damage",
    "connectivity_network_bluetooth",
    "billing_subscriptions_appstore",
    "device_performance_storage",
    "general_feedback_complaint"
]

class AnnotationHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.render_html().encode('utf-8'))
        elif self.path == "/api/next":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            data = self.get_unlabeled_item()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/save":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            
            self.save_annotation(payload)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "saved"}).encode('utf-8'))

    def get_unlabeled_item(self):
        if os.path.exists(CORPUS_PATH):
            df = pd.read_parquet(CORPUS_PATH)
            sample = df.sample(n=1).iloc[0]
            return {
                "tweet_id": str(sample.get("customer_tweet_id", "")),
                "text": str(sample.get("customer_text", "")),
                "official_reply": str(sample.get("brand_reply_text", ""))
            }
        return {"tweet_id": "demo_01", "text": "My phone is getting extremely hot while charging", "official_reply": ""}

    def save_annotation(self, record):
        file_exists = os.path.exists(CSV_PATH)
        with open(CSV_PATH, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["example_id", "customer_text", "intent", "expected_action", "escalation_reason", "difficulty", "source_conversation_id"])
            writer.writerow([
                record.get("example_id", f"manual_{record.get('tweet_id', '')}"),
                record.get("customer_text", ""),
                record.get("intent", ""),
                record.get("expected_action", ""),
                record.get("escalation_reason", ""),
                record.get("difficulty", "medium"),
                record.get("tweet_id", "")
            ])

    def render_html(self):
        options = "".join([f'<option value="{i}">{i}</option>' for i in INTENTS])
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>AppleSupport Annotation Tool</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 30px; max-width: 800px; margin: auto; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; }}
        h2 {{ color: #58a6ff; margin-top: 0; }}
        .tweet-box {{ background: #0d1117; border-left: 4px solid #58a6ff; padding: 16px; margin: 16px 0; font-size: 16px; line-height: 1.5; }}
        label {{ display: block; font-weight: 600; margin: 14px 0 6px 0; }}
        select, input, textarea {{ width: 100%; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 10px; border-radius: 6px; font-size: 14px; box-sizing: border-box; }}
        button {{ background: #238636; color: white; border: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; cursor: pointer; margin-top: 20px; font-size: 14px; }}
        button:hover {{ background: #2ea043; }}
    </style>
</head>
<body>
    <div class="card">
        <h2> Customer Support Annotation Interface</h2>
        <p>Labeling guidelines available in <code>docs/annotation_guidelines.md</code></p>
        
        <label>Customer Tweet:</label>
        <div class="tweet-box" id="tweetText">Loading sample...</div>
        
        <label>Empirical Intent:</label>
        <select id="intentSelect">{options}</select>
        
        <label>Expected Policy Action:</label>
        <select id="actionSelect">
            <option value="auto_handle">Auto-handle (Routine self-help diagnostic)</option>
            <option value="escalate">Escalate (Safety, Hardware, Account Compromise)</option>
        </select>
        
        <label>Escalation Reason / Machine Code:</label>
        <input type="text" id="reasonInput" placeholder="e.g. SAFETY_HAZARD_BATTERY_SWELLING or ROUTINE_AUTO_HANDLE">
        
        <label>Difficulty:</label>
        <select id="diffSelect">
            <option value="easy">Easy (Unambiguous, single clear symptom)</option>
            <option value="medium">Medium (Requires slight inference or domain knowledge)</option>
            <option value="hard">Hard (Adversarial, sarcasm, multi-intent, or non-English)</option>
        </select>
        
        <button onclick="saveAnnotation()">Save Annotation & Next</button>
    </div>

    <script>
        let currentItem = {{}};
        async function loadNext() {{
            const res = await fetch('/api/next');
            currentItem = await res.json();
            document.getElementById('tweetText').innerText = `"${{currentItem.text}}"`;
            document.getElementById('reasonInput').value = '';
        }}
        async function saveAnnotation() {{
            const payload = {{
                tweet_id: currentItem.tweet_id,
                customer_text: currentItem.text,
                intent: document.getElementById('intentSelect').value,
                expected_action: document.getElementById('actionSelect').value,
                escalation_reason: document.getElementById('reasonInput').value || 'MANUAL_ANNOTATION',
                difficulty: document.getElementById('diffSelect').value
            }};
            await fetch('/api/save', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(payload)
            }});
            loadNext();
        }}
        loadNext();
    </script>
</body>
</html>
"""

def main():
    print(f"[*] Starting Human Annotation Server on http://localhost:{PORT}...")
    with socketserver.TCPServer(("", PORT), AnnotationHandler) as httpd:
        print(f"[OK] Annotation interface ready. Open http://localhost:{PORT} in your browser.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Stopping annotation server.")

if __name__ == "__main__":
    main()
