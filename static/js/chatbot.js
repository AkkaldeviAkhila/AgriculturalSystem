// Chatbot JavaScript for Smart Agriculture System

class AgricultureChatbot {
    constructor() {
        this.isRecording = false;
        this.isSpeaking = false;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.currentLanguage = 'en';
        this.chatHistory = [];
        
        this.initializeChat();
        this.initializeSpeechRecognition();
        this.setupEventListeners();
    }
    
    /**
     * Initialize chat interface
     */
    initializeChat() {
        this.chatContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.languageSelect = document.getElementById('languageSelect');
        this.sendButton = document.getElementById('sendBtn');
        this.micButton = document.getElementById('micBtn');
        this.speakerButton = document.getElementById('speakerBtn');
        
        // Load chat history from localStorage
        this.loadChatHistory();
        
        // Set initial language
        this.currentLanguage = this.languageSelect.value;
    }
    
    /**
     * Initialize speech recognition
     */
    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            
            this.recognition.onstart = () => {
                this.isRecording = true;
                this.updateMicButton();
                this.showVoiceStatus(true);
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.messageInput.value = transcript;
                this.sendMessage();
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showNotification('Speech recognition error. Please try again.', 'error');
                this.isRecording = false;
                this.updateMicButton();
                this.showVoiceStatus(false);
            };
            
            this.recognition.onend = () => {
                this.isRecording = false;
                this.updateMicButton();
                this.showVoiceStatus(false);
            };
        } else {
            console.warn('Speech recognition not supported in this browser');
            this.micButton.disabled = true;
            this.micButton.title = 'Speech recognition not supported';
        }
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Language change
        this.languageSelect.addEventListener('change', (e) => {
            this.currentLanguage = e.target.value;
            this.updateRecognitionLanguage();
        });
        
        // Message input
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Microphone button
        this.micButton.addEventListener('click', () => {
            this.toggleMicrophone();
        });
        
        // Speaker button
        this.speakerButton.addEventListener('click', () => {
            this.toggleSpeaker();
        });
    }
    
    /**
     * Send message to chatbot
     */
    async sendMessage(event = null) {
        if (event) {
            event.preventDefault();
        }
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessageToChat(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    language: this.currentLanguage
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            if (data.status === 'success') {
                // Add bot response to chat
                this.addMessageToChat(data.response, 'bot');
                
                // Speak response if speaker is enabled
                if (this.isSpeaking) {
                    this.speakText(data.response);
                }
            } else {
                this.addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addMessageToChat('Connection error. Please check your internet and try again.', 'bot');
        }
        
        // Save chat history
        this.saveChatHistory();
    }
    
    /**
     * Add message to chat interface
     */
    addMessageToChat(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(message)}</div>
                <div class="message-time">${currentTime}</div>
            </div>
        `;
        
        this.chatContainer.appendChild(messageElement);
        this.scrollToBottom();
        
        // Add to chat history
        this.chatHistory.push({
            message: message,
            sender: sender,
            timestamp: new Date().toISOString(),
            language: this.currentLanguage
        });
        
        // Animate message appearance
        requestAnimationFrame(() => {
            messageElement.classList.add('fade-in');
        });
    }
    
    /**
     * Format message text (add links, emojis, etc.)
     */
    formatMessage(message) {
        // Convert URLs to clickable links
        message = message.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        
        // Add some agriculture-related emojis based on content
        if (message.toLowerCase().includes('rain') || message.toLowerCase().includes('water')) {
            message = '🌧️ ' + message;
        } else if (message.toLowerCase().includes('sun') || message.toLowerCase().includes('temperature')) {
            message = '☀️ ' + message;
        } else if (message.toLowerCase().includes('crop') || message.toLowerCase().includes('plant')) {
            message = '🌱 ' + message;
        } else if (message.toLowerCase().includes('fertilizer') || message.toLowerCase().includes('nutrients')) {
            message = '🧪 ' + message;
        }
        
        return message;
    }
    
    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.className = 'message bot-message typing-indicator';
        typingElement.id = 'typing-indicator';
        
        typingElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        this.chatContainer.appendChild(typingElement);
        this.scrollToBottom();
    }
    
    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
    
    /**
     * Toggle microphone recording
     */
    toggleMicrophone() {
        if (!this.recognition) {
            this.showNotification('Speech recognition not supported', 'error');
            return;
        }
        
        if (this.isRecording) {
            this.recognition.stop();
        } else {
            this.recognition.lang = this.getRecognitionLanguage();
            this.recognition.start();
        }
    }
    
    /**
     * Toggle speaker for text-to-speech
     */
    toggleSpeaker() {
        this.isSpeaking = !this.isSpeaking;
        this.updateSpeakerButton();
        
        if (!this.isSpeaking && this.synthesis.speaking) {
            this.synthesis.cancel();
        }
    }
    
    /**
     * Speak text using text-to-speech
     */
    speakText(text) {
        if (!this.isSpeaking || !('speechSynthesis' in window)) {
            return;
        }
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = this.getTTSLanguage();
        utterance.rate = 0.9;
        utterance.pitch = 1;
        
        utterance.onstart = () => {
            this.speakerButton.classList.add('speaking');
        };
        
        utterance.onend = () => {
            this.speakerButton.classList.remove('speaking');
        };
        
        this.synthesis.speak(utterance);
    }
    
    /**
     * Get recognition language code
     */
    getRecognitionLanguage() {
        const langMap = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'te': 'te-IN'
        };
        return langMap[this.currentLanguage] || 'en-US';
    }
    
    /**
     * Get TTS language code
     */
    getTTSLanguage() {
        const langMap = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'te': 'te-IN'
        };
        return langMap[this.currentLanguage] || 'en-US';
    }
    
    /**
     * Update recognition language
     */
    updateRecognitionLanguage() {
        if (this.recognition) {
            this.recognition.lang = this.getRecognitionLanguage();
        }
    }
    
    /**
     * Update microphone button state
     */
    updateMicButton() {
        const icon = this.micButton.querySelector('i');
        if (this.isRecording) {
            icon.className = 'fas fa-stop';
            this.micButton.classList.add('recording');
        } else {
            icon.className = 'fas fa-microphone';
            this.micButton.classList.remove('recording');
        }
    }
    
    /**
     * Update speaker button state
     */
    updateSpeakerButton() {
        const icon = this.speakerButton.querySelector('i');
        if (this.isSpeaking) {
            icon.className = 'fas fa-volume-up';
            this.speakerButton.classList.add('active');
        } else {
            icon.className = 'fas fa-volume-mute';
            this.speakerButton.classList.remove('active');
        }
    }
    
    /**
     * Show voice status
     */
    showVoiceStatus(show) {
        const voiceStatus = document.getElementById('voiceStatus');
        if (voiceStatus) {
            voiceStatus.style.display = show ? 'block' : 'none';
        }
    }
    
    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        if (window.AgriUtils && window.AgriUtils.showNotification) {
            window.AgriUtils.showNotification(message, type);
        } else {
            alert(message);
        }
    }
    
    /**
     * Save chat history to localStorage
     */
    saveChatHistory() {
        try {
            localStorage.setItem('agri_chat_history', JSON.stringify(this.chatHistory));
        } catch (error) {
            console.warn('Could not save chat history:', error);
        }
    }
    
    /**
     * Load chat history from localStorage
     */
    loadChatHistory() {
        try {
            const saved = localStorage.getItem('agri_chat_history');
            if (saved) {
                this.chatHistory = JSON.parse(saved);
                // Optionally restore recent messages to chat interface
                // this.restoreRecentMessages();
            }
        } catch (error) {
            console.warn('Could not load chat history:', error);
            this.chatHistory = [];
        }
    }
    
    /**
     * Clear chat history
     */
    clearChat() {
        if (confirm('Are you sure you want to clear the chat history?')) {
            this.chatContainer.innerHTML = `
                <div class="message bot-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text">
                            Chat cleared! How can I help you with your farming questions?
                        </div>
                        <div class="message-time">Just now</div>
                    </div>
                </div>
            `;
            this.chatHistory = [];
            this.saveChatHistory();
        }
    }
    
    /**
     * Export chat history
     */
    exportChat() {
        if (this.chatHistory.length === 0) {
            this.showNotification('No chat history to export', 'warning');
            return;
        }
        
        const chatData = this.chatHistory.map(msg => 
            `[${new Date(msg.timestamp).toLocaleString()}] ${msg.sender}: ${msg.message}`
        ).join('\n');
        
        const blob = new Blob([chatData], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `agri-chat-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Chat history exported successfully', 'success');
    }
    
    /**
     * Share chat session
     */
    shareChat() {
        const shareData = {
            title: 'Smart Agriculture Chat Session',
            text: 'Check out my conversation with the AI agriculture assistant!',
            url: window.location.href
        };
        
        if (navigator.share) {
            navigator.share(shareData);
        } else {
            // Fallback - copy URL to clipboard
            if (window.AgriUtils && window.AgriUtils.copyToClipboard) {
                window.AgriUtils.copyToClipboard(window.location.href);
            } else {
                this.showNotification('Share feature not supported', 'warning');
            }
        }
    }
}

// Quick question functionality
function askQuestion(question) {
    const messageInput = document.getElementById('messageInput');
    if (messageInput && window.chatbot) {
        messageInput.value = question;
        window.chatbot.sendMessage();
    }
}

// Set language functionality
function setLanguage(lang) {
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect && window.chatbot) {
        languageSelect.value = lang;
        window.chatbot.currentLanguage = lang;
        window.chatbot.updateRecognitionLanguage();
    }
}

// Global functions for template access
function clearChat() {
    if (window.chatbot) {
        window.chatbot.clearChat();
    }
}

function exportChat() {
    if (window.chatbot) {
        window.chatbot.exportChat();
    }
}

function shareChat() {
    if (window.chatbot) {
        window.chatbot.shareChat();
    }
}

function toggleMicrophone() {
    if (window.chatbot) {
        window.chatbot.toggleMicrophone();
    }
}

function toggleSpeaker() {
    if (window.chatbot) {
        window.chatbot.toggleSpeaker();
    }
}

function sendMessage(event) {
    if (window.chatbot) {
        window.chatbot.sendMessage(event);
    }
}

// Initialize chatbot
function initializeChatbot() {
    window.chatbot = new AgricultureChatbot();
    console.log('Agriculture Chatbot initialized successfully');
}

// CSS for chatbot (add to head if not in separate CSS file)
const chatbotStyles = `
<style>
.chat-container {
    height: 500px;
    display: flex;
    flex-direction: column;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    background-color: var(--bs-light);
}

.message {
    display: flex;
    margin-bottom: 1rem;
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.3s ease;
}

.message.fade-in {
    opacity: 1;
    transform: translateY(0);
}

.message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.75rem;
    flex-shrink: 0;
}

.bot-message .message-avatar {
    background-color: var(--bs-primary);
    color: white;
}

.user-message {
    flex-direction: row-reverse;
}

.user-message .message-avatar {
    background-color: var(--bs-success);
    color: white;
    margin-right: 0;
    margin-left: 0.75rem;
}

.message-content {
    flex: 1;
    max-width: 70%;
}

.user-message .message-content {
    text-align: right;
}

.message-text {
    background-color: white;
    padding: 0.75rem 1rem;
    border-radius: 18px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    word-wrap: break-word;
}

.user-message .message-text {
    background-color: var(--bs-primary);
    color: white;
}

.message-time {
    font-size: 0.75rem;
    color: var(--bs-muted);
    margin-top: 0.25rem;
    padding: 0 1rem;
}

.typing-indicator .typing-dots {
    display: flex;
    align-items: center;
    padding: 1rem;
    background-color: white;
    border-radius: 18px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.typing-dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--bs-secondary);
    margin: 0 2px;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {
    0%, 60%, 100% {
        transform: scale(0.8);
        opacity: 0.5;
    }
    30% {
        transform: scale(1);
        opacity: 1;
    }
}

.language-option,
.quick-question,
.feature-item {
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.language-option:hover,
.quick-question:hover {
    background-color: var(--bs-light);
}

.quick-question {
    border-left: 3px solid var(--bs-primary);
}

.feature-item {
    border-left: 3px solid var(--bs-success);
}

.btn.recording {
    background-color: var(--bs-danger) !important;
    color: white !important;
}

.btn.active {
    background-color: var(--bs-success) !important;
    color: white !important;
}

.btn.speaking {
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
}

@media (max-width: 768px) {
    .chat-container {
        height: 400px;
    }
    
    .message-content {
        max-width: 85%;
    }
}
</style>
`;

// Inject styles if not already present
if (!document.querySelector('#chatbot-styles')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'chatbot-styles';
    styleElement.innerHTML = chatbotStyles;
    document.head.appendChild(styleElement);
}

console.log('Chatbot JavaScript loaded successfully');
