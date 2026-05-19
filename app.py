from flask import Flask, render_template, request, redirect, url_for
from google import genai
import threading
import time
import os

app = Flask(main.py)

# Initialize the Gemini Client using the official SDK
try:
    # client = genai.Client() automatically checks os.environ["GEMINI_API_KEY"]
    client = genai.Client()
except Exception as e:
    print("Warning: Failed to initialize Gemini Client. Is your GEMINI_API_KEY set?")
    client = None

# --- AI Bot State & Logic ---
class BackgroundAIBot:
    def __init__(self):
        self.is_running = False
        self.status_message = "Idle"
        self.log = []

    def run(self):
        if not client:
            self._add_log("[Error] Gemini API key missing. Cannot start AI.")
            return

        self.is_running = True
        self.status_message = "AI is thinking..."
        self._add_log("AI Bot successfully authenticated with Google AI Studio.")
        
        # Core AI Execution Loop
        while self.is_running:
            try:
                # Call the Gemini API using the recommended flash model
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents='Generate a very short, interesting, and obscure one-sentence fact about technology, space, or nature. Do not include introductory text.'
                )
                timestamp = time.strftime('%H:%M:%S')
                self._add_log(f"[{timestamp}] AI: {response.text.strip()}")
            except Exception as e:
                self._add_log(f"[Error] API Call Failed: {str(e)}")
            
            # Wait 15 seconds before the next call to respect rate limits.
            # Split into 1-second ticks so the bot can stop immediately when the user commands it.
            for _ in range(15):
                if not self.is_running:
                    break
                time.sleep(1)

    def stop(self):
        self.is_running = False
        self.status_message = "Idle"
        self._add_log("AI Bot stopped by user.")

    def _add_log(self, message):
        self.log.append(message)
        # Prevent memory leaks by keeping the log length manageable
        if len(self.log) > 15:
            self.log.pop(0)

bot = BackgroundAIBot()
bot_thread = None

# --- Web Server Routes ---
@app.route('/', methods=['GET'])
def index():
    # Pass the current state of our live bot instance straight into the template
    return render_template('index.html', bot=bot)

@app.route('/start', methods=['POST'])
def start_bot():
    global bot_thread
    if not bot.is_running:
        bot_thread = threading.Thread(target=bot.run)
        bot_thread.daemon = True 
        bot_thread.start()
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_bot():
    if bot.is_running:
        bot.stop()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Used for local development only. Render will execute via Gunicorn.
    app.run(debug=True, host='127.0.0.1', port=5000, threaded=True)
