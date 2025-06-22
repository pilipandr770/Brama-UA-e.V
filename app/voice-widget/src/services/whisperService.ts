import axios from 'axios';
import { API_URL } from '../constants';
import { AudioBlob, TranscriptionResult } from '../types';

export async function sendAudioToWhisper(audioBlob: AudioBlob): Promise<TranscriptionResult> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.wav');

    try {
        const response = await axios.post(`${API_URL}/whisper`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data as TranscriptionResult;
    } catch (error) {
        throw new Error('Error sending audio to Whisper: ' + error.message);
    }
}