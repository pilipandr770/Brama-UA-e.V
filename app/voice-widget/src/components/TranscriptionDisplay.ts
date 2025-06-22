class TranscriptionDisplay {
    private transcriptionElement: HTMLElement;

    constructor(elementId: string) {
        this.transcriptionElement = document.getElementById(elementId);
    }

    updateTranscription(transcription: string) {
        this.transcriptionElement.innerText = transcription;
    }

    clearTranscription() {
        this.transcriptionElement.innerText = '';
    }
}

export default TranscriptionDisplay;