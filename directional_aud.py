from pydub import AudioSegment
from pydub.playback import play

def create_directional_audio(file_path):
    # Load the audio file
    sound = AudioSegment.from_file(file_path, format="wav")
    
    # Make sure the file is stereo
    if sound.channels != 2:
        sound = sound.set_channels(2)

    # Get frame rate
    frame_rate = sound.frame_rate

    # Duration of the sound in milliseconds
    duration_ms = len(sound)
    
    # Create a silent segment and set it to stereo
    silent_segment = AudioSegment.silent(duration=duration_ms, frame_rate=frame_rate)
    silent_segment = silent_segment.set_channels(2)  # Make the silent segment stereo

    # Create a pan effect from left to right
    sound_effect = silent_segment
    
    # Number of steps to move from left to right
    steps = 100
    for i in range(steps):
        # Calculate pan (from -1.0 to 1.0)
        pan = i / (steps - 1) * 2 - 1
        
        # Create a short segment with current pan
        segment = sound[i * (duration_ms // steps):(i + 1) * (duration_ms // steps)]
        segment = segment.pan(pan)
        
        # Append segment to the effect track
        sound_effect = sound_effect.overlay(segment, position=i * (duration_ms // steps))

    return sound_effect
def create_front_back_audio(file_path):
    sound = AudioSegment.from_file(file_path, format="wav")
    if sound.channels != 2:
        sound = sound.set_channels(2)

    segment_duration = len(sound) // 2  # Half for moving 'front', half for 'back'
    front = sound[:segment_duration].fade_out(segment_duration)  # Gradually decrease volume
    back = sound[segment_duration:].fade_in(segment_duration)  # Gradually increase volume

    return front + back  # Combine the two halves

def create_circular_audio(file_path):
    sound = AudioSegment.from_file(file_path, format="wav")
    if sound.channels != 2:
        sound = sound.set_channels(2)

    steps = 100
    circular_sound = AudioSegment.silent(duration=len(sound), frame_rate=sound.frame_rate, channels=2)
    
    # Full circle motion
    for i in range(steps):
        angle = 2 * np.pi * i / steps  # Angle in radians
        pan = np.sin(angle)  # Pan based on sine wave for circular motion
        segment = sound[i * (len(sound) // steps):(i + 1) * (len(sound) // steps)]
        segment = segment.pan(pan)
        circular_sound = circular_sound.overlay(segment, position=i * (len(sound) // steps))

    return circular_sound


# Path to your audio file
file_path = 'test_tone.wav'

front_back_sound = create_front_back_audio(file_path)
play(front_back_sound)
# Create directional audio
directional_sound = create_directional_audio(file_path)

# Play the audio
play(directional_sound)
