from datetime import datetime
from collections import deque
import cv2, os

# Streaming service config
url = "https://192.168.1.10:8080/video"
cap = cv2.VideoCapture(url)

# Recording configurations
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

# Video properties
fps = 30
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

segment_duration = 5
max_segments = 5

def create_new_segment():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"output/dashcam_{timestamp}.mp4"
    writer = cv2.VideoWriter(file_path, fourcc, fps, (width, height))
    return file_path, writer

video_files = deque(maxlen=max_segments)
current_file, current_writer = create_new_segment()
video_files.append(current_file)

frame_count = 0
frames_per_segment = segment_duration * fps

print(f"Recording the video in {current_file}...")
try:
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Reconnecting ...")
            cap.release()
            cap.cv2.VideoCapture(url)
            break

        current_writer.write(frame)
        frame_count += 1

        if frame_count >= frames_per_segment:
            print(f"Segment completed: {current_file}")
            current_writer.release()

            current_file, current_writer = create_new_segment()
            video_files.append(current_file)
            frame_count = 0

            if len(video_files) > max_segments:
                old_file = video_files.popleft()

                if os.path.exists(old_file):
                    os.remove(old_file)
                    print(f"Deleted {old_file}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Stoping dashcam service ...")

finally:
    current_writer.release()
    cap.release()
    cv2.destroyAllWindows()
    print("Dashcam service stoped")
