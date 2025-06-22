class AudioVisualizer {
    private canvas: HTMLCanvasElement;
    private audioContext: AudioContext;
    private analyser: AnalyserNode;
    private dataArray: Uint8Array;

    constructor(canvas: HTMLCanvasElement) {
        this.canvas = canvas;
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        this.analyser = this.audioContext.createAnalyser();
        this.dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    }

    startVisualization(stream: MediaStream) {
        const source = this.audioContext.createMediaStreamSource(stream);
        source.connect(this.analyser);
        this.analyser.connect(this.audioContext.destination);
        this.draw();
    }

    stopVisualization() {
        this.audioContext.close();
    }

    private draw() {
        requestAnimationFrame(() => this.draw());
        this.analyser.getByteFrequencyData(this.dataArray);
        const canvasCtx = this.canvas.getContext('2d');
        if (canvasCtx) {
            canvasCtx.fillStyle = 'rgb(200, 200, 200)';
            canvasCtx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            const barWidth = (this.canvas.width / this.dataArray.length) * 2.5;
            let barHeight;
            let x = 0;

            for (let i = 0; i < this.dataArray.length; i++) {
                barHeight = this.dataArray[i];
                canvasCtx.fillStyle = 'rgb(' + (barHeight + 100) + ',50,50)';
                canvasCtx.fillRect(x, this.canvas.height - barHeight / 2, barWidth, barHeight / 2);
                x += barWidth + 1;
            }
        }
    }
}

export default AudioVisualizer;