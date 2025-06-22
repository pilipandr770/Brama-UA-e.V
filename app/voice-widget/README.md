# Voice Widget

This project is a voice widget that allows users to record audio, visualize the audio input, and transcribe the recorded audio using the OpenAI Whisper API.

## Features

- **Audio Recording**: Users can start and stop audio recording.
- **Audio Visualization**: Visualizes the audio input in real-time.
- **Transcription Display**: Displays the transcribed text from the recorded audio.
- **Integration with OpenAI Whisper**: Sends recorded audio for transcription.

## Project Structure

```
voice-widget
├── src
│   ├── components
│   │   ├── VoiceRecorder.ts       # Handles audio recording functionality
│   │   ├── AudioVisualizer.ts      # Visualizes audio input
│   │   └── TranscriptionDisplay.ts  # Displays transcribed text
│   ├── services
│   │   ├── audioRecording.ts       # Manages audio recording
│   │   └── whisperService.ts       # Sends audio to Whisper API
│   ├── utils
│   │   ├── audioProcessing.ts      # Utility functions for audio processing
│   │   └── formatters.ts           # Functions for formatting transcriptions
│   ├── types
│   │   └── index.ts                # Interfaces for the project
│   ├── constants.ts                # Constants used throughout the project
│   └── app.ts                      # Entry point of the application
├── public
│   └── index.html                  # Main HTML file for the widget
├── config
│   └── api.ts                     # Configuration settings for the API
├── package.json                    # npm configuration file
├── tsconfig.json                   # TypeScript configuration file
└── README.md                       # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd voice-widget
   ```
3. Install the dependencies:
   ```
   npm install
   ```

## Usage

1. Open `public/index.html` in a web browser.
2. Use the widget to record audio, visualize it, and view the transcriptions.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.