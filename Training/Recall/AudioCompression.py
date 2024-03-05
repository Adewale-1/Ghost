from pydub import AudioSegment


"""
    Bit Rate Reduction: Reducing the bit rate of the audio file is an effective way to compress it. 
    A lower bit rate generally means lower quality, but it can significantly reduce the file size.
    A bit rate of 96 kbps (kilobits per second) is often sufficient for spoken audio.

    Frame Rate Adjustment: While 44.1 kHz is standard for high-quality audio, for speech,
    a lower frame rate like 22.05 kHz or 32 kHz can be sufficient and will help reduce the file size.

    Mono Channel: If the audio is primarily speech, converting it to mono (single channel) instead
    of stereo (dual channel) can reduce the file size without significantly affecting the quality 
    of spoken words.

    Handling Different Input Formats: AudioSegment.from_file() method can handle various formats,
    making your script more flexible.
"""

input_file = "test_audio_file.mp3"
output_file = "compressed_audio_file.mp3"

try:
    # Load the audio file
    audio = AudioSegment.from_file(input_file)

    # Convert to mono, reduce frame rate and bit rate for compression
    compressed_audio = audio.set_frame_rate(22050).set_channels(1)
    compressed_audio.export(output_file, format="mp3", bitrate="96k")

    print(f"Compression successful. File saved as {output_file}")

except Exception as e:
    print(f"Error during compression: {e}")


