# Voice Assistant with Speech Recognition

A powerful voice-controlled assistant using Vosk speech recognition, capable of executing a wide range of commands such as opening websites, controlling media, checking real-time information (time, date), and much more. With fuzzy command matching and an interactive GUI, this assistant enhances your productivity and user experience.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This voice assistant leverages the **Vosk** speech recognition model to accurately process voice commands in real-time. It supports multiple functionalities like opening websites, controlling applications, adjusting media volume, and retrieving the current time or date, among others. The assistant also integrates fuzzy matching (via Levenshtein distance) for more accurate command recognition, even with minor mispronunciations or variations. Additionally, a Tkinter-based GUI offers real-time feedback, making the interaction more intuitive.

---

## Features

- **Voice Command Recognition**: Responds to commands like greetings, opening websites, controlling media, and querying the system's time and date.
- **Speech-to-Text Conversion**: Powered by the **Vosk API**, it converts voice input into text for further processing.
- **Fuzzy Command Matching**: Uses **Levenshtein Distance** to allow flexible and accurate matching of commands even with small variations in phrasing.
- **Interactive GUI**: The Tkinter-based graphical interface displays logs, statuses, and provides feedback on system activity.
- **Real-time Audio Feedback**: Generates short feedback noises during activation and deactivation of the assistant for a seamless experience.
- **Cross-Platform**: Works on Windows, Linux, and macOS with minimal setup.

---

## Installation

Follow these steps to set up the voice assistant on your machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/voice-assistant.git
``

2. **Install the required dependencies**:
   Create a virtual environment (optional but recommended) and install the necessary Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Download the Vosk model**:

   * Download the relevant model from [Vosk Models](https://alphacephei.com/vosk/models). For Persian language, download `vosk-model-fa-0.42`.
   * Place the model directory in the root of the project.

4. **Run the assistant**:
   Once everything is set up, run the assistant with the following command:

   ```bash
   python voice_assistant.py
   ```

---

## Configuration

Customize the assistant's behavior by modifying the following configuration variables:

* `MODEL_PATH`: The path to the Vosk model directory you downloaded.
* `SAMPLERATE`: The sample rate for audio input (default: 16000 Hz).
* `NOISE_VOLUME`: Controls the feedback noise volume during activation and deactivation (default: 0.05).
* `SIMILARITY_THRESHOLD`: The threshold for fuzzy command matching. Commands with similarity above this value are recognized (default: 0.7).

---

## Usage

Once the assistant is running, you can activate it by saying commands such as:

* **Activation**: "Hello Assistant", "Start", "Wake up", "Listen", etc.
* **Deactivation**: "Goodbye", "Stop", "Enough", "Sleep", etc.
* **Greetings**: "Hello", "Hi", "How are you?", "Good morning", etc.
* **Website Opening**: "Open Google", "Open YouTube", "Open Facebook", etc.
* **Music Control**: "Next song", "Pause", "Volume up", "Volume down", etc.
* **System Commands**: "Open Notepad", "Open Calculator", "Open Chrome", etc.
* **Time & Date**: "What time is it?", "What's the date today?", etc.
* **Google Search**: "Search for \[query] on Google", "Google \[query]", etc.

---

## Development

This project is open for further improvements and additions. Here are some potential areas for future development:

* **Multi-Language Support**: Add support for multiple languages to cater to a wider audience.
* **Cloud Integration**: Implement cloud-based syncing for settings and preferences.
* **Enhanced Command Set**: Expand the list of supported commands and integrate more third-party services.
* **Error Handling**: Improve the error handling to make the assistant more resilient in noisy environments.
* **Mobile App**: Create a mobile version of the assistant for cross-platform usage.

---

## Contributing

We welcome contributions to improve the assistant. If you find a bug or have an idea for a feature, feel free to fork the repository and submit a pull request.

### How to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to your branch (`git push origin feature-name`).
6. Create a pull request.

Please ensure that your contributions are well-tested and documented.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

* **Vosk API**: Used for offline speech recognition. More details at [Vosk GitHub](https://github.com/alphacephei/vosk-api).
* **Levenshtein Distance**: Used for fuzzy string matching. Available in the [python-Levenshtein library](https://github.com/segelev/Levenshtein).
* **Tkinter**: For building the graphical user interface (GUI).
* **Sounddevice**: For handling real-time audio input from the microphone.

---

## Screenshots (Optional)

Here you can showcase screenshots of the application interface or the voice assistant in action.

---

Thank you for checking out this project! If you have any questions or feedback, feel free to open an issue or reach out via the contact section of this repository.
