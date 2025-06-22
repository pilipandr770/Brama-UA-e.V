export interface AudioBlob {
    blob: Blob;
    duration: number;
}

export interface TranscriptionResult {
    text: string;
    confidence: number;
}