import os
import datetime
import requests
import json
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from gtts import gTTS

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

def speak_text(text):
    def run_speech():
        try:
            filename = "voice.mp3"
            if os.path.exists(filename):
                os.remove(filename)
            tts = gTTS(text=text, lang='en')
            tts.save(filename)
            os.system(f"am start -a android.intent.action.VIEW -d file://{os.path.abspath(filename)} -t audio/mp3 > /dev/null 2>&1")
        except Exception as e:
            print(f"Audio Error: {e}")

    threading.Thread(target=run_speech).start()

def ask_gemini_ai(prompt):
    if GEMINI_API_KEY == "AQ.Ab8RN6L5HqZMY8Xagwkx7RBfUAdSLl_JoVTYkAXZvBlg8kcIBg":
        return "Please paste your valid Gemini API Key inside main.py."
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": f"Answer in 1 or 2 short sentences for a voice assistant: {prompt}"}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return f"API Error ({response.status_code})"
    except Exception as e:
        return f"Connection error: {e}"

class JarvisUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=10, **kwargs)
        
        self.output_label = Label(
            text="[b]JARVIS Assistant Ready...[/b]\nSend a command below.", 
            markup=True,
            size_hint_y=0.75, 
            halign="left", 
            valign="top"
        )
        self.output_label.bind(size=self.output_label.setter('text_size'))
        self.add_widget(self.output_label)
        
        self.input_text = TextInput(
            hint_text="Type command (e.g., time, date, hello)...", 
            multiline=False, 
            size_hint_y=0.12,
            font_size='18sp'
        )
        self.add_widget(self.input_text)
        
        self.send_btn = Button(
            text="SEND COMMAND", 
            size_hint_y=0.13, 
            background_color=(0.1, 0.6, 0.9, 1),
            font_size='16sp',
            bold=True
        )
        self.send_btn.bind(on_press=self.process_command)
        self.add_widget(self.send_btn)

    def process_command(self, instance):
        command = self.input_text.text.strip()
        if not command:
            return
        
        self.input_text.text = ""
        command_lower = command.lower()
        
        if 'time' in command_lower:
            reply = f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}"
        elif 'date' in command_lower or 'today' in command_lower:
            reply = f"Today's date is {datetime.datetime.now().strftime('%B %d, %Y')}"
        else:
            reply = ask_gemini_ai(command)
            
        self.output_label.text = f"[b]You:[/b] {command}\n\n[b]JARVIS:[/b] {reply}"
        speak_text(reply)

class JarvisApp(App):
    def build(self):
        self.title = "JARVIS AI Assistant"
        return JarvisUI()

if __name__ == "__main__":
    JarvisApp().run()
