// Healthcare Feedback System - Dashboard with Charts
// Natural two-way conversation with AI assistant + visual analysis

class ConversationalFeedbackApp {
    constructor() {
        this.messages = [];
        this.isActive = false;
        this.sessionId = null;
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isRecording = false;
        this.charts = {};

        this.init();
    }

    init() {
        this.setupSpeechRecognition();
        this.setupEventListeners();
        this.updateScreen('welcome');
    }

    setupSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('message-input').value = transcript;
                this.stopRecording();
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showRecordingStatus('Error: ' + event.error, 'error');
                this.stopRecording();
            };

            this.recognition.onend = () => {
                if (this.isRecording) {
                    this.stopRecording();
                }
            };
        }
    }

    setupEventListeners() {
        document.getElementById('start-conversation-btn').addEventListener('click', () => {
            this.startConversation();
        });

        document.getElementById('end-conversation-btn').addEventListener('click', () => {
            this.endConversation();
        });

        document.getElementById('send-btn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('record-btn').addEventListener('click', () => {
            this.startRecording();
        });

        document.getElementById('stop-record-btn').addEventListener('click', () => {
            this.stopRecording();
        });

        document.getElementById('message-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        document.getElementById('new-feedback-btn').addEventListener('click', () => {
            this.reset();
        });

        document.getElementById('view-history-btn').addEventListener('click', () => {
            this.loadHistory();
        });

        document.getElementById('back-to-results-btn').addEventListener('click', () => {
            this.updateScreen('results');
        });
    }

    async startConversation() {
        try {
            const response = await fetch('/api/conversation/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (data.success) {
                this.isActive = true;
                this.sessionId = data.session_id;
                this.messages = [];
                this.updateScreen('conversation');
                this.addMessage('assistant', data.message);
                this.speakMessage(data.message);
            }
        } catch (error) {
            console.error('Error starting conversation:', error);
            alert('Error starting conversation. Please try again.');
        }
    }

    async sendMessage() {
        const inputEl = document.getElementById('message-input');
        const message = inputEl.value.trim();

        if (!message) return;
        if (!this.isActive) {
            alert('Please start a conversation first.');
            return;
        }

        this.addMessage('user', message);
        inputEl.value = '';
        this.stopRecording();

        try {
            const response = await fetch('/api/conversation/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.addMessage('assistant', data.message);
                this.speakMessage(data.message);

                if (data.should_analyze || !data.is_active) {
                    this.isActive = false;
                    if (data.transcript) {
                        this.transcript = data.transcript;
                    }
                    await this.analyzeFeedback();
                }
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Error sending message. Please try again.');
        }
    }

    async endConversation() {
        if (!this.isActive) return;

        try {
            const response = await fetch('/api/conversation/end', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: this.sessionId })
            });

            const data = await response.json();

            if (data.success) {
                this.isActive = false;
                if (data.message) {
                    this.addMessage('assistant', data.message);
                }
                this.transcript = data.transcript || this.getConversationTranscript();
                await this.analyzeFeedback();
            }
        } catch (error) {
            console.error('Error ending conversation:', error);
            this.isActive = false;
            await this.analyzeFeedback();
        }
    }

    async analyzeFeedback() {
        this.updateScreen('analysis');

        try {
            const response = await fetch('/api/conversation/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transcript: this.transcript || this.getConversationTranscript(),
                    session_id: this.sessionId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.renderDashboard(data.feedback);
                this.updateScreen('results');
            } else {
                alert('Error analyzing feedback: ' + (data.error || 'Unknown error'));
                this.updateScreen('conversation');
            }
        } catch (error) {
            console.error('Error analyzing feedback:', error);
            alert('Error analyzing feedback. Please try again.');
            this.updateScreen('conversation');
        }
    }

    renderDashboard(feedback) {
        // Destroy existing charts
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};

        // Overall Score
        const scoreEl = document.getElementById('overall-score');
        const score = feedback.satisfaction_score || 3;
        scoreEl.innerHTML = `
            <div class="score-circle score-${this.getScoreClass(score)}">
                <span class="score-number">${score}</span>
                <span class="score-label">/5</span>
            </div>
            <p class="score-text">Overall Satisfaction</p>
        `;

        // 1. Radar Chart - Patient Experience
        this.renderRadarChart(feedback.radar_metrics);

        // 2. Stacked Bar - Confidence in Treatment
        this.renderConfidenceChart(feedback.confidence_in_treatment);

        // 3. Line/Bar Chart - Duration & Staff Behavior
        this.renderMetricsChart(feedback.duration_satisfaction, feedback.staff_behavior);

        // 4. Summary Bullets
        this.renderSummaryBullets(feedback.summary_bullets);
    }

    getScoreClass(score) {
        if (score >= 4) return 'good';
        if (score >= 3) return 'neutral';
        return 'bad';
    }

    renderRadarChart(radarMetrics) {
        const ctx = document.getElementById('radar-chart').getContext('2d');

        const labels = [
            'Felt Heard',
            'Concerns Addressed',
            'Clear Communication',
            'Respect Shown',
            'Time Given'
        ];

        const data = [
            radarMetrics?.felt_heard || 3,
            radarMetrics?.concerns_addressed || 3,
            radarMetrics?.clear_communication || 3,
            radarMetrics?.respect_shown || 3,
            radarMetrics?.time_given || 3
        ];

        this.charts.radar = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Patient Experience',
                    data: data,
                    backgroundColor: 'rgba(102, 126, 234, 0.3)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 5,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    renderConfidenceChart(confidence) {
        const ctx = document.getElementById('confidence-chart').getContext('2d');

        let yesVal = 0, noVal = 0, partialVal = 0;

        if (confidence === 'yes') {
            yesVal = 100;
        } else if (confidence === 'no') {
            noVal = 100;
        } else {
            partialVal = 100;
        }

        this.charts.confidence = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Treatment Confidence'],
                datasets: [
                    {
                        label: 'Yes',
                        data: [yesVal],
                        backgroundColor: 'rgba(76, 175, 80, 0.8)',
                        borderColor: 'rgba(76, 175, 80, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Partial',
                        data: [partialVal],
                        backgroundColor: 'rgba(255, 193, 7, 0.8)',
                        borderColor: 'rgba(255, 193, 7, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'No',
                        data: [noVal],
                        backgroundColor: 'rgba(244, 67, 54, 0.8)',
                        borderColor: 'rgba(244, 67, 54, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                indexAxis: 'y',
                scales: {
                    x: {
                        stacked: true,
                        max: 100,
                        ticks: {
                            callback: value => value + '%'
                        }
                    },
                    y: {
                        stacked: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    renderMetricsChart(durationSatisfaction, staffBehavior) {
        const ctx = document.getElementById('metrics-chart').getContext('2d');

        this.charts.metrics = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Consultation Duration', 'Staff Behavior'],
                datasets: [{
                    label: 'Satisfaction Rating',
                    data: [durationSatisfaction || 3, staffBehavior || 3],
                    backgroundColor: 'rgba(118, 75, 162, 0.3)',
                    borderColor: 'rgba(118, 75, 162, 1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(118, 75, 162, 1)',
                    pointRadius: 8,
                    pointHoverRadius: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 5,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Rating (1-5)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    renderSummaryBullets(bullets) {
        const bulletsEl = document.getElementById('summary-bullets');

        if (!bullets || bullets.length === 0) {
            bulletsEl.innerHTML = '<li>No specific feedback provided.</li>';
            return;
        }

        bulletsEl.innerHTML = bullets.map(bullet => `<li>${bullet}</li>`).join('');
    }

    addMessage(role, content) {
        this.messages.push({ role, content, timestamp: new Date() });

        const chatContainer = document.getElementById('chat-container');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();

        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        chatContainer.appendChild(messageDiv);

        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    getConversationTranscript() {
        let transcript = '';
        this.messages.forEach(msg => {
            const roleLabel = msg.role === 'user' ? 'Patient' : 'Assistant';
            transcript += `${roleLabel}: ${msg.content}\n\n`;
        });
        return transcript;
    }

    speakMessage(message) {
        if (this.synthesis && message) {
            this.synthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(message);
            utterance.rate = 0.9;
            utterance.pitch = 1;
            utterance.volume = 1;
            this.synthesis.speak(utterance);
        }
    }

    startRecording() {
        if (!this.recognition) {
            alert('Speech recognition is not supported in your browser. Please type your message.');
            return;
        }

        if (this.isRecording) return;

        try {
            this.recognition.start();
            this.isRecording = true;
            document.getElementById('record-btn').classList.add('recording');
            document.getElementById('record-btn').style.display = 'none';
            document.getElementById('stop-record-btn').style.display = 'inline-block';
            this.showRecordingStatus('🎤 Listening... Speak now', 'recording');
        } catch (error) {
            console.error('Error starting recognition:', error);
            this.showRecordingStatus('Error starting microphone. Please check permissions.', 'error');
        }
    }

    stopRecording() {
        if (this.recognition && this.isRecording) {
            this.recognition.stop();
        }
        this.isRecording = false;
        document.getElementById('record-btn').classList.remove('recording');
        document.getElementById('record-btn').style.display = 'inline-block';
        document.getElementById('stop-record-btn').style.display = 'none';
        document.getElementById('recording-status').classList.remove('active', 'recording');
    }

    showRecordingStatus(message, type = 'info') {
        const statusEl = document.getElementById('recording-status');
        statusEl.textContent = message;
        statusEl.className = 'recording-status active';
        if (type === 'recording') {
            statusEl.classList.add('recording');
        }
    }

    async loadHistory() {
        try {
            const response = await fetch('/api/feedback-history');
            const data = await response.json();

            if (data.success) {
                this.displayHistory(data.feedback);
                this.updateScreen('history');
            }
        } catch (error) {
            console.error('Error loading history:', error);
            alert('Error loading history.');
        }
    }

    displayHistory(feedbackList) {
        const historyEl = document.getElementById('history-list');

        if (feedbackList.length === 0) {
            historyEl.innerHTML = '<p>No feedback history yet.</p>';
            return;
        }

        let html = '';
        feedbackList.reverse().forEach((item, index) => {
            html += `
                <div class="history-item">
                    <h4>Feedback #${feedbackList.length - index} - ${item.timestamp}</h4>
                    <p class="score-display">Score: ${item.satisfaction_score}/5</p>
                    <p><strong>Summary:</strong> ${item.summary || 'N/A'}</p>
                </div>
            `;
        });

        historyEl.innerHTML = html;
    }

    updateScreen(screenName) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });

        document.getElementById(screenName + '-screen').classList.add('active');
    }

    reset() {
        this.messages = [];
        this.isActive = false;
        this.sessionId = null;
        this.transcript = null;
        document.getElementById('message-input').value = '';
        document.getElementById('chat-container').innerHTML = '';

        // Destroy charts
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};

        this.updateScreen('welcome');
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ConversationalFeedbackApp();
    new ParticleBackground();
    new ParallaxCard();
});

// ... (ParticleBackground class)

// ============================================================================
// 3D PARALLAX CARD EFFECT
// ============================================================================

class ParallaxCard {
    constructor() {
        this.container = document.querySelector('.container');
        if (!this.container) return;

        this.header = document.querySelector('header');
        this.chatContainer = document.querySelector('.chat-container');
        this.inputContainer = document.querySelector('.input-container');

        this.setupEvents();
    }

    setupEvents() {
        this.container.addEventListener('mousemove', (e) => {
            this.update(e);
        });

        this.container.addEventListener('mouseleave', () => {
            this.reset();
        });
    }

    update(e) {
        const { clientX, clientY } = e;
        const rect = this.container.getBoundingClientRect();

        // Calculate center of the card
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        // Calculate rotation based on cursor position relative to card center
        // Reduced tilt sensitivity (higher divisor = less tilt)
        const rotateY = (clientX - centerX) / 60;
        const rotateX = (centerY - clientY) / 60;

        // Apply rotation to container
        this.container.style.transform = `perspective(1000px) rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;

        // Parallax for inner elements (pop out effect)
        if (this.header) this.header.style.transform = `translateZ(30px)`;
        if (this.chatContainer) this.chatContainer.style.transform = `translateZ(20px)`;
    }

    reset() {
        this.container.style.transform = `perspective(1000px) rotateY(0deg) rotateX(0deg)`;
        if (this.header) this.header.style.transform = `translateZ(0px)`;
        if (this.chatContainer) this.chatContainer.style.transform = `translateZ(0px)`;
    }
}

// ============================================================================
// PARTICLE BACKGROUND - Spreading dots effect
// ============================================================================

class ParticleBackground {
    constructor() {
        this.canvas = document.getElementById('particles-canvas');
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouseX = 0;
        this.mouseY = 0;
        this.mouseRadius = 120;

        this.init();
        this.animate();
        this.setupEvents();
    }

    init() {
        this.resize();
        this.createParticles();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        this.particles = [];
        const numberOfParticles = Math.floor((this.canvas.width * this.canvas.height) / 8000);

        for (let i = 0; i < numberOfParticles; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                baseX: 0,
                baseY: 0,
                size: Math.random() * 2 + 1,
                speedX: (Math.random() - 0.5) * 0.3,
                speedY: (Math.random() - 0.5) * 0.3,
                opacity: Math.random() * 0.5 + 0.3
            });
        }

        // Store base positions
        this.particles.forEach(p => {
            p.baseX = p.x;
            p.baseY = p.y;
        });
    }

    setupEvents() {
        window.addEventListener('resize', () => {
            this.resize();
            this.createParticles();
        });

        window.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
        });

        window.addEventListener('mouseout', () => {
            this.mouseX = -1000;
            this.mouseY = -1000;
        });
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.particles.forEach(particle => {
            // Calculate distance from mouse
            const dx = this.mouseX - particle.x;
            const dy = this.mouseY - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            // Spread effect when mouse is near
            if (distance < this.mouseRadius) {
                const force = (this.mouseRadius - distance) / this.mouseRadius;
                const angle = Math.atan2(dy, dx);
                const pushX = Math.cos(angle) * force * 50;
                const pushY = Math.sin(angle) * force * 50;

                particle.x -= pushX * 0.1;
                particle.y -= pushY * 0.1;
            } else {
                // Return to base position slowly
                particle.x += (particle.baseX - particle.x) * 0.02;
                particle.y += (particle.baseY - particle.y) * 0.02;
            }

            // Slight drift movement
            particle.baseX += particle.speedX;
            particle.baseY += particle.speedY;

            // Wrap around screen
            if (particle.baseX < 0) particle.baseX = this.canvas.width;
            if (particle.baseX > this.canvas.width) particle.baseX = 0;
            if (particle.baseY < 0) particle.baseY = this.canvas.height;
            if (particle.baseY > this.canvas.height) particle.baseY = 0;

            // Draw particle
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
            this.ctx.fill();

            // Draw glow effect
            if (distance < this.mouseRadius * 1.5) {
                const glowOpacity = (1 - distance / (this.mouseRadius * 1.5)) * 0.5;
                this.ctx.beginPath();
                this.ctx.arc(particle.x, particle.y, particle.size * 2, 0, Math.PI * 2);
                this.ctx.fillStyle = `rgba(102, 126, 234, ${glowOpacity})`;
                this.ctx.fill();
            }
        });

        // Draw connecting lines between nearby particles
        this.particles.forEach((p1, i) => {
            this.particles.slice(i + 1).forEach(p2 => {
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 80) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(p1.x, p1.y);
                    this.ctx.lineTo(p2.x, p2.y);
                    this.ctx.strokeStyle = `rgba(255, 255, 255, ${0.1 * (1 - dist / 80)})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.stroke();
                }
            });
        });

        requestAnimationFrame(() => this.animate());
    }
}
