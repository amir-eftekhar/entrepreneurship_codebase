from pydub import AudioSegment
from pydub.generators import Sine
import pygame

def generate_sine_wave(frequency, duration):
    # Generate a sine wave audio segment
    tone = Sine(frequency)
    audio = tone.to_audio_segment(duration=duration)
    return audio

def save_audio(audio, filename):
    # Export audio file
    audio.export(filename, format="wav")

def play_audio(filename):
    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        continue

# Generate a 440 Hz sine wave for 3 seconds
frequency = 440  # Frequency in Hz
duration = 3000  # Duration in milliseconds
audio = generate_sine_wave(frequency, duration)

# Save the audio
filename = 'test_tone.wav'
save_audio(audio, filename)

# Play the audio
print("Playing sound...")
play_audio(filename)
