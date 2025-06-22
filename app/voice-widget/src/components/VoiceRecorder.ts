class VoiceRecorder {
    private mediaRecorder: MediaRecorder | null = null;
    private audioChunks: Blob[] = [];

    startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                this.mediaRecorder = new MediaRecorder(stream);
                this.mediaRecorder.start();

                this.mediaRecorder.ondataavailable = event => {
                    this.audioChunks.push(event.data);
                };
            })
            .catch(error => {
                console.error("Error accessing audio devices.", error);
            });
    }

    stopRecording() {
        return new Promise<Blob>((resolve, reject) => {
            if (this.mediaRecorder) {
                this.mediaRecorder.stop();
                this.mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                    this.audioChunks = [];
                    resolve(audioBlob);
                };
                this.mediaRecorder.onerror = event => {
                    reject(event.error);
                };
            } else {
                reject(new Error("MediaRecorder is not initialized."));
            }
        });
    }

    getAudioBlob(): Blob | null {
        return this.audioChunks.length > 0 ? new Blob(this.audioChunks, { type: 'audio/wav' }) : null;
    }
}

export default VoiceRecorder;