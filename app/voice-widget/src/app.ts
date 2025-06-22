import { VoiceRecorder } from './components/VoiceRecorder';
import { AudioVisualizer } from './components/AudioVisualizer';
import { TranscriptionDisplay } from './components/TranscriptionDisplay';
import { sendAudioToWhisper } from './services/whisperService';

const voiceRecorder = new VoiceRecorder();
const audioVisualizer = new AudioVisualizer();
const transcriptionDisplay = new TranscriptionDisplay();

document.getElementById('startRecordingButton').addEventListener('click', async () => {
    audioVisualizer.startVisualization();
    await voiceRecorder.startRecording();
});

document.getElementById('stopRecordingButton').addEventListener('click', async () => {
    audioVisualizer.stopVisualization();
    const audioBlob = await voiceRecorder.stopRecording();
    const transcription = await sendAudioToWhisper(audioBlob);
    transcriptionDisplay.updateTranscription(transcription);
});

document.getElementById('clearTranscriptionButton').addEventListener('click', () => {
    transcriptionDisplay.clearTranscription();
});