export function normalizeAudio(audioBuffer: AudioBuffer): Float32Array {
    const channelData = audioBuffer.getChannelData(0);
    const max = Math.max(...channelData);
    const min = Math.min(...channelData);
    const range = max - min;

    if (range === 0) {
        return channelData;
    }

    const normalized = new Float32Array(channelData.length);
    for (let i = 0; i < channelData.length; i++) {
        normalized[i] = (channelData[i] - min) / range;
    }

    return normalized;
}

export function convertToWav(audioBuffer: AudioBuffer): Blob {
    const buffer = new ArrayBuffer(44 + audioBuffer.length * 2);
    const view = new DataView(buffer);

    // WAV header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + audioBuffer.length * 2, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, 44100, true);
    view.setUint32(28, 44100 * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    writeString(view, 36, 'data');
    view.setUint32(40, audioBuffer.length * 2, true);

    // Write PCM samples
    const pcmData = new Int16Array(audioBuffer.length);
    for (let i = 0; i < audioBuffer.length; i++) {
        pcmData[i] = Math.max(-1, Math.min(1, audioBuffer.getChannelData(0)[i])) * 0x7FFF;
    }

    for (let i = 0; i < pcmData.length; i++) {
        view.setInt16(44 + i * 2, pcmData[i], true);
    }

    return new Blob([buffer], { type: 'audio/wav' });
}

function writeString(view: DataView, offset: number, string: string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}