// WebRTC configuration
const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' }
    ]
};

// DOM elements
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
let audioDataChannel = null;

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

// Start audio streaming
async function startAudio() {
    try {
        isSessionActive = true;
        
        // Get local audio stream
        localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        log('Got local audio stream');

        // Create peer connection
        peerConnection = new RTCPeerConnection(configuration);
        log('Created peer connection');

        // Create audio data channel
        audioDataChannel = peerConnection.createDataChannel('audio', {
            ordered: true,
            maxRetransmits: 3
        });

        audioDataChannel.onopen = () => {
            log('Audio data channel opened');
        };

        audioDataChannel.onclose = (event) => {
            log(`Audio data channel closed: code=${event.code}, reason=${event.reason}`);
        };

        audioDataChannel.onerror = (error) => {
            log(`Audio data channel error: ${error.message || 'Unknown error'}`);
            console.error('Data channel error details:', error);
        };

        // Add buffer amount low event handler
        audioDataChannel.onbufferedamountlow = () => {
            log(`Data channel buffer amount low: ${audioDataChannel.bufferedAmount}`);
        };

        // Add ICE connection state monitoring
        peerConnection.oniceconnectionstatechange = () => {
            log(`ICE connection state changed to: ${peerConnection.iceConnectionState}`);
        };

        peerConnection.onicegatheringstatechange = () => {
            log(`ICE gathering state changed to: ${peerConnection.iceGatheringState}`);
        };

        peerConnection.onconnectionstatechange = () => {
            log(`Connection state changed to: ${peerConnection.connectionState}`);
        };

        peerConnection.onsignalingstatechange = () => {
            log(`Signaling state changed to: ${peerConnection.signalingState}`);
        };

        // Add ICE candidate handling
        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                log(`New ICE candidate: ${JSON.stringify(event.candidate)}`);
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'candidate',
                        candidate: event.candidate
                    }));
                }
            }
        };

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
                    
                    // Handle audio config
                    if (message.audio_config) {
                        log(`Received audio config: ${JSON.stringify(message.audio_config, null, 2)}`);
                        // Save audio config for later use
                        window.audioConfig = message.audio_config;
                    }
                    
                    // Setup audio processing
                    const audioTrack = localStream.getAudioTracks()[0];
                    const audioContext = new AudioContext();
                    const source = audioContext.createMediaStreamSource(new MediaStream([audioTrack]));
                    
                    try {
                        // Create audio processing work thread
                        const processorPath = new URL('audio-processor.js', window.location.href).href;
                        console.log('Loading audio processor from:', processorPath);
                        await audioContext.audioWorklet.addModule(processorPath);
                        const processor = new AudioWorkletNode(audioContext, 'audio-processor');
                        
                        // Set audio processing parameters
                        processor.port.postMessage({
                            type: 'config',
                            config: window.audioConfig
                        });
                        
                        // Process audio data
                        processor.port.onmessage = (e) => {
                            if (audioDataChannel && audioDataChannel.readyState === 'open') {
                                try {
                                    const message = e.data;
                                    if (audioDataChannel.bufferedAmount > 65535) {  // If buffer is too large
                                        log('Data channel buffer full, skipping data');
                                        return;
                                    }
                                    audioDataChannel.send(message.buffer);
                                    log(`Sent audio data, size: ${message.buffer.byteLength} bytes, buffer: ${audioDataChannel.bufferedAmount}`);
                                } catch (error) {
                                    log(`Error sending audio data: ${error.message}`);
                                    console.error('Send error details:', error);
                                }
                            } else {
                                log(`Data channel not ready, state: ${audioDataChannel ? audioDataChannel.readyState : 'null'}`);
                            }
                        };
                        
                        source.connect(processor);
                        processor.connect(audioContext.destination);
                        log('Audio processing setup completed');
                    } catch (error) {
                        log(`Error loading audio processor: ${error.message}`);
                        const errorDiv = document.getElementById('error');
                        errorDiv.style.display = 'block';
                        errorDiv.textContent = `Error loading audio processor: ${error.message}`;
                        throw error;
                    }
                    
                } else if (message.type === 'candidate') {
                    const success = message.candidate_response.status === 'success';
                    if (success) {
                        log('ICE candidate added successfully');
                    } else {
                        log('Failed to add ICE candidate');
                        const errorDiv = document.getElementById('error');
                        errorDiv.style.display = 'block';
                        errorDiv.textContent = `Error adding ICE candidate: ${message.candidate_response.message}`;
                        throw new Error(message.candidate_response.message);
                    }
                }
            } catch (error) {
                log(`Error processing message: ${error.message}`);
            }
        };

        // Create offer
        await createAndSendOffer();
        
        // Initialize audio visualization
        initAudioVisualization(localStream);
        log('Started audio visualization');

    } catch (error) {
        isSessionActive = false;
        log(`Error starting audio: ${error.message}`);
        statusDiv.textContent = 'Error';
    }
}

// Stop audio streaming
async function stopAudio() {
    try {
        isSessionActive = false;
        
        // Stop local stream
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
            localStream = null;
        }

        // Stop audio visualization
        stopAudioVisualization();

        // Close data channel
        if (audioDataChannel) {
            audioDataChannel.close();
            audioDataChannel = null;
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
        log('Stopped audio streaming');
    } catch (error) {
        log(`Error stopping audio: ${error.message}`);
    }
}

// Event listeners
startAudioButton.addEventListener('click', startAudio);
stopAudioButton.addEventListener('click', stopAudio); 