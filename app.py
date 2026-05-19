from flask import Flask, render_template, request, redirect, url_for
import threading
import time

app = Flask(__name__)

# --- Bot State & Logic ---
class BackgroundBot:
    def __init__(self):
        self.is_running = False
        self.status_message = "Idle"
        self.log = []

    def run(self):
        self.is_running = True
        self.status_message = "Bot is running..."
        self._add_log("Bot started successfully.")
        
        # Core Execution Loop
        while self.is_running:
            time.sleep(3) # Simulate processing time
            if self.is_running:
                timestamp = time.strftime('%H:%M:%S')
                self._add_log(f"[{timestamp}] Executed routine background task.")

    def stop(self):
        self.is_running = False
        self.status_message = "Idle"
        self._add_log("Bot stopped by user.")

    def _add_log(self, message):
        self.log.append(message)
        # Keep log array manageable (last 15 entries)
        if len(self.log) > 15:
            self.log.pop(0)

# Initialize the bot globally so routes can access it
bot = BackgroundBot()
bot_thread = None

# --- Web Routes ---
@app.route('/', methods=['GET'])
def index():
    # Serve the main HTML interface and pass the bot state to the template
    return render_template('index.html', bot=bot)

@app.route('/start', methods=['POST'])
def start_bot():
    global bot_thread
    # Start the bot in a background thread if it isn't already running
    if not bot.is_running:
        bot_thread = threading.Thread(target=bot.run)
        # Daemon threads exit automatically when the main program exits
        bot_thread.daemon = True 
        bot_thread.start()
    return redirect(url_for('index'))

@app.route('/stop', methods=['POST'])
def stop_bot():
    # Signal the bot loop to break
    if bot.is_running:
        bot.stop()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, host='127.0.0.1', port=5000, threaded=True)
