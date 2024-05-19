from pydub import AudioSegment
from pydub.generators import Sine
import pygame
import numpy as np

def generate_sine_wave(frequency, duration, volume):
    """Generate a sine wave audio segment."""
    tone = Sine(frequency)
    audio = tone.to_audio_segment(duration=duration)
    audio = audio - (1 - volume) * 20  # Adjust volume
    return audio

def save_audio(audio, filename):
    """Export audio file."""
    audio.export(filename, format="wav")

def play_audio(filename):
    """Play the audio using pygame."""
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        continue

def create_transition_sound(frequency, total_duration, transition_steps, variations):
    """Create a sound that transitions from loud to quiet and back."""
    segment_duration = total_duration // transition_steps
    sound = AudioSegment.silent(duration=0)
    
    for i in range(variations):
        # Loud to quiet
        for volume in np.linspace(1.0, 0.0, transition_steps):
            segment = generate_sine_wave(frequency, segment_duration, volume)
            sound += segment
        
        # Quiet to loud
        for volume in np.linspace(0.0, 1.0, transition_steps):
            segment = generate_sine_wave(frequency, segment_duration, volume)
            sound += segment
    
    return sound

def main():
    frequency = 440  # Frequency in Hz
    total_duration = 3000  # Total duration of one transition in milliseconds
    transition_steps = 50  # Number of steps in the transition
    variations = 5  # Number of variations (loud-quiet-loud cycles)

    audio = create_transition_sound(frequency, total_duration, transition_steps, variations)
    filename = 'transition_tone.wav'
    save_audio(audio, filename)
    
    # Play the audio
    print("Playing sound...")
    play_audio(filename)

if __name__ == "__main__":
    main()
