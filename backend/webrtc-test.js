// WebRTC configuration
const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
};

// DOM elements
const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const startAudioButton = document.getElementById('startAudioButton');
const stopAudioButton = document.getElementById('stopAudioButton');
const statusDiv = document.getElementById('status');
const logDiv = document.getElementById('log');
const audioVisualizer = document.getElementById('audioVisualizer');

// WebRTC variables
let peerConnection = null;
let localStream = null;
let ws = null;
let pendingOffer = null;
let isSessionActive = false;
let audioContext = null;
let audioSource = null;
let analyser = null;
let animationFrameId = null;

// Speech recognition
let recognition = null;

// Logging function
function log(message) {
    const logEntry = document.createElement('div');
    logEntry.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
    logDiv.appendChild(logEntry);
    logDiv.scrollTop = logDiv.scrollHeight;
}

// Initialize audio visualization
function initAudioVisualization(stream) {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    audioSource = audioContext.createMediaStreamSource(stream);
    analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    audioSource.connect(analyser);
    
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    const canvasCtx = audioVisualizer.getContext('2d');
    
    function draw() {
        animationFrameId = requestAnimationFrame(draw);
        
        analyser.getByteTimeDomainData(dataArray);
        
        canvasCtx.fillStyle = 'rgb(255, 255, 255)';
        canvasCtx.fillRect(0, 0, audioVisualizer.width, audioVisualizer.height);
        
        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'rgb(0, 0, 0)';
        canvasCtx.beginPath();
        
        const sliceWidth = audioVisualizer.width * 1.0 / bufferLength;
        let x = 0;
        
        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * audioVisualizer.height / 2;
            
            if (i === 0) {
                canvasCtx.moveTo(x, y);
            } else {
                canvasCtx.lineTo(x, y);
            }
            
            x += sliceWidth;
        }
        
        canvasCtx.lineTo(audioVisualizer.width, audioVisualizer.height / 2);
        canvasCtx.stroke();
    }
    
    draw();
}

// Stop audio visualization
function stopAudioVisualization() {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
    
    if (audioSource) {
        audioSource.disconnect();
        audioSource = null;
    }
    
    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }
}

// Initialize speech recognition
function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            let finalTranscript = '';
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (finalTranscript) {
                log(`Recognized: ${finalTranscript}`);
                // Send final transcript through WebSocket
                sendTranscript(finalTranscript);
            }
            if (interimTranscript) {
                log(`Interim: ${interimTranscript}`);
            }
        };

        recognition.onerror = (event) => {
            log(`Speech recognition error: ${event.error}`);
        };

        recognition.onend = () => {
            log('Speech recognition ended');
            // Only restart if session is still active
            if (isSessionActive) {
                recognition.start();
            }
        };
    } else {
        log('Speech recognition not supported in this browser');
    }
}

// Create and send offer
async function createAndSendOffer() {
    try {
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        pendingOffer = peerConnection.localDescription;
        
        // If WebSocket is ready, send the offer
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: 'offer',
                sdp: pendingOffer.sdp
            }));
            log('Sent offer');
            pendingOffer = null;
        } else {
            log(`WebSocket not ready. State: ${ws ? ws.readyState : 'null'}`);
        }
    } catch (error) {
        log(`Error creating offer: ${error.message}`);
    }
}

// Start WebRTC session
async function startSession() {
    try {
        isSessionActive = true;
        
        // Get local audio stream
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        log('Got local audio stream');

        // Initialize speech recognition
        initSpeechRecognition();
        recognition.start();
        log('Started speech recognition');

        // Create peer connection
        peerConnection = new RTCPeerConnection(configuration);
        log('Created peer connection');

        // Add local stream to peer connection
        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });

        // Connect to signaling server
        ws = new WebSocket('ws://localhost:8000/webrtc/signal');
        
        ws.onopen = async () => {
            log('Connected to signaling server');
            statusDiv.textContent = 'Connected';
            
            // If we have a pending offer, send it now
            if (pendingOffer) {
                ws.send(JSON.stringify({
                    type: 'offer',
                    sdp: pendingOffer.sdp
                }));
                log('Sent pending offer');
                pendingOffer = null;
            }
        };

        ws.onclose = (event) => {
            log(`WebSocket closed: ${event.code} ${event.reason}`);
            statusDiv.textContent = 'Disconnected';
            isSessionActive = false;
        };

        ws.onerror = (error) => {
            log(`WebSocket error: ${error.message || 'Unknown error'}`);
            statusDiv.textContent = 'Error';
        };

        ws.onmessage = async (event) => {
            try {
                const message = JSON.parse(event.data);
                log(`Received message: ${message.type}`);

                if (message.type === 'answer') {
                    await peerConnection.setRemoteDescription(new RTCSessionDescription(message));
                    log('Set remote description');
                } else if (message.type === 'candidate') {
                    await peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
                    log('Added ICE candidate');
                } else if (message.type === 'transcript_ack') {
                    log(`Transcript acknowledged: ${message.message}`);
                }
            } catch (error) {
                log(`Error processing message: ${error.message}`);
            }
        };

        // Create offer
        await createAndSendOffer();

    } catch (error) {
        isSessionActive = false;
        log(`Error starting session: ${error.message}`);
        statusDiv.textContent = 'Error';
    }
}

// Stop WebRTC session
async function stopSession() {
    try {
        isSessionActive = false;
        
        // Stop speech recognition
        if (recognition) {
            recognition.stop();
            recognition = null;
        }

        // Stop local stream
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            localStream = null;
        }

        // Stop audio visualization
        stopAudioVisualization();

        // Close peer connection
        if (peerConnection) {
            peerConnection.close();
            peerConnection = null;
        }

        // Close WebSocket
        if (ws) {
            ws.close();
            ws = null;
        }

        statusDiv.textContent = 'Disconnected';
        log('Session stopped');
    } catch (error) {
        log(`Error stopping session: ${error.message}`);
    }
}

// Start audio streaming
async function startAudio() {
    try {
        if (!localStream) {
            localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            log('Got local audio stream');
        }
        
        initAudioVisualization(localStream);
        log('Started audio visualization');
        
        // Send audio data through WebSocket
        const audioTrack = localStream.getAudioTracks()[0];
        const audioStream = new MediaStream([audioTrack]);
        const audioContext = new AudioContext();
        
        // Load and register AudioWorklet
        await audioContext.audioWorklet.addModule('audio-processor.js');
        const source = audioContext.createMediaStreamSource(audioStream);
        const processor = new AudioWorkletNode(audioContext, 'audio-processor');
        
        processor.port.onmessage = (e) => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                const message = e.data;
                if (message.type === 'sentence') {
                    ws.send(JSON.stringify({
                        type: 'audio',
                        audio: message.audio,
                        duration: message.duration
                    }));
                    log(`Sent audio sentence (duration: ${message.duration.toFixed(2)}s)`);
                }
            }
        };
        
        source.connect(processor);
        processor.connect(audioContext.destination);
        
        log('Started audio streaming');
    } catch (error) {
        log(`Error starting audio: ${error.message}`);
    }
}

// Stop audio streaming
function stopAudio() {
    stopAudioVisualization();
    log('Stopped audio streaming');
}

// Send transcript through WebSocket
function sendTranscript(text) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'transcript',
            transcript: {
                text: text,
                timestamp: new Date().toISOString(),
                confidence: 0.95,
                language: 'en-US'
            }
        }));
        log(`Sent transcript: ${text}`);
    } else {
        log('WebSocket not ready for sending transcript');
    }
}

// Event listeners
startButton.addEventListener('click', startSession);
stopButton.addEventListener('click', stopSession);
startAudioButton.addEventListener('click', startAudio);
stopAudioButton.addEventListener('click', stopAudio); 