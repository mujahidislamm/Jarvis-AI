document.addEventListener('DOMContentLoaded', () => {
    // ── DOM ELEMENTS ──
    const sidebar = document.getElementById('chat-sidebar');
    const sidebarToggleBtn = document.getElementById('sidebar-toggle-btn');
    const sidebarCloseBtn = document.getElementById('sidebar-close-btn');
    const historyList = document.getElementById('history-list');
    const newChatBtn = document.getElementById('new-chat-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');

    const heroStage = document.getElementById('hero-stage');
    const chatStream = document.getElementById('chat-stream');
    const messagesContainer = document.getElementById('messages-container');
    const typingIndicator = document.getElementById('typing-indicator');
    const typingStatusLabel = document.getElementById('typing-status-label');

    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const ttsToggleBtn = document.getElementById('tts-toggle-btn');
    const statusPill = document.getElementById('status-pill');
    const statusText = document.getElementById('status-text');
    const audioPlayer = document.getElementById('tts-audio');
    const audioStatusPill = document.getElementById('audio-status-pill');

    const imageModal = document.getElementById('image-modal');
    const imageModalBtn = document.getElementById('image-modal-btn');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const executeImageBtn = document.getElementById('execute-image-btn');
    const imagePromptInput = document.getElementById('image-prompt-input');
    const imageGallery = document.getElementById('image-gallery');
    const imageLoading = document.getElementById('image-loading');
    const quickImageCard = document.getElementById('quick-image-card');

    const userDisplayName = document.getElementById('user-display-name');

    // ── STATE ──
    let isTTSActive = true;
    let isListening = false;
    let recognition = null;
    let currentAssistantName = "Jarvis";
    let micPermissionRequestPending = false;
    let micPermissionErrorShown = false;

    // ── INITIALIZATION ──
    fetchSystemStatus();
    loadChatHistory();
    initSpeechRecognition();

    // ── EVENT LISTENERS ──
    sidebarToggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });

    sidebarCloseBtn.addEventListener('click', () => {
        sidebar.classList.add('collapsed');
    });

    newChatBtn.addEventListener('click', () => {
        heroStage.classList.remove('hidden');
        chatStream.classList.add('hidden');
        messagesContainer.innerHTML = '';
        setStatus('JARVIS ONLINE • READY', 'ready');
    });

    clearHistoryBtn.addEventListener('click', async () => {
        if (confirm("Clear all conversation history?")) {
            await fetch('/api/history/clear', { method: 'POST' });
            loadChatHistory();
            messagesContainer.innerHTML = '';
            heroStage.classList.remove('hidden');
            chatStream.classList.add('hidden');
        }
    });

    ttsToggleBtn.addEventListener('click', () => {
        isTTSActive = !isTTSActive;
        ttsToggleBtn.classList.toggle('active', isTTSActive);
        audioStatusPill.innerHTML = isTTSActive 
            ? '<i class="fa-solid fa-wave-square"></i> Audio Synth Active'
            : '<i class="fa-solid fa-volume-xmark"></i> Audio Muted';
        audioStatusPill.style.color = isTTSActive ? 'var(--primary-teal)' : 'var(--text-muted)';
        if (!isTTSActive && audioPlayer) {
            audioPlayer.pause();
        }
    });

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submitUserQuery();
        }
    });

    sendBtn.addEventListener('click', submitUserQuery);

    // Quick Action cards
    document.querySelectorAll('.quick-card[data-query]').forEach(card => {
        card.addEventListener('click', () => {
            const query = card.getAttribute('data-query');
            userInput.value = query;
            submitUserQuery();
        });
    });

    if (quickImageCard) {
        quickImageCard.addEventListener('click', () => {
            openImageModal();
        });
    }

    // Modal Events
    imageModalBtn.addEventListener('click', openImageModal);
    closeModalBtn.addEventListener('click', () => imageModal.classList.add('hidden'));
    imageModal.addEventListener('click', (e) => {
        if (e.target === imageModal) imageModal.classList.add('hidden');
    });

    executeImageBtn.addEventListener('click', executeImageGeneration);
    imagePromptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') executeImageGeneration();
    });

    // ── AUDIO CHIMES (WEB AUDIO API) ──
    function playChime(type = 'start') {
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) return;
            const ctx = new AudioCtx();
            const now = ctx.currentTime;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = 'sine';
            gain.gain.setValueAtTime(0.08, now);

            if (type === 'start') {
                osc.frequency.setValueAtTime(520, now);
                osc.frequency.exponentialRampToValueAtTime(880, now + 0.12);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
                osc.start(now);
                osc.stop(now + 0.22);
            } else {
                osc.frequency.setValueAtTime(880, now);
                osc.frequency.exponentialRampToValueAtTime(440, now + 0.14);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.24);
                osc.start(now);
                osc.stop(now + 0.24);
            }
        } catch (e) {
            // Audio context not allowed until interaction, safe to ignore
        }
    }

    // ── SPEECH RECOGNITION & VOICE RECORDING ENGINE ──
    let mediaRecorder = null;
    let audioChunks = [];
    let micStream = null;
    let fallbackTimer = null;
    const inputGlassBox = document.querySelector('.input-glass-box');
    const defaultPlaceholder = userInput.getAttribute('placeholder') || "Ask Jarvis anything, execute automation, or request research...";

    function initSpeechRecognition() {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRec) {
            try {
                recognition = new SpeechRec();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'en-US';

                recognition.onstart = () => {
                    isListening = true;
                    setListeningUI(true);
                    playChime('start');
                    setStatus('LISTENING FOR SPEECH...', 'listening');
                };

                recognition.onresult = (event) => {
                    let interimTranscript = '';
                    let finalTranscript = '';

                    for (let i = event.resultIndex; i < event.results.length; ++i) {
                        const transcript = event.results[i][0].transcript;
                        if (event.results[i].isFinal) {
                            finalTranscript += transcript;
                        } else {
                            interimTranscript += transcript;
                        }
                    }

                    if (finalTranscript) {
                        userInput.value = finalTranscript.trim();
                        stopListening();
                        submitUserQuery();
                    } else if (interimTranscript) {
                        userInput.value = interimTranscript;
                        setStatus('TRANSCRIBING VOICE...', 'listening');
                    }
                };

                recognition.onerror = (event) => {
                    console.warn("Speech Recognition Error:", event.error);
                    stopListening();

                    if (event.error === 'not-allowed' || event.error === 'permission-denied') {
                        if (!micPermissionErrorShown) {
                            micPermissionErrorShown = true;
                            setStatus('MIC BLOCKED • ALLOW IN BROWSER', 'ready');
                            alert("Microphone permission was blocked. Please click the lock or camera icon in your browser's address bar and allow Microphone access.");
                        }
                    } else if (event.error === 'network') {
                        // Switch to media recorder fallback only when browser speech recognition itself fails.
                        console.info("Web Speech network failure, switching to audio recorder fallback.");
                        startMediaRecorder();
                    } else if (event.error === 'no-speech') {
                        setStatus('JARVIS ONLINE • READY', 'ready');
                    } else {
                        setStatus('SPEECH ERROR • TRY AGAIN', 'ready');
                    }
                };

                recognition.onend = () => {
                    if (isListening) {
                        stopListening();
                    }
                };
            } catch (err) {
                console.warn("Could not instantiate SpeechRecognition:", err);
                recognition = null;
            }
        }

        // Attach click handler to mic button
        micBtn.addEventListener('click', toggleVoiceInput);
    }

    async function requestMicrophonePermission() {
        if (micPermissionRequestPending) {
            return false;
        }

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Voice recording is not supported in this browser. Please use Google Chrome or Microsoft Edge.");
            return false;
        }

        try {
            micPermissionRequestPending = true;
            micPermissionErrorShown = false;
            micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            return true;
        } catch (err) {
            console.error("Microphone access error:", err);
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                setStatus('MIC BLOCKED • ALLOW IN BROWSER', 'ready');
                if (!micPermissionErrorShown) {
                    micPermissionErrorShown = true;
                    alert("Microphone permission was denied. Please allow microphone access in your browser settings.");
                }
            } else {
                setStatus('MIC ACCESS ERROR', 'ready');
            }
            return false;
        } finally {
            micPermissionRequestPending = false;
        }
    }

    async function toggleVoiceInput() {
        // Stop audio playback if Jarvis is speaking
        if (audioPlayer && !audioPlayer.paused) {
            audioPlayer.pause();
        }
        if (window.speechSynthesis && window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
        }

        if (isListening) {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            } else if (recognition) {
                try { recognition.stop(); } catch (e) {}
            }
            stopListening();
            if (userInput.value.trim()) {
                submitUserQuery();
            }
            return;
        }

        // Restore the simpler original behavior: use browser speech recognition first,
        // and only fall back to MediaRecorder if that path fails.
        if (recognition) {
            try {
                recognition.start();
            } catch (e) {
                console.warn("SpeechRecognition start failed, retrying media recorder:", e);
                startMediaRecorder();
            }
        } else {
            startMediaRecorder();
        }
    }

    async function startMediaRecorder() {
        if (!micStream) {
            const permissionGranted = await requestMicrophonePermission();
            if (!permissionGranted) {
                return;
            }
        }

        try {
            audioChunks = [];

            let options = {};
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                options = { mimeType: 'audio/webm;codecs=opus' };
            } else if (MediaRecorder.isTypeSupported('audio/webm')) {
                options = { mimeType: 'audio/webm' };
            } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
                options = { mimeType: 'audio/ogg' };
            }

            mediaRecorder = new MediaRecorder(micStream, options);

            mediaRecorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
                if (micStream) {
                    micStream.getTracks().forEach(track => track.stop());
                    micStream = null;
                }

                if (audioChunks.length > 0 && audioBlob.size > 200) {
                    await sendAudioToServer(audioBlob);
                }
            };

            mediaRecorder.start();
            isListening = true;
            setListeningUI(true);
            playChime('start');
            setStatus('RECORDING AUDIO... (CLICK MIC TO SEND)', 'listening');

            clearTimeout(fallbackTimer);
            fallbackTimer = setTimeout(() => {
                if (isListening && mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    stopListening();
                }
            }, 12000);

        } catch (err) {
            console.error("Microphone access error:", err);
            stopListening();
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                setStatus('MIC BLOCKED • ALLOW IN BROWSER', 'ready');
                if (!micPermissionErrorShown) {
                    micPermissionErrorShown = true;
                    alert("Microphone permission was denied. Please allow microphone access in your browser settings.");
                }
            } else {
                setStatus('MIC ACCESS ERROR', 'ready');
            }
        }
    }

    async function sendAudioToServer(audioBlob) {
        setStatus('TRANSCRIBING AUDIO...', 'thinking');
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            const res = await fetch('/api/stt', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (data.success && data.text) {
                userInput.value = data.text.trim();
                submitUserQuery();
            } else {
                setStatus('NO SPEECH DETECTED', 'ready');
                setTimeout(() => setStatus('JARVIS ONLINE • READY', 'ready'), 2500);
            }
        } catch (e) {
            console.error("Failed sending audio to server:", e);
            setStatus('TRANSCRIPTION ERROR', 'ready');
        }
    }

    function setListeningUI(active) {
        if (active) {
            micBtn.classList.add('listening');
            micBtn.setAttribute('title', 'Listening... Click to stop and send');
            if (inputGlassBox) inputGlassBox.classList.add('listening-mode');
            userInput.setAttribute('placeholder', 'Listening... Speak your command or query...');
        } else {
            micBtn.classList.remove('listening');
            micBtn.setAttribute('title', 'Click to speak (Voice Recognition)');
            if (inputGlassBox) inputGlassBox.classList.remove('listening-mode');
            userInput.setAttribute('placeholder', defaultPlaceholder);
        }
    }

    function stopListening() {
        isListening = false;
        clearTimeout(fallbackTimer);
        setListeningUI(false);
        playChime('stop');
        setStatus('JARVIS ONLINE • READY', 'ready');
    }

    // ── STATUS MANAGEMENT ──
    function setStatus(text, mode = 'ready') {
        statusText.innerHTML = text;
        statusPill.className = 'status-pill ' + mode;
    }

    async function fetchSystemStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            if (data.username && userDisplayName) {
                userDisplayName.textContent = data.username;
            }
            if (data.assistant_name) {
                currentAssistantName = data.assistant_name;
            }
        } catch (e) {
            console.warn("Status fetch failed:", e);
        }
    }

    // ── CHAT QUERY & EXECUTION ──
    async function submitUserQuery() {
        const query = userInput.value.trim();
        if (!query) return;

        // Reset input
        userInput.value = '';
        userInput.style.height = 'auto';

        // Switch to Chat Stream
        heroStage.classList.add('hidden');
        chatStream.classList.remove('hidden');

        // Append User Message
        appendMessage('user', query);

        // Show typing indicator
        typingIndicator.classList.remove('hidden');
        typingStatusLabel.textContent = "Jarvis is processing intent...";
        setStatus('ANALYZING INTENT...', 'thinking');

        try {
            const res = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });

            const data = await res.json();
            typingIndicator.classList.add('hidden');

            if (data.success) {
                appendMessage('assistant', data.answer, data.source);
                loadChatHistory();

                // TTS playback
                if (isTTSActive && data.answer) {
                    playTTSAudio(data.answer);
                } else {
                    setStatus('JARVIS ONLINE • READY', 'ready');
                }
            } else {
                appendMessage('assistant', `⚠️ ${data.error || "An error occurred while communicating with Jarvis."}`, "System Alert");
                setStatus('JARVIS ONLINE • READY', 'ready');
            }
        } catch (err) {
            typingIndicator.classList.add('hidden');
            appendMessage('assistant', `⚠️ Network error: Could not reach Jarvis server. (${err.message})`, "Network Error");
            setStatus('SERVER DISCONNECTED', 'thinking');
        }
    }

    function appendMessage(role, text, source = null) {
        const row = document.createElement('div');
        row.className = `message-row ${role}-row`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-microchip"></i>';

        const content = document.createElement('div');
        content.className = 'message-content';

        const header = document.createElement('div');
        header.className = 'message-header';
        
        const now = new Date();
        const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        header.innerHTML = `
            <span><strong>${role === 'user' ? 'You' : currentAssistantName}</strong> &bull; ${timeStr}</span>
            ${source ? `<span class="message-source-tag">${source}</span>` : ''}
        `;

        const body = document.createElement('div');
        body.className = 'message-body';
        
        // Use marked for markdown formatting
        if (typeof marked !== 'undefined' && role === 'assistant') {
            body.innerHTML = marked.parse(text);
        } else {
            body.textContent = text;
        }

        content.appendChild(header);
        content.appendChild(body);
        row.appendChild(avatar);
        row.appendChild(content);

        messagesContainer.appendChild(row);
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    // ── TEXT TO SPEECH ──
    async function playTTSAudio(text) {
        setStatus('JARVIS SPEAKING...', 'speaking');
        try {
            const res = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });

            if (res.ok) {
                const blob = await res.blob();
                const audioUrl = URL.createObjectURL(blob);
                audioPlayer.src = audioUrl;
                audioPlayer.onended = () => {
                    setStatus('JARVIS ONLINE • READY', 'ready');
                };
                audioPlayer.onerror = () => {
                    fallbackBrowserTTS(text);
                };
                await audioPlayer.play();
            } else {
                fallbackBrowserTTS(text);
            }
        } catch (e) {
            fallbackBrowserTTS(text);
        }
    }

    function fallbackBrowserTTS(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            const cleanText = text.replace(/[*#|`]/g, '').slice(0, 300);
            const utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.rate = 1.05;
            utterance.pitch = 1.0;
            utterance.onend = () => setStatus('JARVIS ONLINE • READY', 'ready');
            window.speechSynthesis.speak(utterance);
        } else {
            setStatus('JARVIS ONLINE • READY', 'ready');
        }
    }

    // ── CHAT HISTORY LOAD ──
    async function loadChatHistory() {
        try {
            const res = await fetch('/api/history');
            const data = await res.json();
            const history = data.history || [];

            if (!history.length) {
                historyList.innerHTML = `
                    <div class="history-empty">
                        <i class="fa-regular fa-comments"></i>
                        <p>No conversation history yet</p>
                    </div>`;
                return;
            }

            historyList.innerHTML = '';
            // Display user queries
            const userHistory = history.filter(item => item.role === 'user').reverse();

            userHistory.forEach(item => {
                const card = document.createElement('div');
                card.className = 'history-item';
                card.innerHTML = `
                    <div class="history-item-header">
                        <span><i class="fa-solid fa-message"></i> Query</span>
                        <span>Recent</span>
                    </div>
                    <div class="history-item-snippet">${escapeHtml(item.content)}</div>
                `;
                card.addEventListener('click', () => {
                    userInput.value = item.content;
                    submitUserQuery();
                });
                historyList.appendChild(card);
            });
        } catch (e) {
            console.warn("Failed loading history:", e);
        }
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ── IMAGE GENERATION MODAL ──
    function openImageModal() {
        imageModal.classList.remove('hidden');
        imagePromptInput.focus();
        loadExistingImages();
    }

    async function loadExistingImages() {
        try {
            const res = await fetch('/api/generate-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: 'Iron Man' })
            });
            const data = await res.json();
            if (data.images && data.images.length) {
                renderGallery(data.images);
            }
        } catch (e) {}
    }

    async function executeImageGeneration() {
        const prompt = imagePromptInput.value.trim();
        if (!prompt) return;

        imageLoading.classList.remove('hidden');
        imageGallery.innerHTML = '';

        try {
            const res = await fetch('/api/generate-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt })
            });
            const data = await res.json();
            imageLoading.classList.add('hidden');

            if (data.images && data.images.length) {
                renderGallery(data.images);
            } else {
                imageGallery.innerHTML = `<p style="color:var(--text-muted);grid-column:1/-1;">No images returned. Please check HuggingFace API connectivity.</p>`;
            }
        } catch (e) {
            imageLoading.classList.add('hidden');
            imageGallery.innerHTML = `<p style="color:#ef4444;grid-column:1/-1;">Image generation error: ${e.message}</p>`;
        }
    }

    function renderGallery(imageUrls) {
        imageGallery.innerHTML = '';
        imageUrls.forEach(url => {
            const item = document.createElement('div');
            item.className = 'gallery-item';
            item.innerHTML = `<a href="${url}" target="_blank" title="View Fullscreen"><img src="${url}" alt="Generated Rendering" loading="lazy"></a>`;
            imageGallery.appendChild(item);
        });
    }
});
