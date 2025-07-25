import os
import logging
from datetime import datetime
from gtts import gTTS
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load .env variables
load_dotenv()
api_key_loaded = os.getenv("OPENAI_API_KEY")
if not api_key_loaded:
    logging.error("OPENAI_API_KEY not found in environment. Check your .env file.")
else:
    logging.info("OPENAI_API_KEY loaded successfully.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key_loaded)

class VoiceChatbot:
    """
    Voice-enabled multilingual AI agriculture assistant with ChatGPT integration and TTS.
    Supports Telugu, Hindi, and English for speech-enabled conversation.
    """

    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'te': 'Telugu'
        }

    def process_message(self, message, language='en'):
        """
        Get AI-generated farming response for the user message using OpenAI ChatGPT.
        """
        try:
            prompt = (
                f"You are a helpful agriculture assistant who replies in {self.supported_languages.get(language, 'English')} "
                f"and provides clear, practical, beginner-friendly, step-by-step farming advice. "
                f"Do not apologize or repeat instructions. If the question is unrelated to agriculture, politely redirect the user. "
                f"\n\nUser Question:\n{message}"
            )

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable, friendly smart agriculture assistant helping small farmers with practical guidance."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )

            ai_reply = response.choices[0].message.content.strip()
            logging.info(f"Generated AI response: {ai_reply}")
            return ai_reply

        except Exception as e:
            logging.error(f"Error generating AI response: {e}")
            return self._get_error_response(language)

    def text_to_speech(self, text, language='en'):
        """
        Generate and save speech audio from the text using gTTS.
        Returns the filename for the generated audio inside 'static/audio'.
        """
        try:
            lang_map = {'en': 'en', 'hi': 'hi', 'te': 'te'}

            # Ensure 'static/audio' directory exists
            audio_dir = Path("static/audio")
            audio_dir.mkdir(parents=True, exist_ok=True)

            tts = gTTS(text=text, lang=lang_map.get(language, 'en'))
            filename = f"static/audio/response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            tts.save(filename)

            logging.info(f"TTS audio saved as {filename}")
            return {
                'status': 'success',
                'message': 'TTS audio generated successfully.',
                'audio_file': filename
            }

        except Exception as e:
            logging.error(f"TTS error: {e}")
            return {
                'status': 'error',
                'message': 'Text-to-speech conversion failed.'
            }

    def _get_error_response(self, language):
        """
        Return a user-friendly error message in the specified language.
        """
        responses = {
            'en': "Sorry, I had trouble understanding your question. Please try again.",
            'hi': "माफ करें, मुझे आपका प्रश्न समझने में परेशानी हुई। कृपया फिर से प्रयास करें।",
            'te': "క్షమించండి, మీ ప్రశ్నను అర్థం చేసుకోవడంలో నాకు ఇబ్బంది వచ్చింది. దయచేసి మళ్లీ ప్రయత్నించండి."
        }
        return responses.get(language, responses['en'])


# Example testing block for local validation
if __name__ == "__main__":
    chatbot = VoiceChatbot()
    user_message = input("Enter your farming question: ")
    language_choice = input("Enter language (en/hi/te): ").strip() or 'en'

    response_text = chatbot.process_message(user_message, language_choice)
    print("\nAssistant:", response_text)

    # Generate TTS
    tts_result = chatbot.text_to_speech(response_text, language_choice)
    print(tts_result)
