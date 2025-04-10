
import speech_recognition as sr
from threading import Thread, Lock
from queue import Queue
import time
import logging

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.current_speech_text = "System ready. Waiting for your command..."
        self.speech_queue = Queue(maxsize=1)
        self.report_queue = Queue(maxsize=1)
        self.time_query_queue = Queue(maxsize=1)
        self.lock = Lock()
        self.running = True
        self.is_listening = True
        self.thread = Thread(target=self._speech_worker)
        self.thread.daemon = True
        self.thread.start()
        
        # Increased phrase time limit and pause threshold
        self.recognizer.pause_threshold = 1.0  # Increased from default 0.8
        self.recognizer.phrase_threshold = 0.5  # Increased from default 0.3
        self.recognizer.non_speaking_duration = 0.5  # Increased from default 0.5
        
        self.command_phrases = ["what is happening", "describe", "what's in front of me", 
                              "tell me about this", "what do you see", "can you describe"]
        self.report_phrases = ["what's the report", "give me the report", "tell me the report"]
        self.time_phrases = ["what happened on", "actions at", "description from", 
                           "what occurred at", "show me from", "tell me about"]

    def _speech_worker(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        while self.running:
            if self.is_listening:
                try:
                    with self.mic as source:
                        # Increased timeout and phrase time limit
                        audio = self.recognizer.listen(
                            source, 
                            timeout=5,  # Increased from None
                            phrase_time_limit=10  # Increased from 5
                        )
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    with self.lock:
                        self.current_speech_text = text
                        
                    # Buffer complete sentences
                    if any(cmd in text for cmd in self.time_phrases):
                        if self.time_query_queue.empty():
                            self.time_query_queue.put_nowait(text)
                            continue  # Prioritize time queries
                            
                    if any(cmd in text for cmd in self.command_phrases):
                        if self.speech_queue.empty():
                            self.speech_queue.put_nowait(text)
                    elif any(cmd in text for cmd in self.report_phrases):
                        if self.report_queue.empty():
                            self.report_queue.put_nowait(text)
                            
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    with self.lock:
                        self.current_speech_text = "Sorry, I didn't catch that. Please try again."
                except sr.RequestError:
                    with self.lock:
                        self.current_speech_text = "Speech service unavailable."
                except Exception as e:
                    logging.error(f"Speech error: {e}")
                    with self.lock:
                        self.current_speech_text = "Processing error occurred."
            time.sleep(0.1)

    # ... rest of the methods remain the same ...

    def get_speech_text(self):
        with self.lock:
            return self.current_speech_text

    def check_for_command(self):
        if not self.speech_queue.empty():
            return self.speech_queue.get_nowait()
        return None

    # def check_for_report_command(self):
    #     if not self.report_queue.empty():
    #         return self.report_queue.get_nowait()
    #     return None

    def check_time_query(self):
        if not self.time_query_queue.empty():
            return self.time_query_queue.get_nowait()
        return None

    def pause_listening(self):
        self.is_listening = False

    def resume_listening(self):
        self.is_listening = True

    def stop(self):
        self.running = False
        self.thread.join()


# import speech_recognition as sr
# from threading import Thread, Lock, Event
# from queue import Queue
# import time
# import logging
# import calendar

# class SpeechHandler:
#     def __init__(self):
#         self.recognizer = sr.Recognizer()
#         self.mic = sr.Microphone()
#         self.current_speech_text = "System ready. Waiting for your command..."
#         self.speech_queue = Queue(maxsize=1)
#         self.report_queue = Queue(maxsize=1)
#         self.time_query_queue = Queue(maxsize=1)
#         self.date_query_queue = Queue(maxsize=1) # New queue for date queries
#         self.lock = Lock()
#         self.running = True
#         self.is_listening = True
#         self.listen_thread = None
#         self.stop_listening_event = Event()
#         self.listening_for_date = False

#         # Increased phrase time limit and pause threshold
#         self.recognizer.pause_threshold = 1.0  # Increased from default 0.8
#         self.recognizer.phrase_threshold = 0.5  # Increased from default 0.3
#         self.recognizer.non_speaking_duration = 0.5  # Increased from default 0.5

#         self.command_phrases = ["what is happening", "describe", "what's in front of me",
#                                 "tell me about this", "what do you see", "can you describe"]
#         self.report_phrases = ["what's the report", "give me the report", "tell me the report"]
#         self.time_phrases = ["what happened on", "actions at", "description from",
#                                "what occurred at", "show me from", "tell me about"]
#         self.date_phrases = ["on", "for", "from"] # Keywords that might precede a date

#     def _speech_worker(self):
#         with self.mic as source:
#             self.recognizer.adjust_for_ambient_noise(source, duration=2)

#         while self.running:
#             if self.is_listening or self.listening_for_date:
#                 try:
#                     with self.mic as source:
#                         print(f"Listening... (is_listening: {self.is_listening}, listening_for_date: {self.listening_for_date})")
#                         audio = self.recognizer.listen(
#                             source,
#                             timeout=5,  # Increased from None
#                             phrase_time_limit=10  # Increased from 5
#                         )
#                     text = self.recognizer.recognize_google(audio).lower()
#                     print(f"Heard: {text}")

#                     with self.lock:
#                         self.current_speech_text = text

#                     if self.listening_for_date:
#                         self._process_date_input(text)
#                     elif any(cmd in text for cmd in self.time_phrases):
#                         if self.time_query_queue.empty():
#                             self.time_query_queue.put_nowait(text)
#                             continue  # Prioritize time queries
#                     elif any(cmd in text for cmd in self.command_phrases):
#                         if self.speech_queue.empty():
#                             self.speech_queue.put_nowait(text)
#                     elif any(cmd in text for cmd in self.report_phrases):
#                         if self.report_queue.empty():
#                             self.report_queue.put_nowait(text)

#                 except sr.WaitTimeoutError:
#                     continue
#                 except sr.UnknownValueError:
#                     with self.lock:
#                         self.current_speech_text = "Sorry, I didn't catch that. Please try again."
#                 except sr.RequestError:
#                     with self.lock:
#                         self.current_speech_text = "Speech service unavailable."
#                 except Exception as e:
#                     logging.error(f"Speech error: {e}")
#                     with self.lock:
#                         self.current_speech_text = "Processing error occurred."
#                 time.sleep(0.1)
#             else:
#                 time.sleep(0.5) # Reduce CPU usage when not actively listening

#     def _process_date_input(self, text):
#         parts = text.split()
#         day = None
#         month = None
#         for part in parts:
#             if part.isdigit():
#                 day = int(part)
#             elif part in [month_name.lower() for month_name in calendar.month_name[1:]]:
#                 month = part
#                 break
#         if day is not None and month is not None:
#             try:
#                 month_number = list(calendar.month_name).index(month.capitalize())
#                 self.date_query_queue.put((day, month_number))
#                 self.listening_for_date = False
#             except ValueError:
#                 logging.warning(f"Could not convert month: {month}")
#         elif "cancel" in text or "stop" in text or "nevermind" in text:
#             self.date_query_queue.put(None) # Indicate cancellation
#             self.listening_for_date = False
#         else:
#             print("Heard for date, but didn't recognize a clear date.")

#     def get_speech_text(self):
#         with self.lock:
#             return self.current_speech_text

#     def check_for_command(self):
#         if not self.speech_queue.empty():
#             return self.speech_queue.get_nowait()
#         return None

#     def check_time_query(self):
#         if not self.time_query_queue.empty():
#             return self.time_query_queue.get_nowait()
#         return None

#     def check_for_date(self):
#         if not self.date_query_queue.empty():
#             return self.date_query_queue.get_nowait()
#         return None

#     def start_listening_for_date(self):
#         print("Starting to listen specifically for a date.")
#         self.listening_for_date = True

#     def pause_listening(self):
#         self.is_listening = False

#     def resume_listening(self):
#         self.is_listening = True

#     def stop(self):
#         self.running = False
#         if self.listen_thread and self.listen_thread.is_alive():
#             self.stop_listening_event.set()
#             self.listen_thread.join(timeout=1)