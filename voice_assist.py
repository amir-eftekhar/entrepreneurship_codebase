import pvporcupine
import pvrhino
import pyaudio

def main():
    # Initialize Porcupine (wake word engine)
    porcupine = pvporcupine.create(keywords=["hey halo"])
    
    rhino = pvrhino.create(context_path="/path/to/your/context/file.rhn")

    # Set up audio input
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = [int(x) for x in pcm]
            
            if porcupine.process(pcm):
                print("Wake word detected!")
                
                # Rhino processes the command after the wake word
                while True:
                    pcm = audio_stream.read(rhino.frame_length)
                    pcm = [int(x) for x in pcm]
                    is_finalized = rhino.process(pcm)
                    if is_finalized:
                        inference = rhino.get_inference()
                        if inference.is_understood:
                            print(f"Intent: {inference.intent}")
                            print(f"Slots: {inference.slots}")
                            break
                        else:
                            print("Did not understand the command.")
                            break

    finally:
        audio_stream.close()
        pa.terminate()
        porcupine.delete()
        rhino.delete()

if __name__ == "__main__":
    main()
