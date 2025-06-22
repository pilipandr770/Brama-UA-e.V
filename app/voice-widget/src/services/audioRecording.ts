import { AudioBlob } from '../types';
import { normalizeAudio, convertToWav } from '../utils/audioProcessing';

let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];

export const startRecording = async (): Promise<void> => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };

    mediaRecorder.start();
};

export const stopRecording = async (): Promise<AudioBlob> => {
    return new Promise((resolve) => {
        if (mediaRecorder) {
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioChunks = [];
                const normalizedAudio = await normalizeAudio(audioBlob);
                const wavAudio = await convertToWav(normalizedAudio);
                resolve(wavAudio);
            };

            mediaRecorder.stop();
        }
    });
};