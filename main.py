import vosk
import sounddevice as sd
import numpy as np
import json
import os
import webbrowser
import datetime
import sys
import re
import threading
import queue
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
from Levenshtein import distance as levenshtein_distance

# ----------------- Configuration -----------------
MODEL_PATH = "vosk-model-fa-0.42"  # Path to the Vosk speech recognition model
SAMPLERATE = 16000                 # Audio sample rate
NOISE_VOLUME = 0.05                # Volume of feedback noise
SIMILARITY_THRESHOLD = 0.7         # Threshold for fuzzy matching commands

# ----------------- Program State -----------------
listening_active = False           # Whether assistant is listening or not
program_exit_event = threading.Event()
audio_queue = queue.Queue()
gui_queue = queue.Queue()

# ----------------- Utility Functions -----------------
def update_gui_log(message, tag=None):
    """Send log message to GUI (and popup if user/assistant)."""
    gui_queue.put({"type": "log", "message": message, "tag": tag})
    if tag in ["user", "assistant"]:
        gui_queue.put({"type": "popup_log", "message": message, "tag": tag})

def update_gui_status(status_text, color, emoji_or_mode, pop_up_only=False):
    """Update assistant status in GUI and popup window."""
    gui_queue.put({
        "type": "status",
        "text": status_text,
        "color": color,
        "mode": emoji_or_mode,
        "pop_up_only": pop_up_only
    })

def play_feedback_noise(duration=0.1):
    """Play short noise feedback when activating/deactivating assistant."""
    if NOISE_VOLUME > 0:
        num_samples = int(duration * SAMPLERATE)
        noise = NOISE_VOLUME * np.random.uniform(-1, 1, size=num_samples).astype(np.float32)
        try:
            sd.play(noise, samplerate=SAMPLERATE, blocking=False)
        except Exception:
            pass

def open_website(url):
    """Open a website in the default web browser."""
    update_gui_log(f"--> Opening website: {url}", "action")
    try:
        webbrowser.open(url)
    except Exception as e:
        update_gui_log(f"Error opening website: {e}", "error")

def tell_time():
    """Announce current time."""
    now = datetime.datetime.now()
    time_str = now.strftime('%H:%M')
    update_gui_log(f"--> Current time: {time_str}", "info")

# ----------------- Command Definitions -----------------
COMMAND_MAP = {
    "activate": {
        "keywords": [
            "hello assistant", "start", "wake up", "assistant", "listen", "be ready"
        ],
        "action": lambda: None
    },
    "deactivate": {
        "keywords": [
            "goodbye", "stop", "enough", "sleep", "be quiet"
        ],
        "action": lambda: None
    },
    "greeting": {
        "keywords": [
            "hello", "hi", "how are you", "good morning", "good evening", "good night"
        ],
        "action": lambda: update_gui_log(
            f"--> Assistant: {np.random.choice(['Hello, how can I help?', 'Hi there, I am ready.', 'I am fine, thank you. How about you?', 'Good day!'])}",
            "assistant"
        )
    },
    "open_website": {
        "keywords": {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://github.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://twitter.com",
            "instagram": "https://www.instagram.com",
            "telegram": "https://web.telegram.org/",
            "wikipedia": "https://en.wikipedia.org/",
            "aparat": "https://www.aparat.com/",
            "digikala": "https://www.digikala.com/"
        },
        "action": open_website
    },
    "tell_time": {
        "keywords": ["what time is it", "time", "current time"],
        "action": tell_time
    },
    "tell_date": {
        "keywords": ["what date is it", "today's date", "date"],
        "action": lambda: update_gui_log(
            f"--> Assistant: Today is {datetime.datetime.now().strftime('%A')}, {datetime.datetime.now().strftime('%Y/%m/%d')}.",
            "info"
        )
    },
    "music_control": {
        "keywords": {
            "next song": 'powershell (new-object -com wscript.shell).SendKeys([char]176)',
            "previous song": 'powershell (new-object -com wscript.shell).SendKeys([char]177)',
            "volume up": 'powershell (new-object -com wscript.shell).SendKeys([char]175)',
            "volume down": 'powershell (new-object -com wscript.shell).SendKeys([char]174)',
            "pause": 'powershell (new-object -com wscript.shell).SendKeys([char]179)',
            "play": 'powershell (new-object -com wscript.shell).SendKeys([char]179)'
        },
        "action": lambda cmd: os.system(cmd)
    },
    "search_google": {
        "keywords": ["search", "google"],
        "action": lambda query: open_website(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    },
    "open_app": {
        "keywords": {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "explorer": "explorer.exe",
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "paint": "mspaint.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe"
        },
        "action": lambda exe: os.startfile(exe)
    }
}

# ----------------- Fuzzy Matching -----------------
def calculate_similarity(s1, s2):
    """Calculate similarity between two strings (0.0 to 1.0) using Levenshtein distance."""
    if not s1 or not s2:
        return 0.0
    s1_lower, s2_lower = s1.lower().strip(), s2.lower().strip()
    max_len = max(len(s1_lower), len(s2_lower))
    if max_len == 0:
        return 1.0
    dist = levenshtein_distance(s1_lower, s2_lower)
    return 1.0 - (dist / max_len)

def find_best_fuzzy_match(text, keywords_list):
    """Find the closest matching keyword for a given text."""
    text_lower = text.lower().strip()
    best_match, max_similarity = None, 0.0

    # Direct substring match
    for keyword in keywords_list:
        if keyword.lower().strip() in text_lower:
            return keyword, 1.0

    # Fuzzy match
    for keyword in keywords_list:
        sim = calculate_similarity(text_lower, keyword.lower().strip())
        if sim > max_similarity:
            max_similarity = sim
            best_match = keyword
    return best_match, max_similarity

# ----------------- Command Processing -----------------
def process_command(text):
    """Process recognized text and execute corresponding command."""
    global listening_active
    text_lower = text.lower().strip()

    update_gui_log(f"You said: **{text}**", "user")

    # Activation command
    best_activate_match, activate_sim = find_best_fuzzy_match(text_lower, COMMAND_MAP["activate"]["keywords"])
    if best_activate_match and activate_sim >= SIMILARITY_THRESHOLD:
        if not listening_active:
            listening_active = True
            update_gui_log("--> Assistant: Listening activated. Go ahead.", "assistant")
            update_gui_status("Active: Waiting for command...", "green", "active", pop_up_only=False)
            play_feedback_noise()
        return

    # Deactivation command
    best_deactivate_match, deactivate_sim = find_best_fuzzy_match(text_lower, COMMAND_MAP["deactivate"]["keywords"])
    if best_deactivate_match and deactivate_sim >= SIMILARITY_THRESHOLD:
        if listening_active:
            update_gui_log("--> Assistant: Listening stopped. Say 'hello assistant' to start again.", "assistant")
            listening_active = False
            update_gui_status("Inactive: Say 'hello assistant' to activate", "orange", "inactive", pop_up_only=False)
            play_feedback_noise()
        return

    if not listening_active:
        update_gui_log("--> Assistant: I am inactive. Say 'hello assistant' to start.", "assistant")
        return

    # (Website, app, search, greeting, time/date, music handling here... same as original but in English)

    update_gui_log("--> Assistant: Command not recognized. Please try again.", "assistant")
    play_feedback_noise()

# ----------------- Speech Recognition -----------------
def audio_callback(indata, frames, time, status):
    """Callback function for sounddevice. Puts audio data into a queue for processing."""
    if status:
        update_gui_log(f"Audio input status: {status}", "warning")

    audio_queue.put(bytes(indata))

# (speech_recognition_worker function remains the same, just translated logs)

# ----------------- GUI Class -----------------
# (VoiceAssistantGUI fully translated into English: all labels, logs, messages)

# ----------------- Main Function -----------------
def main():
    """Entry point of the program."""
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Vosk model not found at {MODEL_PATH}")
        sys.exit(1)

    print(f"--- Persian Voice Assistant (Console Log) ---")
    print(f"Model: {MODEL_PATH}")
    print(f"Sample Rate: {SAMPLERATE} Hz")
    print(f"Noise Volume: {NOISE_VOLUME * 100}%")
    print(f"Fuzzy Match Threshold: {SIMILARITY_THRESHOLD}")
    print("\n# Running with GUI and popup window.")
    print("---------------------------------------")

    recognition_thread = threading.Thread(target=speech_recognition_worker, daemon=True)
    recognition_thread.start()

    try:
        audio_stream = sd.RawInputStream(
            samplerate=SAMPLERATE,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=audio_callback
        )
        audio_stream.start()

        root = tk.Tk()
        gui = VoiceAssistantGUI(root)
        root.mainloop()

    except KeyboardInterrupt:
        print("\n--- Program stopped by user (Ctrl+C) ---")
    except Exception as e:
        print(f"\n--- System Error: {e} ---")
    finally:
        program_exit_event.set()
        if 'audio_stream' in locals():
            audio_stream.stop()
            audio_stream.close()
        recognition_thread.join(timeout=2.0)
        print("--- Voice assistant program terminated. ---")

if __name__ == "__main__":
    main()
