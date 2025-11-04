import cv2
import pyaudio
import wave
import time
import os
import subprocess
import keyboard

TEMP_VIDEO_FILE = "temp_video.avi"
TEMP_AUDIO_FILE = "temp_audio.wav"
FINAL_OUTPUT_FILE = "environment_record_FINAL.mp4"

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 20.0
VIDEO_FOURCC = cv2.VideoWriter_fourcc(*'XVID')

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def record_video_audio():
    """Records video and audio simultaneously in sync."""
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)
    audio_frames = []

    # Initialize video capture
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    out = cv2.VideoWriter(TEMP_VIDEO_FILE, VIDEO_FOURCC, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

    if not cap.isOpened():
        print("❌ Camera could not be opened.")
        return

    print("🎥 Video and 🎙️ Audio recording started. (Press Q to stop)")

    start_time = time.time()
    frames_recorded = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Write video frame
        out.write(frame)
        cv2.imshow("Camera Recording - Q = Exit", frame)

        # Capture audio
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_frames.append(data)

        frames_recorded += 1

        # Exit with Q or ESC
        if keyboard.is_pressed('q') or cv2.waitKey(1) == 27:
            break

        # Synchronization delay for FPS
        elapsed = time.time() - start_time
        target_time = frames_recorded * (1 / FPS)
        time.sleep(max(0, target_time - elapsed))

    # Cleanup
    cap.release()
    out.release()
    stream.stop_stream()
    stream.close()
    p.terminate()
    cv2.destroyAllWindows()

    # Save audio recording to file
    with wave.open(TEMP_AUDIO_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(audio_frames))

    print("✅ Video and audio recording completed.")

def combine_audio_video_with_ffmpeg():
    print("🔗 Merging audio and video...")
    command = [
        r"C:\ffmpeg\bin\ffmpeg.exe", "-y",
        "-i", TEMP_VIDEO_FILE,
        "-i", TEMP_AUDIO_FILE,
        "-c:v", "libx264",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        FINAL_OUTPUT_FILE
    ]
    try:
        subprocess.run(command, check=True)
        print(f"✅ Merging completed: {os.path.abspath(FINAL_OUTPUT_FILE)}")
    except Exception as e:
        print(f"❌ FFmpeg error: {e}")
    finally:
        for f in [TEMP_VIDEO_FILE, TEMP_AUDIO_FILE]:
            if os.path.exists(f):
                os.remove(f)
        print("🗑️ Temporary files deleted.")

if __name__ == "__main__":
    record_video_audio()
    combine_audio_video_with_ffmpeg()
    print("\n--- Program Terminated ---")
