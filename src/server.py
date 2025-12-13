from datetime import datetime
from collections import deque
import cv2, os

# Recording config
FPS = 30
BUFFER_SIZE = 60 * 5 # Seconds
PRE_COLLISION_TIME = 30 # Seconds
POS_COLLISION_TIME = 60 # Seconds

# Streaming service
streaming_url = "https://192.168.1.10:8080/video"
cap = cv2.VideoCapture(streaming_url)
frame_counter = 0

# Streaming properties
streaming = {
    "fourcc": cv2.VideoWriter_fourcc(*"mp4v"),
    "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
    "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
}

# Local properties
buffer = deque(maxlen=(FPS * BUFFER_SIZE))

def save_collision_video(pre_buffer, buffer, time):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"output/dashcam_{timestamp}.mp4"
    out = cv2.VideoWriter(
        filename,
        streaming["fourcc"],
        FPS,
        (streaming["width"], streaming["height"])
    )

    for frame in pre_buffer:
        out.write(frame)

    for frame in buffer:
        out.write(frame)

    out.release()

from collision_detector import CollisionDetector

collision_detector = CollisionDetector(FPS, PRE_COLLISION_TIME, POS_COLLISION_TIME, save_collision_video)

# Process
try:
    print("Server started")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Reconnecting ...")
            cap.release()
            cap.cv2.VideoCapture(streaming_url)
            continue

        collision_detector.handle(buffer)


        #collision, collision_buffer, collision_frame, collision_time = collision_detector(realtime_buffer, collision, collision_buffer, collision_frame, collision_time)

        #if collision:
        #    pre_buffer = realtime_buffer.copy()
        #    realtime_buffer.clear()
        #    collision = False
        #
        #if len(pre_buffer) > 0:
        #    if len(realtime_buffer) >= (POS_COLLISION_TIME * FPS):
        #        save_collision_video(pre_buffer, realtime_buffer, datetime.now())
        #        break
        if len(buffer) >= (FPS * BUFFER_SIZE):
            buffer.popleft()
        else:
            buffer.append(frame.copy())

        frame_counter += 1

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()