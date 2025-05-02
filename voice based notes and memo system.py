import os
import json
import datetime
import time
import threading
import speech_recognition as sr
import pyttsx3
import dateparser

class VoiceAssistant:
    def __init__(self, wake_word="hey assistant", user_name="User"):
        self.WAKE_WORD = wake_word.lower()
        self.USER_NAME = user_name
        self.keep_running = True

        self.setup_voice_engine()
        self.setup_voice_recognition()
        self.setup_data_storage()
        self.start_background_services()

        print(f"{self.USER_NAME}'s Assistant Ready!")

    def setup_voice_engine(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 170)
        self.engine.setProperty('volume', 1.0)
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)

    def setup_voice_recognition(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def setup_data_storage(self):
        self.data_dir = "assistant_data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_file = os.path.join(self.data_dir, "assistant_data.json")
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            else:
                self.data = {
                    "reminders": [],
                    "notes": [],
                    "preferences": {
                        "wake_word": self.WAKE_WORD,
                        "user_name": self.USER_NAME
                    }
                }
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = {"reminders": [], "notes": [], "preferences": {}}

    def save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")

    def start_background_services(self):
        self.reminder_thread = threading.Thread(target=self.check_reminders)
        self.reminder_thread.daemon = True
        self.reminder_thread.start()

    def speak(self, text):
        print(f"Assistant: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error in speech synthesis: {e}")

    def listen(self):
        with self.microphone as source:
            print("\nListening...")
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                text = self.recognizer.recognize_google(audio).lower()
                print(f"You: {text}")
                return text
            except sr.WaitTimeoutError:
                print("Listening timed out")
                return None
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except Exception as e:
                print(f"Recognition error: {e}")
                return None

    def parse_reminder_time(self, time_str):
        if time_str.startswith("in "):
            time_str = time_str[3:]

        parsed_time = dateparser.parse(
            time_str,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.datetime.now(),
                'RETURN_AS_TIMEZONE_AWARE': False
            }
        )

        if not parsed_time:
            try:
                if "second" in time_str:
                    seconds = int(time_str.split()[0])
                    parsed_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
                elif "minute" in time_str:
                    minutes = int(time_str.split()[0])
                    parsed_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
                elif "hour" in time_str:
                    hours = int(time_str.split()[0])
                    parsed_time = datetime.datetime.now() + datetime.timedelta(hours=hours)
            except:
                pass

        return parsed_time

    def add_reminder(self, what, when_str):
        reminder_time = self.parse_reminder_time(when_str)
        if not reminder_time:
            return "Sorry, I didn't understand that time format"

        if reminder_time < datetime.datetime.now():
            return "That time has already passed! Please set a future reminder."

        self.data["reminders"].append({
            "what": what,
            "when": reminder_time.strftime("%Y-%m-%d %H:%M:%S"),
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_data()

        time_diff = reminder_time - datetime.datetime.now()
        if time_diff.total_seconds() < 60:
            return f"I'll remind you to {what} in {int(time_diff.total_seconds())} seconds"
        elif time_diff.total_seconds() < 3600:
            return f"I'll remind you to {what} in {int(time_diff.total_seconds() / 60)} minutes"
        else:
            return f"Reminder set for {reminder_time.strftime('%I:%M %p on %A')} to {what}"

    def check_reminders(self):
        while self.keep_running:
            now = datetime.datetime.now()
            reminders_to_trigger = []

            for reminder in self.data["reminders"]:
                try:
                    reminder_time = datetime.datetime.strptime(reminder["when"], "%Y-%m-%d %H:%M:%S")
                    if now >= reminder_time:
                        reminders_to_trigger.append(reminder)
                except Exception as e:
                    print(f"Error processing reminder: {e}")
                    continue

            if reminders_to_trigger:
                for reminder in reminders_to_trigger:
                    self.speak(f"🔔 Reminder! {reminder['what']}")
                    self.data["reminders"].remove(reminder)
                self.save_data()
                time.sleep(2)

            time.sleep(1)

    def show_reminders(self):
        if not self.data["reminders"]:
            return "You have no reminders set"

        try:
            sorted_reminders = sorted(
                self.data["reminders"],
                key=lambda x: datetime.datetime.strptime(x["when"], "%Y-%m-%d %H:%M:%S")
            )

            response = "📅 Your reminders:\n"
            for i, reminder in enumerate(sorted_reminders, 1):
                when = datetime.datetime.strptime(reminder["when"], "%Y-%m-%d %H:%M:%S")
                time_diff = when - datetime.datetime.now()

                if time_diff.total_seconds() < 60:
                    time_str = f"in {int(time_diff.total_seconds())} seconds"
                elif time_diff.total_seconds() < 3600:
                    time_str = f"in {int(time_diff.total_seconds() / 60)} minutes"
                else:
                    time_str = when.strftime("%a %I:%M %p")

                response += f"{i}. {reminder['what']} ({time_str})\n"

            return response
        except Exception as e:
            print(f"Error showing reminders: {e}")
            return "Couldn't retrieve reminders"

    def show_my_reminders(self):
        return self.show_reminders()

    def add_note(self, text):
        if not text.strip():
            return "Please say something to add as a note"

        self.data["notes"].append({
            "text": text,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_data()
        return f"Note added: {text}"

    def show_notes(self):
        if not self.data["notes"]:
            return "You have no notes"

        try:
            response = "📝 Your notes:\n"
            for i, note in enumerate(reversed(self.data["notes"]), 1):
                note_time = datetime.datetime.strptime(note["time"], "%Y-%m-%d %H:%M:%S")
                response += f"{i}. {note['text']} ({note_time.strftime('%Y-%m-%d %H:%M')})\n"
            return response
        except Exception as e:
            print(f"Error showing notes: {e}")
            return "Couldn't retrieve notes"

    def show_calendar(self, day_str="today"):
        """Show reminders for a specific date"""
        try:
            date_obj = dateparser.parse(day_str)
            if not date_obj:
                return "I couldn't understand the date you said."

            date_str = date_obj.strftime("%Y-%m-%d")
            events = []

            for reminder in self.data["reminders"]:
                when = datetime.datetime.strptime(reminder["when"], "%Y-%m-%d %H:%M:%S")
                if when.strftime("%Y-%m-%d") == date_str:
                    events.append(f"- {when.strftime('%I:%M %p')}: {reminder['what']}")

            if not events:
                return f"You have no events on {date_str}"

            return f"📅 Events for {date_str}:\n" + "\n".join(events)

        except Exception as e:
            print(f"Error in show_calendar: {e}")
            return "Sorry, I couldn't get your calendar."

    def handle_reminder_command(self, command):
        try:
            if " in " in command and (" to " in command or " about " in command):
                parts = command.split(" in ", 1)
                action_part = parts[1]

                if " to " in action_part:
                    time_part, what = action_part.split(" to ", 1)
                elif " about " in action_part:
                    time_part, what = action_part.split(" about ", 1)
                else:
                    return "Try: 'remind me in [time] to [action]'"

                return self.add_reminder(what.strip(), f"in {time_part.strip()}")

            elif " to " in command and " in " in command:
                parts = command.split(" to ", 1)
                action_part = parts[1]

                if " in " in action_part:
                    what, time_part = action_part.split(" in ", 1)
                    return self.add_reminder(what.strip(), f"in {time_part.strip()}")

            elif " to " in command:
                parts = command.split(" to ", 1)
                when, what = parts[0].replace("remind me", "").strip(), parts[1].strip()
            elif " at " in command:
                parts = command.split(" at ", 1)
                what, when = parts[0].replace("remind me", "").strip(), parts[1].strip()
            else:
                return "Try: 'remind me to [action] at [time]' or 'remind me in [time] to [action]'"

            return self.add_reminder(what, when)
        except Exception as e:
            print(f"Error processing reminder command: {e}")
            return "Sorry, I couldn't set that reminder"

    def process_command(self, command):
        if not command:
            return None

        command = command.lower()

        if command.startswith("set wake word"):
            new_word = command[13:].strip()
            if new_word:
                self.WAKE_WORD = new_word
                self.data["preferences"]["wake_word"] = new_word
                self.save_data()
                return f"Wake word updated to: {new_word}"

        elif command.startswith("set name"):
            new_name = command[9:].strip()
            if new_name:
                self.USER_NAME = new_name
                self.data["preferences"]["user_name"] = new_name
                self.save_data()
                return f"Okay, I'll call you {new_name}"

        elif "remind me" in command or "set reminder" in command:
            return self.handle_reminder_command(command)

        elif "my reminders" in command or "show reminders" in command:
            return self.show_my_reminders()

        elif "add note" in command:
            return self.add_note(command.replace("add note", "").strip())

        elif "my notes" in command or "show notes" in command:
            return self.show_notes()

        elif "show calendar" in command:
            return self.show_calendar("today")

        elif "calendar for" in command:
            date_str = command.split("calendar for")[-1].strip()
            return self.show_calendar(date_str)

        elif any(word in command for word in ["hello", "hi", "hey"]):
            return f"Hello {self.USER_NAME}! How can I help?"

        elif any(word in command for word in ["time", "what time"]):
            return f"It's {datetime.datetime.now().strftime('%I:%M %p')}"

        elif any(word in command for word in ["date", "what day"]):
            return f"Today is {datetime.datetime.now().strftime('%A, %B %d')}"

        elif any(word in command for word in ["goodbye", "exit", "quit", "stop"]):
            self.keep_running = False
            return f"Goodbye {self.USER_NAME}! Shutting down..."

        else:
            return "I didn't understand that. Try saying 'remind me to...' or 'add note...'"

    def run(self):
        self.speak(f"Hello {self.USER_NAME}! Say '{self.WAKE_WORD}' when you need me.")

        try:
            while self.keep_running:
                command = self.listen()

                if command and self.WAKE_WORD in command:
                    self.speak("Yes?")
                    while self.keep_running:
                        new_command = self.listen()
                        if not new_command:
                            self.speak("I didn't hear anything. Going back to sleep.")
                            break

                        response = self.process_command(new_command)
                        if response:
                            self.speak(response)

                        if not self.keep_running:
                            break
        except KeyboardInterrupt:
            self.speak("Shutting down...")
        finally:
            self.save_data()


if __name__ == "__main__":
    assistant = VoiceAssistant(wake_word="hey assistant", user_name="User")
    assistant.run()

if __name__ == "__main__":
    Bellione().run()
