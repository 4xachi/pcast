# PCAST - AI Podcast Generator

<div align="center">

```
 ██████╗  ██████╗ █████╗ ███████╗████████╗
 ██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝
 ██████╔╝██║     ███████║███████╗   ██║   
 ██╔═══╝ ██║     ██╔══██║╚════██║   ██║   
 ██║     ╚██████╗██║  ██║███████║   ██║   
 ╚═╝      ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   
                                          
 AI Podcast Generator | Creator: John
```

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

</div>

## 📋 Overview

PCAST is an advanced AI podcast generator that creates professional-quality podcast scripts and audio using Google's Gemini AI models. With just a topic prompt, PCAST generates a natural, engaging conversation between two speakers and converts it into high-quality audio with distinct voices. Perfect for content creators, educators, language learners, or anyone interested in exploring AI-generated audio content.

## ✨ Key Features

- **AI-Powered Script Generation**: Create realistic, engaging podcast scripts on any topic using Gemini 2.5 Flash
- **Natural-Sounding Audio**: Convert scripts to high-quality audio using Gemini's advanced text-to-speech technology
- **Multiple Languages**: Support for English, Tagalog, and Taglish (Tagalog-English mix)
- **Customizable Voices**: Choose from 29 different voice options across male, female, and neutral categories
- **Accent Selection**: Select from English, Tagalog, or neutral accent profiles
- **Flexible Duration**: Generate podcasts of different lengths (2-5 minutes)
- **Interactive UI**: Colorful terminal interface with real-time progress visualization
- **Cross-Platform**: Works on Windows, macOS, Linux, and Android (via Termux)

## 📊 Technical Details

PCAST uses the following technologies:

- **Google Gemini AI**: Powers script generation (Gemini 2.5 Flash) and audio synthesis (Gemini TTS)
- **Python**: Built with modern Python for cross-platform compatibility
- **tqdm**: For smooth progress visualization during generation
- **colorama**: For enhanced terminal UI with colored text and formatting
- **pydub**: For audio processing and format conversion

## 🔧 Installation

### Prerequisites

- Python 3.7 or higher
- Internet connection (for API calls to Google's Gemini services)
- 100MB+ free disk space for application and generated podcasts

### For Windows, macOS, and Linux

1. **Install Python** (3.7+) if not already installed

2. **Clone the repository**:
```bash
git clone https://github.com/username/pcast.git
cd pcast
```

3. **Install required packages**:
```bash
pip install google-genai aiohttp pydub tqdm colorama
```

4. **Run the application**:
```bash
python app.py
```

### For Android (via Termux)

1. **Install Termux** from F-Droid or Google Play Store

2. **Install required packages**:
```bash
pkg update && pkg upgrade
pkg install python python-pip git termux-api
```

3. **Clone the repository**:
```bash
git clone https://github.com/username/pcast.git
cd pcast
```

4. **Install Python dependencies**:
```bash
pip install google-genai aiohttp pydub tqdm colorama
```

5. **Run the app**:
```bash
python app.py
```

6. **For audio playback in Termux**: Install the Termux:API app from the Play Store and run:
```bash
pkg install termux-api
```

## 📱 Usage Guide

### Starting the Application

1. Open a terminal/command prompt
2. Navigate to the PCAST directory
3. Run `python app.py`

### Creating a Podcast

1. **Configure Podcast Settings**:

   - **Speaker Names**: Enter custom names for both podcast hosts
   - **Voice Types**: Select from male, female, or neutral voices for each speaker
   - **Language**: Choose the podcast language:
     - **English**: Full English script
     - **Tagalog**: Full Filipino/Tagalog script
     - **Taglish**: Mix of Tagalog and English
   - **Accent**: Select the accent style:
     - **English**: Standard American English accent
     - **Tagalog**: Filipino English accent
     - **Neutral**: Accent-neutral delivery
   - **Duration**: Choose between short (2-3 minutes) or medium (4-5 minutes) format

2. **Generate Script**:
   - Enter a podcast topic (any subject, question, or theme)
   - The AI will generate a complete podcast script with both speakers
   - Review the color-coded script in the terminal

3. **Generate Audio**:
   - Choose to create audio from the script
   - Watch progress bars for audio generation and processing
   - The finished audio file will be saved to the `generated_podcasts` directory

4. **Play or Share**:
   - Option to play the audio directly from the app
   - Find the audio file in the `generated_podcasts` folder
   - Share the MP3/WAV file on any platform

### Example Topics

- "The future of artificial intelligence"
- "Beginner's guide to urban gardening"
- "Discussion about recent climate change initiatives"
- "Travel tips for budget backpackers"
- "Debate on the best superhero movies"

## 📁 File Structure

```
pcast/
├── app.py                # Main application code
├── README.md             # Project documentation (this file)
├── LICENSE               # License information
└── generated_podcasts/   # Directory for saved podcast files
    ├── podcast_*.txt     # Generated scripts
    └── podcast_*.wav     # Generated audio files
```

## 🔄 Command Line Arguments

- `python app.py`: Run the application normally
- `python app.py --help` or `python app.py -h`: Display help information
- `python app.py install`: Show installation instructions

## 🔍 Troubleshooting

### Common Issues

- **API Error**: Make sure you have a working internet connection
- **Audio Playback Issues**: Ensure your system has audio playback capabilities
- **Font Display Problems**: Some terminals may not display the ASCII art correctly
- **Slow Generation**: Script and audio generation may take longer on slower connections

### Solutions

- Try running with a stable internet connection
- Check if your device has sufficient storage space
- Ensure you've installed all required dependencies
- Update to the latest version with `git pull`

## 🔄 Updating

To update PCAST to the latest version:

```bash
cd pcast
git pull
pip install -r requirements.txt  # If dependencies have changed
```

## 🔮 Upcoming Features

- Background music integration
- Multi-speaker support (more than 2 voices)
- Additional export formats (MP3, OGG)
- Custom voice fine-tuning
- Podcast series management
- Web interface option

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Credits

- **Creator**: John
- **AI Technology**: Google Gemini AI
- **Voice Models**: Google TTS voices

## 📞 Support

For issues, feature requests, or questions, please open an issue on the GitHub repository.

---

<div align="center">

**PCAST** - Create amazing podcast content with AI

</div> 