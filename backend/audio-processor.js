class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.silenceThreshold = 0.01;  // silence threshold
        this.silenceDuration = 0.5;    // silence duration (seconds)
        this.minSpeechDuration = 0.3;  // minimum speech duration (seconds)
        this.sampleRate = 48000;       // sample rate
        
        this.silenceCounter = 0;
        this.speechCounter = 0;
        this.isSpeaking = false;
        this.buffer = [];
    }

    process(inputs, outputs) {
        const input = inputs[0];
        if (input.length > 0) {
            const audioData = input[0];
            
            // calculate audio energy
            const energy = this.calculateEnergy(audioData);
            
            // detect speech activity
            if (energy > this.silenceThreshold) {
                this.silenceCounter = 0;
                this.speechCounter++;
                this.isSpeaking = true;
            } else {
                this.silenceCounter++;
                if (this.isSpeaking) {
                    this.speechCounter++;
                }
            }

            // add audio data to buffer
            this.buffer.push(...audioData);

            // detect sentence boundaries
            const silenceFrames = this.silenceCounter * (128 / this.sampleRate);
            const speechFrames = this.speechCounter * (128 / this.sampleRate);

            if (this.isSpeaking && 
                silenceFrames >= this.silenceDuration && 
                speechFrames >= this.minSpeechDuration) {
                // send complete sentence audio data
                this.port.postMessage({
                    type: 'sentence',
                    audio: Array.from(this.buffer),
                    duration: speechFrames
                });
                
                // reset state
                this.buffer = [];
                this.isSpeaking = false;
                this.speechCounter = 0;
            }
        }
        return true;
    }

    calculateEnergy(audioData) {
        let sum = 0;
        for (let i = 0; i < audioData.length; i++) {
            sum += audioData[i] * audioData[i];
        }
        return Math.sqrt(sum / audioData.length);
    }
}

registerProcessor('audio-processor', AudioProcessor); 