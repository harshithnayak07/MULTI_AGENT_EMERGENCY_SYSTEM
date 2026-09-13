// Voice Input Module - Web Speech API with Backend Fallback

class VoiceInput {
    constructor() {
        this.recognition = null;
        this.isRecording = false;
        this.transcript = '';
        this.onResult = null;
        this.onError = null;
        this.onStatusChange = null;
        
        this.initializeSpeechRecognition();
    }

    initializeSpeechRecognition() {
        // Check for browser support
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // Configure recognition
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;

            // Event handlers
            this.recognition.onstart = () => {
                this.isRecording = true;
                this.updateStatus('recording', 'Listening...');
            };

            this.recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }

                this.transcript = finalTranscript || interimTranscript;
                this.updateTranscript(this.transcript);

                if (finalTranscript && this.onResult) {
                    this.onResult(finalTranscript);
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isRecording = false;
                this.updateStatus('error', this.getErrorMessage(event.error));
                
                if (this.onError) {
                    this.onError(event.error);
                }
            };

            this.recognition.onend = () => {
                this.isRecording = false;
                this.resetButton();
                if (this.transcript) {
                    this.updateStatus('complete', 'Recording complete');
                } else {
                    this.updateStatus('ready', 'Tap the mic to speak');
                }
            };

            console.log('Web Speech API initialized');
        } else {
            console.warn('Web Speech API not supported in this browser');
            this.updateStatus('unsupported', 'Voice input not supported');
        }
    }

    startRecording() {
        if (!this.recognition) {
            console.error('Speech recognition not available');
            if (this.onError) {
                this.onError('not_supported');
            }
            return false;
        }

        try {
            this.transcript = '';
            this.recognition.start();
            return true;
        } catch (error) {
            console.error('Error starting recording:', error);
            this.updateStatus('error', 'Failed to start recording');
            if (this.onError) {
                this.onError('start_failed');
            }
            return false;
        }
    }

    stopRecording() {
        if (this.recognition && this.isRecording) {
            try {
                this.recognition.stop();
            } catch (error) {
                console.error('Error stopping recording:', error);
            }
        }
    }

    getTranscript() {
        return this.transcript;
    }

    clearTranscript() {
        this.transcript = '';
        this.updateTranscript('');
    }

    resetButton() {
        const voiceButton = document.getElementById('voiceButton');
        if (voiceButton) {
            voiceButton.classList.remove('recording');
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceButton.title = 'Speak your emergency';
        }
    }

    isSupported() {
        return this.recognition !== null;
    }

    isCurrentlyRecording() {
        return this.isRecording;
    }

    getErrorMessage(error) {
        const errorMessages = {
            'no-speech': 'No speech detected. Please try again.',
            'audio-capture': 'Microphone not available.',
            'not-allowed': 'Microphone access denied. Please allow microphone access.',
            'network': 'Network error. Please check your connection.',
            'aborted': 'Recording was aborted.',
            'default': 'An error occurred during voice recognition.'
        };
        return errorMessages[error] || errorMessages['default'];
    }

    updateStatus(status, message) {
        const statusElement = document.getElementById('voiceStatus');
        if (statusElement) {
            const indicator = statusElement.querySelector('.status-dot');
            const text = statusElement.querySelector('.status-text');

            if (indicator) {
                indicator.classList.remove('active', 'complete', 'error');
                switch (status) {
                    case 'recording':
                        indicator.classList.add('active');
                        break;
                    case 'error':
                        indicator.classList.add('error');
                        break;
                    case 'complete':
                        indicator.classList.add('complete');
                        break;
                    default:
                        break;
                }
            }

            if (text) {
                text.textContent = message;
            }
        }

        if (this.onStatusChange) {
            this.onStatusChange(status, message);
        }
    }

    updateTranscript(text) {
        const transcriptElement = document.getElementById('voiceTranscript');
        if (transcriptElement) {
            transcriptElement.textContent = text || '';
        }
    }

    setResultCallback(callback) {
        this.onResult = callback;
    }

    setErrorCallback(callback) {
        this.onError = callback;
    }

    setStatusChangeCallback(callback) {
        this.onStatusChange = callback;
    }
}

// Backend fallback for voice processing
async function processVoiceBackend(audioData = null) {
    try {
        const response = await fetch('/api/voice/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ audio_data: audioData })
        });

        if (!response.ok) {
            throw new Error('Voice processing failed');
        }

        const result = await response.json();
        return result.text;
    } catch (error) {
        console.error('Backend voice processing error:', error);
        throw error;
    }
}

// Initialize voice input when DOM is ready
let voiceInput;

document.addEventListener('DOMContentLoaded', () => {
    voiceInput = new VoiceInput();

    // Set up voice button
    const voiceButton = document.getElementById('voiceButton');
    if (voiceButton) {
        voiceButton.addEventListener('click', () => {
            if (voiceInput.isCurrentlyRecording()) {
                voiceInput.stopRecording();
                voiceButton.classList.remove('recording');
                voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
            } else {
                if (voiceInput.startRecording()) {
                    voiceButton.classList.add('recording');
                    voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
                }
            }
        });
    }

    // Set up result callback to update emergency input
    voiceInput.setResultCallback((transcript) => {
        const emergencyInput = document.getElementById('emergencyInput');
        if (emergencyInput) {
            emergencyInput.value = transcript;
        }
    });

    // Check if voice is supported and update UI accordingly
    if (!voiceInput.isSupported()) {
        const voiceButton = document.getElementById('voiceButton');
        if (voiceButton) {
            voiceButton.disabled = true;
            voiceButton.title = 'Voice input not supported in this browser';
            voiceButton.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        }
    }
});