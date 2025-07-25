// static/js/chatbot.js

class AgricultureChatbot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.languageSelect = document.getElementById('languageSelect');
        this.micBtn = document.getElementById('micBtn');
        this.speakerBtn = document.getElementById('speakerBtn');
        this.voiceStatus = document.getElementById('voiceStatus');
        this.audioPlayer = document.getElementById('audioPlayer');

        this.speakerEnabled = true;
        this.listening = false;
        this.recognition = null;
        this.lastBotMessage = "";

        this.initSpeechRecognition();
    }

    initSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn("Speech recognition not supported in this browser.");
            return;
        }
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 1;

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log('Voice Input Captured:', transcript);
            this.messageInput.value = transcript;
            this.sendMessage();
        };

        this.recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            alert(`Speech recognition error: ${event.error}`);
        };

        this.recognition.onend = () => {
            this.listening = false;
            if (this.voiceStatus) this.voiceStatus.style.display = 'none';
            if (this.micBtn) {
                this.micBtn.classList.remove('btn-danger');
                this.micBtn.classList.add('btn-outline-light');
            }
            console.log('Speech recognition ended.');
        };
    }

    toggleMicrophone() {
        if (!this.recognition) {
            alert("Speech recognition not supported in your browser.");
            return;
        }

        if (this.listening) {
            this.recognition.stop();
        } else {
            const lang = this.languageSelect.value;
            this.recognition.lang = lang === 'hi' ? 'hi-IN' : lang === 'te' ? 'te-IN' : 'en-US';
            try {
                this.recognition.start();
                this.listening = true;
                if (this.voiceStatus) this.voiceStatus.style.display = 'block';
                if (this.micBtn) {
                    this.micBtn.classList.add('btn-danger');
                    this.micBtn.classList.remove('btn-outline-light');
                }
                console.log('Speech recognition started...');
            } catch (error) {
                console.error('Speech recognition could not start:', error);
                alert('Speech recognition could not start. Try again.');
            }
        }
    }

    toggleSpeaker() {
        const icon = this.speakerBtn.querySelector('i');
        this.speakerEnabled = !this.speakerEnabled;
        if (this.speakerEnabled) {
            icon.classList.remove('fa-volume-mute');
            icon.classList.add('fa-volume-up');
            if (this.lastBotMessage) {
                this.speakText(this.lastBotMessage, this.languageSelect.value);
            }
        } else {
            icon.classList.remove('fa-volume-up');
            icon.classList.add('fa-volume-mute');
            if (!this.audioPlayer.paused) this.audioPlayer.pause();
            window.speechSynthesis.cancel();
        }
    }

    appendMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender === 'bot' ? 'bot-message' : 'user-message'}`;
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${sender === 'bot' ? 'fa-robot' : 'fa-user'}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${message}</div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>`;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    async sendMessage(event) {
        if (event) event.preventDefault();
        const message = this.messageInput.value.trim();
        if (!message) return;
        const language = this.languageSelect.value;

        this.appendMessage(message, 'user');
        this.messageInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, language })
            });
            const data = await response.json();
            if (data.response) {
                this.lastBotMessage = data.response;
                this.appendMessage(data.response, 'bot');
                if (this.speakerEnabled) {
                    this.speakText(data.response, language);
                }
            } else {
                this.appendMessage('No response from server.', 'bot');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.appendMessage('Error connecting to server.', 'bot');
        }
    }

    speakText(text, language) {
        this.lastBotMessage = text;
        if (language === 'te') {
            fetch('/api/text-to-speech', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, language })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.audio_url) {
                        console.log('Playing Telugu TTS:', data.audio_url);
                        this.audioPlayer.src = data.audio_url;
                        this.audioPlayer.load();
                        this.audioPlayer.play().catch(err => {
                            console.error('Audio playback error:', err);
                            alert('Click on the page or interact with the site to enable audio playback due to browser restrictions.');
                        });
                    } else {
                        console.error('No audio_url returned from Flask.');
                    }
                })
                .catch(err => console.error('Fetch error for Telugu TTS:', err));
        } else {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = language === 'hi' ? 'hi-IN' : 'en-US';
            utterance.rate = 1; // Adjust speed if needed
            window.speechSynthesis.speak(utterance);
            console.log('Speaking via browser TTS...');
        }
    }
}

let chatbot;
function initializeChatbot() {
    chatbot = new AgricultureChatbot();
    window.sendMessage = (event) => chatbot.sendMessage(event);
    window.toggleMicrophone = () => chatbot.toggleMicrophone();
    window.toggleSpeaker = () => chatbot.toggleSpeaker();
    window.setLanguage = (lang) => { chatbot.languageSelect.value = lang; };
    window.askQuestion = (question) => {
        chatbot.messageInput.value = question;
        chatbot.sendMessage();
    };
    window.clearChat = () => {
        if (confirm("Are you sure you want to clear the chat?")) {
            chatbot.chatMessages.innerHTML = "";
            chatbot.lastBotMessage = "";
        }
    };
    window.exportChat = () => {
        let chatText = "";
        document.querySelectorAll("#chatMessages .message").forEach(msg => {
            const sender = msg.classList.contains("bot-message") ? "AgriBot" : "You";
            const text = msg.querySelector(".message-text").innerText;
            const time = msg.querySelector(".message-time").innerText;
            chatText += `[${time}] ${sender}: ${text}\n`;
        });
        const blob = new Blob([chatText], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "agriculture_chat.txt";
        a.click();
        URL.revokeObjectURL(url);
    };
}
