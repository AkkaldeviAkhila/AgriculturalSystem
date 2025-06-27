import os
import logging
import json
import re
import random
from datetime import datetime

class VoiceChatbot:
    """
    Voice-enabled chatbot for agriculture assistance
    Supports Telugu, Hindi, and English languages
    """
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi', 
            'te': 'Telugu'
        }
        
        # Agriculture knowledge base
        self.knowledge_base = {
            'greetings': {
                'en': ['Hello! How can I help you with farming today?', 
                       'Welcome to the Agriculture Assistant!',
                       'Hi there! What farming question do you have?'],
                'hi': ['नमस्ते! आज मैं खेती में आपकी कैसे मदद कर सकता हूं?',
                       'कृषि सहायक में आपका स्वागत है!',
                       'नमस्कार! आपका कृषि संबंधी कोई प्रश्न है?'],
                'te': ['నమస్కారం! ఈరోజు వ్యవసాయంలో మీకు ఎలా సహాయం చేయగలను?',
                       'వ్యవసాయ సహాయకుడికి స్వాగతం!',
                       'హలో! మీకు ఏమైనా వ్యవసాయ ప్రశ్న ఉందా?']
            },
            'soil_care': {
                'en': [
                    'Test your soil pH regularly. Most crops prefer 6.0-7.0 pH.',
                    'Add organic compost to improve soil structure and fertility.',
                    'Practice crop rotation to maintain soil health.',
                    'Use cover crops during off-season to prevent erosion.'
                ],
                'hi': [
                    'नियमित रूप से अपनी मिट्टी का पीएच परीक्षण करें। अधिकांश फसलें 6.0-7.0 पीएच पसंद करती हैं।',
                    'मिट्टी की संरचना और उर्वरता में सुधार के लिए जैविक खाद डालें।',
                    'मिट्टी के स्वास्थ्य को बनाए रखने के लिए फसल चक्र का अभ्यास करें।',
                    'कटाव को रोकने के लिए ऑफ-सीजन के दौरान कवर क्रॉप्स का उपयोग करें।'
                ],
                'te': [
                    'మీ మట్టి pH ని క్రమం తప్పకుండా పరీక్షించండి. చాలా పంటలు 6.0-7.0 pH ని ఇష్టపడతాయి.',
                    'మట్టి నిర్మాణం మరియు ఫలదీకరణను మెరుగుపరచడానికి సేంద్రీయ ఎరువులను చేర్చండి.',
                    'మట్టి ఆరోగ్యాన్ని కాపాడుకోవడానికి పంట మార్పిడిని అభ్యసించండి.',
                    'కోత నిరోధించడానికి ఆఫ్-సీజన్‌లో కవర్ క్రాప్‌లను ఉపయోగించండి.'
                ]
            },
            'pest_control': {
                'en': [
                    'Use integrated pest management (IPM) approach.',
                    'Encourage beneficial insects like ladybugs and spiders.',
                    'Neem oil is an effective organic pesticide.',
                    'Remove infected plants immediately to prevent spread.'
                ],
                'hi': [
                    'एकीकृत कीट प्रबंधन (आईपीएम) दृष्टिकोण का उपयोग करें।',
                    'लेडीबग्स और मकड़ियों जैसे लाभकारी कीड़ों को प्रोत्साहित करें।',
                    'नीम का तेल एक प्रभावी जैविक कीटनाशक है।',
                    'फैलाव को रोकने के लिए संक्रमित पौधों को तुरंत हटा दें।'
                ],
                'te': [
                    'సమగ్ర చీడపీడల నిర్వహణ (IPM) విధానాన్ని ఉపయోగించండి.',
                    'లేడీబగ్స్ మరియు సాలెపురుగుల వంటి మేలైన కీటకాలను ప్రోత్సహించండి.',
                    'వేప నూనె ఒక ప్రభావవంతమైన సేంద్రీయ కీటనాశకం.',
                    'వ్యాప్తిని నిరోధించడానికి వ్యాధిగ్రస్త మొక్కలను వెంటనే తొలగించండి.'
                ]
            },
            'irrigation': {
                'en': [
                    'Use drip irrigation to save water and improve efficiency.',
                    'Water early morning or late evening to reduce evaporation.',
                    'Mulch around plants to retain soil moisture.',
                    'Check soil moisture before watering to avoid over-watering.'
                ],
                'hi': [
                    'पानी बचाने और दक्षता में सुधार के लिए ड्रिप सिंचाई का उपयोग करें।',
                    'वाष्पीकरण कम करने के लिए सुबह जल्दी या देर शाम पानी दें।',
                    'मिट्टी की नमी बनाए रखने के लिए पौधों के चारों ओर मल्च करें।',
                    'अधिक पानी देने से बचने के लिए पानी देने से पहले मिट्टी की नमी जांचें।'
                ],
                'te': [
                    'నీటిని ఆదా చేయడానికి మరియు సామర్థ్యాన్ని మెరుగుపరచడానికి చినుకు నీటిపారుదలను ఉపయోగించండి.',
                    'ఆవిరి తగ్గించడానికి ఉదయం లేదా సాయంత్రం నీరు పట్టండి.',
                    'మట్టి తేమను నిలుపుకోవడానికి మొక్కల చుట్టూ మల్చ్ చేయండి.',
                    'అధిక నీరు పట్టడాన్ని నివారించడానికి నీరు పట్టే ముందు మట్టి తేమను తనిఖీ చేయండి.'
                ]
            }
        }
    
    def process_message(self, message, language='en'):
        """Process user message and return appropriate response"""
        try:
            # Convert message to lowercase for better matching
            message_lower = message.lower()
            
            # Detect intent based on keywords
            intent = self._detect_intent(message_lower)
            
            # Generate response based on intent and language
            response = self._generate_response(intent, language)
            
            return response
            
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            return self._get_error_response(language)
    
    def _detect_intent(self, message):
        """Detect user intent from message"""
        # Define keyword mappings for different intents
        intent_keywords = {
            'greeting': ['hello', 'hi', 'namaste', 'namaskar', 'namaskaram', 'hey'],
            'soil': ['soil', 'mitti', 'bhumi', 'fertility', 'ph', 'nutrients', 'nitrogen', 'phosphorus'],
            'crop': ['crop', 'fasal', 'panta', 'plant', 'grow', 'cultivation', 'recommendation'],
            'pest': ['pest', 'disease', 'keet', 'rog', 'insect', 'fungus', 'virus', 'infection'],
            'irrigation': ['water', 'irrigation', 'pani', 'jal', 'neeru', 'watering', 'moisture'],
            'weather': ['weather', 'mausam', 'climate', 'rain', 'temperature', 'humidity'],
            'fertilizer': ['fertilizer', 'khad', 'manure', 'compost', 'npk', 'organic'],
            'price': ['price', 'cost', 'market', 'sell', 'buy', 'rate', 'mandi']
        }
        
        # Check for keyword matches
        for intent, keywords in intent_keywords.items():
            if any(keyword in message for keyword in keywords):
                return intent
        
        # Default intent if no specific match found
        return 'general'
    
    def _generate_response(self, intent, language):
        """Generate response based on intent and language"""
        
        if intent == 'greeting':
            return random.choice(self.knowledge_base['greetings'][language])
        
        elif intent == 'soil':
            return random.choice(self.knowledge_base['soil_care'][language])
        
        elif intent == 'pest':
            return random.choice(self.knowledge_base['pest_control'][language])
        
        elif intent == 'irrigation':
            return random.choice(self.knowledge_base['irrigation'][language])
        
        elif intent == 'crop':
            return self._get_crop_advice(language)
        
        elif intent == 'weather':
            return self._get_weather_advice(language)
        
        elif intent == 'fertilizer':
            return self._get_fertilizer_advice(language)
        
        elif intent == 'price':
            return self._get_price_info(language)
        
        else:
            return self._get_general_response(language)
    
    def _get_crop_advice(self, language):
        """Get crop-specific advice"""
        advice = {
            'en': 'Choose crops based on your soil type, climate, and market demand. Consider crop rotation and seasonal variations.',
            'hi': 'अपनी मिट्टी के प्रकार, जलवायु और बाजार की मांग के आधार पर फसलें चुनें। फसल चक्र और मौसमी बदलाव पर विचार करें।',
            'te': 'మీ మట్టి రకం, వాతావరణం మరియు మార్కెట్ డిమాండ్ ఆధారంగా పంటలను ఎంచుకోండి. పంట మార్పిడి మరియు కాలానుగుణ మార్పులను పరిగణించండి.'
        }
        return advice[language]
    
    def _get_weather_advice(self, language):
        """Get weather-related advice"""
        advice = {
            'en': 'Monitor weather forecasts regularly. Plan irrigation and pest control based on weather conditions.',
            'hi': 'मौसम पूर्वानुमान की नियमित निगरानी करें। मौसम की स्थिति के आधार पर सिंचाई और कीट नियंत्रण की योजना बनाएं।',
            'te': 'వాతావరణ సూచనలను క్రమం తప్పకుండా పర్యవేక్షించండి. వాతావరణ పరిస్థితుల ఆధారంగా నీటిపారుదల మరియు కీటకాల నియంత్రణను ప్లాన్ చేయండి.'
        }
        return advice[language]
    
    def _get_fertilizer_advice(self, language):
        """Get fertilizer advice"""
        advice = {
            'en': 'Use balanced NPK fertilizers. Organic compost is always beneficial. Avoid over-fertilization.',
            'hi': 'संतुलित एनपीके उर्वरकों का उपयोग करें। जैविक खाद हमेशा फायदेमंद होती है। अधिक उर्वरक से बचें।',
            'te': 'సమతుల్య NPK ఎరువులను ఉపయోగించండి. సేంద్రీయ కంపోస్ట్ ఎల్లప్పుడూ ప్రయోజనకరం. అధిక ఎరువులను నివారించండి.'
        }
        return advice[language]
    
    def _get_price_info(self, language):
        """Get price information advice"""
        advice = {
            'en': 'Check local mandi prices regularly. Consider storage options for better pricing. Plan harvest timing.',
            'hi': 'स्थानीय मंडी की कीमतों की नियमित जांच करें। बेहतर मूल्य के लिए भंडारण विकल्पों पर विचार करें। फसल के समय की योजना बनाएं।',
            'te': 'స్థానిక మండి ధరలను క్రమం తప్పకుండా తనిఖీ చేయండి. మెరుగైన ధరల కోసం నిల్వ ఎంపికలను పరిగణించండి. కోత సమయాన్ని ప్లాన్ చేయండి.'
        }
        return advice[language]
    
    def _get_general_response(self, language):
        """Get general response for unmatched queries"""
        responses = {
            'en': 'I can help you with soil care, crop suggestions, pest control, irrigation, and farming advice. What would you like to know?',
            'hi': 'मैं मिट्टी की देखभाल, फसल सुझाव, कीट नियंत्रण, सिंचाई और कृषि सलाह में आपकी मदद कर सकता हूं। आप क्या जानना चाहते हैं?',
            'te': 'నేను మట్టి సంరక్షణ, పంట సూచనలు, కీటకాల నియంత్రణ, నీటిపారుదల మరియు వ్యవసాయ సలహాలతో మీకు సహాయం చేయగలను. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?'
        }
        return responses[language]
    
    def _get_error_response(self, language):
        """Get error response"""
        responses = {
            'en': 'Sorry, I had trouble understanding your question. Please try again.',
            'hi': 'माफ करें, मुझे आपका प्रश्न समझने में परेशानी हुई। कृपया फिर से कोशिश करें।',
            'te': 'క్షమించండి, మీ ప్రశ్నను అర్థం చేసుకోవడంలో నాకు ఇబ్బంది ఉంది. దయచేసి మళ్ళీ ప్రయత్నించండి.'
        }
        return responses[language]
    
    def text_to_speech(self, text, language='en'):
        """Convert text to speech audio (placeholder implementation)"""
        try:
            # This would integrate with actual TTS service
            # For demo purposes, return a placeholder response
            return {
                'status': 'success',
                'message': f'TTS would generate audio for: "{text}" in {language}',
                'audio_url': None  # Would contain actual audio file URL/data
            }
        except Exception as e:
            logging.error(f"TTS error: {e}")
            return {
                'status': 'error',
                'message': 'Text-to-speech conversion failed'
            }
    
    def speech_to_text(self, audio_data, language='en'):
        """Convert speech audio to text (placeholder implementation)"""
        try:
            # This would integrate with actual STT service
            # For demo purposes, return a placeholder response
            return {
                'status': 'success',
                'text': 'Speech recognition would convert audio to text here',
                'confidence': 0.85
            }
        except Exception as e:
            logging.error(f"STT error: {e}")
            return {
                'status': 'error',
                'text': '',
                'confidence': 0.0
            }
