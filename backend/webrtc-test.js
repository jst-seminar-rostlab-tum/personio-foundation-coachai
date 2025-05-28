// WebRTC configuration
const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
};

// DOM elements
const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const statusDiv = document.getElementById('status');
const logDiv = document.getElementById('log');

// WebRTC variables
let peerConnection = null;
let localStream = null;
let ws = null;
let pendingOffer = null;
let isSessionActive = false;

// Speech recognition
let recognition = null;

// Logging function
function log(message) {
    const logEntry = document.createElement('div');
    logEntry.textContent = `${new Date().toLocaleTimeString()} - ${message}`;
    logDiv.appendChild(logEntry);
    logDiv.scrollTop = logDiv.scrollHeight;
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

// Send transcript through WebSocket
function sendTranscript(text) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'transcript',
            transcript: {
                text: text,
                timestamp: new Date().toISOString(),
                confidence: 0.95, // TODO: add confidence
                language: 'en-US' // TODO: add language
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