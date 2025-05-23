#!/usr/bin/env python3
# To run this code you need to install the following dependencies:
# pip install google-genai aiohttp pydub tqdm colorama

import asyncio
import base64
import json
import mimetypes
import os
import re
import struct
import sys
import time
import random
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from google import genai
from google.genai import types
from tqdm import tqdm
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

# Constants
DEFAULT_API_KEY = "AIzaSyDQtDYzHTK67JcgurfpwUl021-X_qPPWwA"
OUTPUT_DIR = "generated_podcasts"
DEFAULT_MODEL = "gemini-2.5-flash-preview-05-20"
TTS_MODEL = "gemini-2.5-flash-preview-tts"
MAX_RETRIES = 3
RETRY_DELAY = 2

# ASCII Art for the application (with colors)
PCAST_ASCII = f"""{Fore.CYAN}
 ██████╗  ██████╗ █████╗ ███████╗████████╗
 ██╔══██╗██╔════╝██╔══██╗██╔════╝╚══██╔══╝
 ██████╔╝██║     ███████║███████╗   ██║   
 ██╔═══╝ ██║     ██╔══██║╚════██║   ██║   
 ██║     ╚██████╗██║  ██║███████║   ██║   
 ╚═╝      ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   
                                          
{Fore.GREEN} AI Podcast Generator | Coded by: John
"""

# Create output directory if it doesn't exist
Path(OUTPUT_DIR).mkdir(exist_ok=True)

class PodcastGenerator:
    """Main class for handling podcast generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the podcast generator with API key."""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", DEFAULT_API_KEY)
        self.client = genai.Client(api_key=self.api_key)
        self.voices = {
            "male": ["algenib", "alnilam", "charon", "enceladus", "fenrir", "iapetus", "orus", 
                    "puck", "pulcherrima", "rasalgethi", "sadachbia", "sadaltager", 
                    "schedar", "umbriel", "zubenelgenubi"],
            "female": ["achernar", "aoede", "autonoe", "callirrhoe", "despina", "erinome", 
                      "gacrux", "kore", "laomedeia", "leda", "sulafat", "vindemiatrix", "zephyr"],
            "neutral": ["achird"]  # Only one neutral voice from the provided list
        }
        
        # Default podcast instructions
        self.podcast_instructions = {
            "english": "Speak with an American/standard English accent throughout the podcast. Use clear American pronunciation, intonation patterns, and speech rhythms.",
            "tagalog": "Speak with a Filipino/Tagalog accent throughout the podcast. Use Filipino English pronunciation patterns, rhythms and intonation even when speaking in English.",
            "neutral": "Read the following podcast interview script in a natural, conversational tone. Use a natural, relaxed speaking style as if chatting with friends on a podcast. Include natural reactions and casual acknowledgments between speakers."
        }
        
    def save_binary_file(self, file_name: str, data: bytes) -> str:
        """Save binary data to a file and return the full path."""
        full_path = os.path.join(OUTPUT_DIR, file_name)
        with open(full_path, "wb") as f:
            f.write(data)
        return full_path

    def save_text_file(self, file_name: str, text: str) -> str:
        """Save text data to a file and return the full path."""
        full_path = os.path.join(OUTPUT_DIR, file_name)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(text)
        return full_path

    def generate_podcast_script(self, topic: str, speaker1_name: str = "Speaker 1", 
                                speaker2_name: str = "Speaker 2", language_choice: str = "english",
                                duration_minutes: int = 3) -> str:
        """Generate a podcast script using Gemini AI based on the provided topic."""
        # Set language instruction based on user's choice
        language_instruction = ""
        if language_choice.lower() == "tagalog":
            language_instruction = "Generate the script entirely in Tagalog language. "
        elif language_choice.lower() == "taglish":
            language_instruction = "Generate the script in Taglish (a mix of Tagalog and English). Use both languages naturally as Filipinos would in conversation. "
        elif language_choice.lower() != "english":
            # For other languages that might be supported
            language_instruction = f"Generate the script in {language_choice} language. "
        
        # Calculate approximate word count based on desired duration
        # Average speaking rate is ~150 words per minute
        min_words = duration_minutes * 120  # Lower end of range
        max_words = duration_minutes * 170  # Upper end of range
        
        # Create a prompt for generating a podcast script about the given topic
        prompt = f"""Create a podcast script on the topic: {topic}
        
        {language_instruction}The script should:
        - Have exactly two speakers named "{speaker1_name}" and "{speaker2_name}"
        - Include an introduction, discussion, and conclusion
        - Be conversational, engaging, and informative
        - Be EXACTLY {duration_minutes}-{duration_minutes+1} minutes in length when read aloud
        - Be approximately {min_words}-{max_words} words long to match this duration
        - Format each line with the speaker name followed by their dialogue (Example: "{speaker1_name}: Hello everyone!")
        - Include a brief intro where speakers introduce themselves and the podcast topic
        - Have a clear structure with logical flow between topics
        - ALWAYS end with a proper conclusion and sign-off line
        - Make sure the script is substantial enough to fill the entire {duration_minutes}-minute duration
        
        Please provide only the script with no additional comments or formatting."""
        
        for attempt in range(MAX_RETRIES):
            try:
                # Create a progress bar to show activity during script generation
                pbar = tqdm(
                    total=100, 
                    desc=f"{Fore.YELLOW}Generating podcast script", 
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}",
                    dynamic_ncols=True
                )
                
                # Set up an async function to update the progress bar while waiting
                def update_progress():
                    # Simulate incremental progress up to 95% (keep the last 5% for completion)
                    progress = 0
                    while progress < 95:
                        # Randomize the progress increments for a more natural feel
                        increment = min(95 - progress, max(1, int(progress / 10) + 1))
                        progress += increment
                        pbar.n = progress
                        pbar.refresh()
                        # Adjust sleep time to make the animation smoother and more random
                        time.sleep(0.2 + random.random() * 0.3)
                
                # Start the progress bar animation in a separate thread
                progress_thread = threading.Thread(target=update_progress)
                progress_thread.daemon = True
                progress_thread.start()
                
                # First attempt with higher token limit
                response = self.client.models.generate_content(
                    model=DEFAULT_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.8,
                        max_output_tokens=4000,
                    )
                )
                
                # Set progress to 100% when complete
                pbar.n = 100
                pbar.refresh()
                pbar.close()
                
                if not response.text or response.text.strip() == "":
                    if attempt < MAX_RETRIES - 1:
                        print(f"{Fore.RED}Empty response received. Retrying ({attempt+1}/{MAX_RETRIES})...")
                        time.sleep(RETRY_DELAY)
                        continue
                    return f"{Fore.RED}Error: Unable to generate script in {language_choice} for this topic. Please try a different language or topic."
                
                script = response.text.strip()
                
                # Check if script appears to be cut off (ends without punctuation or ends with a partial sentence)
                if not script.endswith(('.', '!', '?')) or script.rstrip().endswith(('ni', 'at', 'ang', 'ng', 'sa')):
                    print(f"{Fore.YELLOW}Script appears incomplete. Attempting to complete it...")
                    
                    # Generate a proper ending for the script
                    completion_prompt = f"""This is an incomplete podcast script that needs a proper conclusion. 
                    Please provide ONLY a brief conclusion (1-2 exchanges between speakers) that wraps up the conversation naturally.
                    Use the same speaker names ({speaker1_name} and {speaker2_name}) and same language.
                    
                    Incomplete script:
                    {script}"""
                    
                    try:
                        # Create a new progress bar for conclusion generation
                        conclusion_pbar = tqdm(
                            total=100, 
                            desc=f"{Fore.YELLOW}Generating conclusion", 
                            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
                        )
                        
                        # Animate the conclusion progress bar
                        def update_conclusion_progress():
                            progress = 0
                            while progress < 95:
                                increment = min(95 - progress, max(1, int(progress / 10) + 1))
                                progress += increment
                                conclusion_pbar.n = progress
                                conclusion_pbar.refresh()
                                time.sleep(0.1 + random.random() * 0.2)
                        
                        # Start the progress animation
                        conclusion_thread = threading.Thread(target=update_conclusion_progress)
                        conclusion_thread.daemon = True
                        conclusion_thread.start()
                        
                        completion_response = self.client.models.generate_content(
                            model=DEFAULT_MODEL,
                            contents=completion_prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.7,
                                max_output_tokens=1000,
                            )
                        )
                        
                        conclusion_pbar.n = 100
                        conclusion_pbar.refresh()
                        conclusion_pbar.close()
                        
                        if completion_response.text and completion_response.text.strip():
                            # Append the conclusion to the script
                            script += "\n" + completion_response.text.strip()
                    except Exception as e:
                        if 'conclusion_pbar' in locals():
                            conclusion_pbar.close()
                        print(f"{Fore.RED}Note: Couldn't generate a conclusion. {str(e)}")
                
                return script
            
            except Exception as e:
                if 'pbar' in locals():
                    pbar.close()
                
                error_message = str(e)
                if "content_filter" in error_message.lower():
                    return f"{Fore.RED}Error: The topic may contain sensitive content that cannot be generated. Please try a different topic."
                elif attempt < MAX_RETRIES - 1:
                    print(f"{Fore.RED}Error occurred: {error_message}. Retrying ({attempt+1}/{MAX_RETRIES})...")
                    time.sleep(RETRY_DELAY)
                else:
                    return f"{Fore.RED}Error: {error_message}. Please try a different topic."

    def select_voices(self, gender1: str, gender2: str) -> Tuple[str, str]:
        """Select appropriate voices based on gender preferences."""
        import random
        
        voice1 = random.choice(self.voices.get(gender1.lower(), self.voices["neutral"]))
        voice2 = random.choice(self.voices.get(gender2.lower(), self.voices["neutral"]))
        
        # Ensure we don't select the same voice for both speakers
        while voice2 == voice1 and len(self.voices.get(gender2.lower(), self.voices["neutral"])) > 1:
            voice2 = random.choice(self.voices.get(gender2.lower(), self.voices["neutral"]))
            
        return voice1, voice2

    async def generate_podcast_audio(self, script: str, topic: str, 
                                   speaker1_name: str = "Host1", speaker2_name: str = "Host2", 
                                   accent: str = "neutral", voice1: str = "zephyr", voice2: str = "puck") -> Tuple[str, str]:
        """Generate audio from the podcast script using Gemini TTS."""
        # Use default podcast instructions based on the accent
        instruction = self.podcast_instructions.get(accent.lower(), self.podcast_instructions["neutral"])
        
        # Add instructions to the script
        enhanced_script = f"{instruction}\n\n{script}"

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=enhanced_script),
                ],
            ),
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature=1,
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker=speaker1_name,
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice1
                                )
                            ),
                        ),
                        types.SpeakerVoiceConfig(
                            speaker=speaker2_name,
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=voice2
                                )
                            ),
                        ),
                    ]
                ),
            ),
        )

        print(f"{Fore.BLUE}Initializing audio generation... This may take a moment.")
        
        # Create initial progress indicator
        init_pbar = tqdm(
            total=100, 
            desc=f"{Fore.BLUE}Preparing audio engine",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
            dynamic_ncols=True
        )
        
        # Simulate initial setup with smooth animation
        def animate_init():
            for i in range(1, 101):
                init_pbar.n = i
                init_pbar.refresh()
                # Vary speed based on progress
                delay = 0.05 if i < 80 else 0.02
                time.sleep(delay * random.random())
                
        init_thread = threading.Thread(target=animate_init)
        init_thread.daemon = True
        init_thread.start()
        
        # Wait for animation to get started
        time.sleep(1)
        
        # Collect all audio chunks
        all_audio_chunks = []
        mime_type = None
        progress_bar = None
        
        for attempt in range(MAX_RETRIES):
            try:
                # Wait for the init animation to finish
                init_thread.join(timeout=0.5)
                init_pbar.close()
                
                # Create a progress bar with unknown total but showing activity
                progress_bar = tqdm(
                    desc=f"{Fore.MAGENTA}Processing audio chunks", 
                    unit="chunk",
                    bar_format="{l_bar}{bar}| {n_fmt} chunks {postfix}",
                    dynamic_ncols=True
                )
                
                # Start a pulse animation for the bar while waiting for chunks
                received_chunk = False
                
                def pulse_animation():
                    pulse_count = 0
                    while not received_chunk:
                        progress_bar.set_postfix_str(f"waiting{' .' * (pulse_count % 4)}")
                        progress_bar.refresh()
                        pulse_count += 1
                        time.sleep(0.5)
                
                pulse_thread = threading.Thread(target=pulse_animation)
                pulse_thread.daemon = True
                pulse_thread.start()
                
                for chunk in self.client.models.generate_content_stream(
                    model=TTS_MODEL,
                    contents=contents,
                    config=generate_content_config,
                ):
                    if (
                        chunk.candidates is None
                        or chunk.candidates[0].content is None
                        or chunk.candidates[0].content.parts is None
                    ):
                        continue
                    
                    if chunk.candidates[0].content.parts[0].inline_data:
                        # We received a real chunk, stop the pulse animation
                        if not received_chunk:
                            received_chunk = True
                            # Give time for the thread to notice and stop
                            time.sleep(0.6)
                            progress_bar.set_postfix_str("")
                        
                        inline_data = chunk.candidates[0].content.parts[0].inline_data
                        # Store the audio data
                        all_audio_chunks.append(inline_data.data)
                        # Keep track of the mime type (assuming it's consistent across chunks)
                        if mime_type is None:
                            mime_type = inline_data.mime_type
                        progress_bar.update(1)
                    else:
                        if hasattr(chunk, 'text') and chunk.text and chunk.text.strip():
                            progress_bar.write(chunk.text)
                
                progress_bar.close()
                break  # If successful, break the retry loop
                
            except Exception as e:
                if progress_bar:
                    progress_bar.close()
                if 'init_pbar' in locals() and init_pbar:
                    init_pbar.close()
                
                error_message = str(e)
                if attempt < MAX_RETRIES - 1:
                    print(f"\n{Fore.RED}Error occurred during audio generation: {error_message}")
                    print(f"{Fore.YELLOW}Retrying ({attempt+1}/{MAX_RETRIES}) in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    raise Exception(f"Failed to generate audio after {MAX_RETRIES} attempts: {error_message}")
        
        print(f"\n{Fore.BLUE}Processing audio data...")
        
        if not all_audio_chunks:
            raise Exception("No audio was generated. Please try again with a different topic.")
            
        # Combine all audio chunks with a progress bar
        chunk_count = len(all_audio_chunks)
        with tqdm(
            total=chunk_count, 
            desc=f"{Fore.CYAN}Combining audio chunks", 
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} chunks"
        ) as pbar:
            # Add a brief delay and smoother animation
            combined_audio = b''
            for i, chunk in enumerate(all_audio_chunks):
                combined_audio += chunk
                pbar.update(1)
                # Add slight delay for visual effect on smaller datasets
                if chunk_count < 20 and i < chunk_count - 1:  
                    time.sleep(0.05)
        
        # Save the combined audio
        timestamp = self.get_timestamp()
        sanitized_topic = re.sub(r'[^\w\s-]', '', topic)[:30].strip().replace(' ', '_')
        file_name = f"podcast_{sanitized_topic}_{timestamp}"
        
        # Save the script for reference
        script_path = self.save_text_file(f"{file_name}.txt", script)
        
        file_extension = mimetypes.guess_extension(mime_type) if mime_type else None
        if file_extension is None:
            file_extension = ".wav"
            with tqdm(total=100, desc=f"{Fore.BLUE}Converting to WAV format") as pbar:
                # Simulate conversion progress
                def animate_conversion():
                    progress = 0
                    while progress < 95:
                        # Convert progressively faster
                        increment = max(1, min(5, int(progress/20) + 1))
                        progress += increment
                        pbar.n = progress
                        pbar.refresh()
                        time.sleep(0.03 + random.random() * 0.05)
                
                # Start conversion animation
                convert_thread = threading.Thread(target=animate_conversion)
                convert_thread.daemon = True
                convert_thread.start()
                
                # Actual conversion
                combined_audio = self.convert_to_wav(combined_audio, mime_type or "audio/L16;rate=24000")
                
                # Finalize progress bar
                pbar.n = 100
                pbar.refresh()
        
        # Show saving progress
        with tqdm(total=100, desc=f"{Fore.GREEN}Saving podcast files") as save_pbar:
            save_pbar.update(30)
            audio_path = self.save_binary_file(f"{file_name}{file_extension}", combined_audio)
            save_pbar.update(70)
            
        print(f"\n{Fore.GREEN}✓ Complete podcast audio saved as: {Style.BRIGHT}{audio_path}")
        print(f"{Fore.GREEN}✓ Script saved as: {Style.BRIGHT}{script_path}")
        
        return audio_path, script_path

    def get_timestamp(self) -> str:
        """Return a simple timestamp for file naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def convert_to_wav(self, audio_data: bytes, mime_type: str) -> bytes:
        """Generates a WAV file header for the given audio data and parameters."""
        parameters = self.parse_audio_mime_type(mime_type)
        bits_per_sample = parameters["bits_per_sample"]
        sample_rate = parameters["rate"]
        num_channels = 1
        data_size = len(audio_data)
        bytes_per_sample = bits_per_sample // 8
        block_align = num_channels * bytes_per_sample
        byte_rate = sample_rate * block_align
        chunk_size = 36 + data_size 

        # http://soundfile.sapp.org/doc/WaveFormat/
        header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",          
            chunk_size,       
            b"WAVE",         
            b"fmt ",         
            16,               
            1,                
            num_channels,    
            sample_rate,     
            byte_rate,        
            block_align,     
            bits_per_sample,  
            b"data",          
            data_size         
        )
        return header + audio_data

    def parse_audio_mime_type(self, mime_type: str) -> Dict[str, int]:
        """Parses bits per sample and rate from an audio MIME type string."""
        bits_per_sample = 16
        rate = 24000

        # Extract rate from parameters
        parts = mime_type.split(";")
        for param in parts: # Skip the main type part
            param = param.strip()
            if param.lower().startswith("rate="):
                try:
                    rate_str = param.split("=", 1)[1]
                    rate = int(rate_str)
                except (ValueError, IndexError):
                    pass # Keep rate as default
            elif param.startswith("audio/L"):
                try:
                    bits_per_sample = int(param.split("L", 1)[1])
                except (ValueError, IndexError):
                    pass # Keep bits_per_sample as default if conversion fails

        return {"bits_per_sample": bits_per_sample, "rate": rate}

    def get_user_input(self, prompt: str, default: str = "") -> str:
        """Get user input with a default value."""
        response = input(f"{Fore.YELLOW}{prompt}{Fore.CYAN}{f' (default: {default})' if default else ''}{Fore.RESET}: ").strip()
        return response if response else default

    def get_menu_choice(self, prompt: str, options: Dict[str, str], default: str = "1") -> str:
        """Display a menu and get user choice."""
        print(f"\n{Fore.YELLOW}{prompt}")
        for key, value in options.items():
            print(f"{Fore.CYAN}{key}. {Fore.WHITE}{value}")
        
        choice = self.get_user_input(f"Enter your choice (1-{len(options)})", default)
        return choice

    def clear_screen(self):
        """Clear the terminal screen based on the operating system."""
        if sys.platform == "win32":
            os.system("cls")
        else:
            os.system("clear")

async def main():
    """Main function to run the podcast generator."""
    # Clear screen and display ASCII art
    generator = PodcastGenerator()
    generator.clear_screen()
    print(PCAST_ASCII)
    
    print(f"\n{Fore.WHITE}{Back.BLUE}===== ADVANCED AI PODCAST GENERATOR ====={Back.RESET}")
    print(f"{Fore.CYAN}This tool generates a podcast script and audio using Gemini API.")
    print(f"{Fore.CYAN}Enter a topic for your podcast, and AI will create a script with two speakers.")
    print(f"{Fore.CYAN}The script will then be converted to audio using advanced text-to-speech.\n")
    
    # Initialize the podcast generator
    api_key = os.environ.get("GEMINI_API_KEY", DEFAULT_API_KEY)
    generator = PodcastGenerator(api_key)
    
    # Display a fancy setup header
    print(f"{Fore.WHITE}{Back.GREEN} PODCAST SETUP {Back.RESET}")
    
    # Get custom speaker names
    print(f"\n{Fore.YELLOW}Let's set up your podcast speakers:")
    speaker1_name = generator.get_user_input("Enter name for first speaker", "Host 1")
    speaker2_name = generator.get_user_input("Enter name for second speaker", "Host 2")
    
    # Get gender for voice selection
    gender1 = generator.get_menu_choice("Select voice type for first speaker:", 
                                      {"1": "Male", "2": "Female", "3": "Neutral"}, "1")
    gender1_map = {"1": "male", "2": "female", "3": "neutral"}
    gender1 = gender1_map.get(gender1, "male")
    
    gender2 = generator.get_menu_choice("Select voice type for second speaker:", 
                                      {"1": "Male", "2": "Female", "3": "Neutral"}, "2")
    gender2_map = {"1": "male", "2": "female", "3": "neutral"}
    gender2 = gender2_map.get(gender2, "female")
    
    # Select voices based on gender
    voice1, voice2 = generator.select_voices(gender1, gender2)
    print(f"\n{Fore.GREEN}✓ Your podcast will feature {Fore.WHITE}{Style.BRIGHT}{speaker1_name}{Style.RESET_ALL}{Fore.GREEN} (voice: {voice1}) and {Fore.WHITE}{Style.BRIGHT}{speaker2_name}{Style.RESET_ALL}{Fore.GREEN} (voice: {voice2})!")
    
    # Language selection
    language_choice = generator.get_menu_choice("Select script language:", 
                                              {"1": "English", "2": "Tagalog", "3": "Taglish (Tagalog-English)"}, "1")
    language_map = {"1": "english", "2": "tagalog", "3": "taglish"}
    language_choice = language_map.get(language_choice, "english")
    print(f"{Fore.GREEN}✓ Selected language: {Fore.WHITE}{Style.BRIGHT}{language_choice.capitalize()}")
    
    # Accent selection
    accent_choice = generator.get_menu_choice("Select accent:", 
                                            {"1": "English", "2": "Tagalog", "3": "Neutral"}, "3")
    accent_map = {"1": "english", "2": "tagalog", "3": "neutral"}
    accent_choice = accent_map.get(accent_choice, "neutral")
    print(f"{Fore.GREEN}✓ Selected accent: {Fore.WHITE}{Style.BRIGHT}{accent_choice.capitalize()}")
    
    # Duration selection
    duration_choice = generator.get_menu_choice("Select podcast duration:", 
                                              {"1": "Short (2-3 minutes)", 
                                               "2": "Medium (4-5 minutes)"}, "1")
    duration_map = {"1": 3, "2": 5}
    duration_minutes = duration_map.get(duration_choice, 3)
    print(f"{Fore.GREEN}✓ Selected duration: {Fore.WHITE}{Style.BRIGHT}{duration_minutes} minutes")
    print(f"{Fore.YELLOW}Note: Actual audio duration may vary slightly from the target length.")
    
    while True:
        print(f"\n{Fore.WHITE}{Back.BLUE} PODCAST GENERATION {Back.RESET}")
        topic = generator.get_user_input("\nEnter a podcast topic (or 'quit' to exit)")
        
        if topic.lower() in ['quit', 'exit', 'q', '']:
            print(f"{Fore.CYAN}Exiting the Advanced Podcast Generator. Goodbye!")
            break
            
        print(f"\n{Fore.YELLOW}Generating podcast script in {language_choice.capitalize()} with {accent_choice.capitalize()} accent...")
        try:
            script = generator.generate_podcast_script(topic, speaker1_name, speaker2_name, 
                                                     language_choice, duration_minutes)
            
            # Check if the script contains an error message
            if script.startswith(f"{Fore.RED}Error:"):
                print(f"{script}")
                print(f"{Fore.YELLOW}Please try again with a different topic.")
                continue
                
            print(f"\n{Fore.WHITE}{Back.BLUE} GENERATED SCRIPT {Back.RESET}")
            # Print script with alternating colors for speakers
            for line in script.split('\n'):
                if f"{speaker1_name}:" in line:
                    print(f"{Fore.CYAN}{line}")
                elif f"{speaker2_name}:" in line:
                    print(f"{Fore.GREEN}{line}")
                else:
                    print(f"{Fore.WHITE}{line}")
            print(f"{Fore.WHITE}{Back.BLUE} END OF SCRIPT {Back.RESET}\n")
                
            proceed = generator.get_user_input("Generate audio for this script? (y/n)", "y")
            if proceed.lower() == 'y':
                audio_path, script_path = await generator.generate_podcast_audio(
                    script, topic, speaker1_name, speaker2_name, accent_choice, voice1, voice2
                )
                
                # Offer to play the audio - adapted for different platforms including Termux
                play_audio = generator.get_user_input("Would you like to play the audio now? (y/n)", "n")
                if play_audio.lower() == 'y':
                    try:
                        if sys.platform == "win32":
                            os.system(f'start {audio_path}')
                        elif sys.platform == "darwin":  # macOS
                            os.system(f'open {audio_path}')
                        elif "TERMUX_VERSION" in os.environ:  # Detect Termux
                            os.system(f'termux-media-player play {audio_path}')
                        else:  # Linux and other Unix-like
                            os.system(f'xdg-open {audio_path}')
                        print(f"{Fore.GREEN}✓ Audio playback started in your default media player.")
                    except Exception as e:
                        print(f"{Fore.RED}Could not play audio: {str(e)}")
                        print(f"{Fore.YELLOW}Please play the file manually: {audio_path}")
            
        except Exception as e:
            print(f"{Fore.RED}An error occurred: {str(e)}")
        
        print(f"\n{Fore.CYAN}{'=' * 30}\n")

def print_install_instructions():
    """Print installation instructions for Termux."""
    print(f"\n{Fore.WHITE}{Back.BLUE}===== INSTALLATION INSTRUCTIONS FOR TERMUX ====={Back.RESET}\n")
    print(f"{Fore.CYAN}1. Make sure you have the following packages installed:")
    print(f"{Fore.YELLOW}   pkg install python python-pip git termux-api")
    print(f"\n{Fore.CYAN}2. Install the required Python packages:")
    print(f"{Fore.YELLOW}   pip install google-genai aiohttp pydub tqdm colorama")
    print(f"\n{Fore.CYAN}3. Run the app:")
    print(f"{Fore.YELLOW}   python app.py")
    print(f"\n{Fore.CYAN}Note: For audio playback in Termux, install the Termux:API package from the Play Store")
    print(f"{Fore.CYAN}      and run 'pkg install termux-api' to enable audio playback functionality.")
    print(f"\n{Fore.CYAN}To update the app, run: {Fore.YELLOW}git pull\n")

if __name__ == "__main__":
    # Check if help or install arguments were provided
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'install']:
        print_install_instructions()
    else:
        if sys.platform == "win32":
            # Set event loop policy for Windows
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Run the main function using asyncio
        asyncio.run(main())
