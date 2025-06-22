export function formatTranscription(transcription: string): string {
    return transcription.trim();
}

export function highlightKeywords(transcription: string, keywords: string[]): string {
    let highlightedTranscription = transcription;
    keywords.forEach(keyword => {
        const regex = new RegExp(`(${keyword})`, 'gi');
        highlightedTranscription = highlightedTranscription.replace(regex, '<strong>$1</strong>');
    });
    return highlightedTranscription;
}