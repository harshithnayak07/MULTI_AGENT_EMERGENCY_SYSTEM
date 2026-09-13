// Main Application Logic

class EmergencyApp {
    constructor() {
        this.websocket = null;
        this.isConnected = false;
        this.streamedAdvice = '';
        
        this.initializeEventListeners();
        this.initializeWebSocket();
    }

    initializeEventListeners() {
        // Analyze button
        const analyzeButton = document.getElementById('analyzeButton');
        if (analyzeButton) {
            analyzeButton.addEventListener('click', () => this.analyzeEmergency());
        }

        // Clear button
        const clearButton = document.getElementById('clearButton');
        if (clearButton) {
            clearButton.addEventListener('click', () => this.clearForm());
        }

        // Retry button (in error section)
        const retryButton = document.getElementById('retryButton');
        if (retryButton) {
            retryButton.addEventListener('click', () => this.retryAnalysis());
        }

        // New analysis button (in results section)
        const newAnalysisButton = document.getElementById('newAnalysisButton');
        if (newAnalysisButton) {
            newAnalysisButton.addEventListener('click', () => this.startNewAnalysis());
        }
    }

    startNewAnalysis() {
        this.clearForm();
        const textarea = document.getElementById('emergencyInput');
        if (textarea) {
            textarea.focus();
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async initializeWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/real-time`;
            
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
            };

            this.websocket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
            };

            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                // Attempt to reconnect after 3 seconds
                setTimeout(() => this.initializeWebSocket(), 3000);
            };

        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            // Fallback to REST API
            this.isConnected = false;
        }
    }

    handleWebSocketMessage(message) {
        switch (message.type) {
            case 'connected':
                console.log('WebSocket connection confirmed');
                break;
                
            case 'status':
                this.handleStatusUpdate(message.data);
                break;
                
            case 'agent_update':
                this.handleAgentUpdate(message.data);
                break;
                
            case 'stream_chunk':
                this.handleStreamChunk(message.data);
                break;
                
            case 'complete':
                this.handleAnalysisComplete(message.data);
                break;
                
            case 'error':
                this.handleError(message.data.error);
                break;
                
            default:
                console.log('Unknown message type:', message.type);
        }
    }

    handleStatusUpdate(data) {
        console.log('Status update:', data);
    }

    handleAgentUpdate(data) {
        const agentIdMap = {
            'location_agent': 'locationAgent',
            'hospital_agent': 'hospitalAgent',
            'weather_agent': 'weatherAgent',
            'llm_agent': 'llmAgent'
        };
        const agentId = agentIdMap[data.agent];
        const agentElement = agentId ? document.getElementById(agentId) : null;
        if (agentElement) {
            const statusBadge = agentElement.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = 'status-badge';
                
                switch (data.status) {
                    case 'processing':
                        statusBadge.classList.add('processing');
                        statusBadge.textContent = 'Processing';
                        break;
                    case 'complete':
                        statusBadge.classList.add('complete');
                        statusBadge.textContent = 'Complete';
                        break;
                    default:
                        statusBadge.classList.add('pending');
                        statusBadge.textContent = 'Pending';
                }
            }
        }
    }

    handleStreamChunk(data) {
        if (data.chunk) {
            this.streamedAdvice += data.chunk;
            this.updateAdviceDisplay(this.streamedAdvice);
            if (!data.is_final) {
                this.appendCaret();
            }
        }
        
        if (data.is_final) {
            this.removeCaret();
            console.log('Streaming complete');
        }
    }

    handleAnalysisComplete(data) {
        this.hideLoading();
        this.showResults();
        
        // Update UI with results
        this.updateLocationResult(data.location);
        this.updateWeatherResult(data.temperature);
        this.updateHospitalList(data.hospitals_detail || data.hospitals);
        this.updateAdviceDisplay(data.advice);
        
        // Update map — prefer structured hospital data with real coordinates
        if (typeof updateMapWithEmergencyData === 'function') {
            updateMapWithEmergencyData(
                data.location,
                data.coordinates,
                data.hospitals_detail || data.hospitals
            );
        }

        // Ensure Leaflet recalculates its container size now it's visible
        if (emergencyMap) emergencyMap.invalidateSize();
    }

    handleError(error) {
        console.error('Analysis error:', error);
        this.hideLoading();
        this.showError(error);
    }

    async analyzeEmergency() {
        // Stop voice recording if it's active
        this.stopVoiceRecording();

        const userInput = this.getUserInput();
        
        if (!userInput || userInput.trim() === '') {
            alert('Please enter an emergency description');
            return;
        }

        this.showLoading();
        this.hideResults();
        this.hideError();
        
        // Reset agent statuses
        this.resetAgentStatuses();
        this.streamedAdvice = '';

        if (this.isConnected && this.websocket) {
            // Use WebSocket for real-time updates
            this.websocket.send(JSON.stringify({
                type: 'emergency_analysis',
                user_input: userInput
            }));
        } else {
            // Fallback to REST API
            await this.analyzeViaREST(userInput);
        }
    }

    async analyzeViaREST(userInput) {
        try {
            const response = await fetch('/api/emergency/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_input: userInput })
            });

            if (!response.ok) {
                throw new Error('Analysis request failed');
            }

            const result = await response.json();
            
            if (result.success) {
                this.handleAnalysisComplete(result);
            } else {
                this.handleError(result.message || 'Analysis failed');
            }

        } catch (error) {
            console.error('REST API error:', error);
            this.handleError('Failed to analyze emergency. Please try again.');
        }
    }

    getUserInput() {
        const textarea = document.getElementById('emergencyInput');
        const typed = textarea ? textarea.value : '';
        if (typed && typed.trim() !== '') {
            return typed;
        }
        if (typeof voiceInput !== 'undefined' && voiceInput) {
            return voiceInput.getTranscript();
        }
        return '';
    }

    stopVoiceRecording() {
        if (typeof voiceInput !== 'undefined' && voiceInput && voiceInput.isCurrentlyRecording()) {
            voiceInput.stopRecording();
            if (typeof voiceInput.resetButton === 'function') {
                voiceInput.resetButton();
            } else {
                const voiceButton = document.getElementById('voiceButton');
                if (voiceButton) {
                    voiceButton.classList.remove('recording');
                    voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
                    voiceButton.title = 'Speak your emergency';
                }
            }
        }
    }

    showLoading() {
        document.getElementById('loadingSection').classList.remove('hidden');
        document.getElementById('analyzeButton').disabled = true;
    }

    hideLoading() {
        document.getElementById('loadingSection').classList.add('hidden');
        document.getElementById('analyzeButton').disabled = false;
    }

    showResults() {
        document.getElementById('resultsSection').classList.remove('hidden');
    }

    hideResults() {
        document.getElementById('resultsSection').classList.add('hidden');
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        if (errorMessage) {
            errorMessage.textContent = message;
        }
        
        errorSection.classList.remove('hidden');
    }

    hideError() {
        document.getElementById('errorSection').classList.add('hidden');
    }

    resetAgentStatuses() {
        const agents = ['locationAgent', 'hospitalAgent', 'weatherAgent', 'llmAgent'];
        agents.forEach(agentId => {
            const agentElement = document.getElementById(agentId);
            if (agentElement) {
                const statusBadge = agentElement.querySelector('.status-badge');
                if (statusBadge) {
                    statusBadge.className = 'status-badge pending';
                    statusBadge.textContent = 'Pending';
                }
            }
        });
    }

    updateLocationResult(location) {
        const element = document.getElementById('locationResult');
        if (element) {
            element.textContent = location;
        }
    }

    updateWeatherResult(temperature) {
        const element = document.getElementById('weatherResult');
        if (element) {
            element.textContent = `${temperature}°C`;
        }
    }

    updateHospitalList(hospitals) {
        const listElement = document.getElementById('hospitalList');
        if (!listElement) return;

        listElement.innerHTML = '';

        if (hospitals && hospitals.length > 0) {
            hospitals.forEach((hospital, index) => {
                const li = document.createElement('li');
                const name = hospital.name || `Hospital ${index + 1}`;
                const address = hospital.address || '';
                // Show name on first line, full address on second line
                li.innerHTML = `
                    <i class="fas fa-hospital"></i>
                    <span><strong>${name}</strong>${address ? '<br>' + address : ''}</span>
                `;
                listElement.appendChild(li);
            });
        } else {
            listElement.innerHTML = '<li class="placeholder">No hospitals found</li>';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    renderAdviceMarkdown(text) {
        if (!text) return '';
        const escaped = this.escapeHtml(text.trim());
        const lines = escaped.split('\n');
        let out = '';
        let i = 0;

        const inline = (s) => s
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');

        while (i < lines.length) {
            const line = lines[i].trim();

            if (!line) {
                i++;
                continue;
            }

            if (/^(-{3,}|\*{3,}|_{3,})$/.test(line)) {
                out += '<hr>';
                i++;
                continue;
            }

            const heading = line.match(/^(#{1,4})\s+(.+)$/);
            if (heading) {
                const level = Math.min(heading[1].length, 4);
                out += `<h${level}>${inline(heading[2])}</h${level}>`;
                i++;
                continue;
            }

            if (line.startsWith('|') && line.includes('|', 1)) {
                const tableLines = [];
                while (i < lines.length && lines[i].trim().startsWith('|')) {
                    tableLines.push(lines[i].trim());
                    i++;
                }
                const rows = tableLines.map((r) =>
                    r.replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => inline(c.trim()))
                );
                let bodyStart = 1;
                if (rows[1] && rows[1].length > 0 && rows[1].every((c) => /^:?-+:?$/.test(c.replace(/\s/g, '')))) {
                    bodyStart = 2;
                }
                out += '<table>';
                out += `<thead><tr>${rows[0].map((c) => `<th>${c}</th>`).join('')}</tr></thead><tbody>`;
                for (let r = bodyStart; r < rows.length; r++) {
                    out += `<tr>${rows[r].map((c) => `<td>${c}</td>`).join('')}</tr>`;
                }
                out += '</tbody></table>';
                continue;
            }

            const listItem = line.match(/^[-*]\s+(.+)$/);
            if (listItem) {
                out += '<ul>';
                while (i < lines.length) {
                    const m = lines[i].trim().match(/^[-*]\s+(.+)$/);
                    if (!m) break;
                    out += `<li>${inline(m[1])}</li>`;
                    i++;
                }
                out += '</ul>';
                continue;
            }

            const numberedItem = line.match(/^(\d+)[.)]\s+(.+)$/);
            if (numberedItem) {
                out += '<ol>';
                while (i < lines.length) {
                    const m = lines[i].trim().match(/^\d+[.)]\s+(.+)$/);
                    if (!m) break;
                    out += `<li>${inline(m[1])}</li>`;
                    i++;
                }
                out += '</ol>';
                continue;
            }

            const quote = line.match(/^(?:&gt;|>)\s?(.+)$/);
            if (quote) {
                out += `<blockquote>${inline(quote[1])}</blockquote>`;
                i++;
                continue;
            }

            // Paragraph — consume until the next block-level token
            const para = [];
            while (i < lines.length) {
                const t = lines[i].trim();
                if (!t) break;
                if (t.startsWith('|') && t.includes('|', 1)) break;
                if (/^(#{1,4}\s|[-*]\s|\d+[.)]\s|(?:&gt;|>))/.test(t)) break;
                if (/^(-{3,}|\*{3,}|_{3,})$/.test(t)) break;
                para.push(t);
                i++;
            }
            const body = para.map((p) => inline(p)).join('<br>');
            if (body) out += `<p>${body}</p>`;
        }
        return out;
    }

    appendCaret() {
        const element = document.getElementById('adviceResult');
        if (element && !element.querySelector('.stream-caret')) {
            const caret = document.createElement('span');
            caret.className = 'stream-caret';
            element.appendChild(caret);
        }
    }

    removeCaret() {
        const element = document.getElementById('adviceResult');
        if (element) {
            const caret = element.querySelector('.stream-caret');
            if (caret) caret.remove();
        }
    }

    updateAdviceDisplay(advice) {
        const element = document.getElementById('adviceResult');
        if (element) {
            if (advice) {
                // Render streaming/full advice with lightweight markdown support
                element.innerHTML = this.renderAdviceMarkdown(advice);
            } else {
                element.innerHTML = '<div class="placeholder">AI advice will appear here</div>';
            }
        }
    }

    clearForm() {
        // Clear text input
        const textarea = document.getElementById('emergencyInput');
        if (textarea) {
            textarea.value = '';
        }

        // Clear voice input
        if (typeof voiceInput !== 'undefined' && voiceInput) {
            voiceInput.clearTranscript();
        }

        // Hide results and errors
        this.hideResults();
        this.hideError();

        // Clear map
        if (typeof emergencyMap !== 'undefined' && emergencyMap) {
            emergencyMap.clearAllMarkers();
        }
    }

    retryAnalysis() {
        this.hideError();
        this.analyzeEmergency();
    }
}

// Initialize app when DOM is ready
let emergencyApp;

document.addEventListener('DOMContentLoaded', () => {
    emergencyApp = new EmergencyApp();
    console.log('Emergency application initialized');
});

// Handle page visibility changes for WebSocket
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && emergencyApp) {
        // Reconnect WebSocket if needed
        if (!emergencyApp.isConnected) {
            emergencyApp.initializeWebSocket();
        }
    }
});