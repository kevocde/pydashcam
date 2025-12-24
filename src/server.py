import av
from datetime import datetime
from collections import deque
from common.utils import get_arg
from collision_detector import CollisionDetector

# def save_in_file(buffer, pos_buffer, stream, time):
#     print("Collision Detected, saving evidence.")
#     timestamp = time.strftime("%Y%m%d_%H%M%S")
#     filename = f"output/dashcam_{timestamp}.mkv"
#     out_container = av.open(filename, mode="w")
#     out_stream = out_container.add_stream_from_template(stream)
#     all_frames = list(buffer) + list(pos_buffer)
#     found_kframe = False
#
#     try:
#         for packet in all_frames[:-2]:
#             if packet.is_corrupt:
#                 continue
#             else:
#                 if found_kframe or packet.is_keyframe:
#                     found_kframe = True
#                     packet.stream = out_stream
#                     out_container.mux(packet)
#     except Exception:
#         pass
#     finally:
#         out_container.close()

#collision_detector = CollisionDetector(int(STREAM_PROPS["rate"]), 30, 30, save_in_file)

def start(stream_url: str, buffer_duration: int = 60, handlers: dict = {}):
    container = av.open(stream_url, options={"rtsp_transport": "tcp"})
    stream = container.streams.video[0]
    rate = int(stream.base_rate)
    buffer = deque(maxlen=(buffer_duration * rate))
    frames = 0

    try:
        print("Monitoring ...")
        for packet in container.demux(stream):
            if packet.is_corrupt:
                continue

            buffer.append(packet)
            frames += 1

            for value in handlers.values():
                value.handle(stream, buffer)

            if frames % rate == 0:
                print(str((frames / rate)) + " secs")

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        for value in handlers.values():
            value.destroy()

        container.close()

if __name__ == "__main__":
    start(
        get_arg("stream"),
        60,
        {
            "collision": CollisionDetector()
        }
    )