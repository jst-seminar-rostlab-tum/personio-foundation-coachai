class AudioProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        // 默认配置
        this.silenceThreshold = 0.01;  // 静音阈值
        this.silenceDuration = 0.5;    // 静音持续时间(秒)
        this.minSpeechDuration = 0.3;  // 最小语音持续时间(秒)
        this.sampleRate = 48000;       // 采样率
        this.bufferSize = 2048;        // 缓冲区大小
        
        this.silenceCounter = 0;
        this.speechCounter = 0;
        this.isSpeaking = false;
        this.buffer = [];

        // 监听配置消息
        this.port.onmessage = (event) => {
            if (event.data.type === 'config') {
                const config = event.data.config;
                this.silenceThreshold = config.silence_threshold;
                this.silenceDuration = config.silence_duration;
                this.minSpeechDuration = config.min_speech_duration;
                this.sampleRate = config.sample_rate;
                this.bufferSize = config.buffer_size;
                console.log('Audio processor configured:', config);
            }
        };
    }

    process(inputs) {
        const input = inputs[0];
        if (input.length > 0) {
            const audioData = input[0];
            
            // 计算音频能量
            const energy = this.calculateEnergy(audioData);
            
            // 检测语音活动
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

            // 添加音频数据到缓冲区
            this.buffer.push(...audioData);

            // 检测句子边界
            const silenceFrames = this.silenceCounter * (128 / this.sampleRate);
            const speechFrames = this.speechCounter * (128 / this.sampleRate);

            if (this.isSpeaking && 
                silenceFrames >= this.silenceDuration && 
                speechFrames >= this.minSpeechDuration) {
                // 发送完整的句子音频数据
                this.port.postMessage({
                    buffer: new Float32Array(this.buffer).buffer,
                    duration: speechFrames
                }, [new Float32Array(this.buffer).buffer]);
                
                // 重置状态
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