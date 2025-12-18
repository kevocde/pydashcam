import av
from datetime import datetime
from collections import deque

from common.utils import get_arg
from collision_detector import CollisionDetector

# Stream props
BUFFER_SIZE = 60 # In seconds
STREAM_PROPS = {
    "url": get_arg("stream"),
    "codec": "libx264",
    "rate": 30,
    "dimensions": {
        "width": 1920,
        "height": 1080,
    },
}
in_container = av.open(STREAM_PROPS["url"], options={"rtsp_transport": "tcp"})
in_stream = in_container.streams.video[0]
buffer = deque(maxlen=STREAM_PROPS["rate"] * BUFFER_SIZE)
frames = 0

def save_in_file(buffer, pos_buffer, stream, time):
    print("Collision Detected, saving evidence.")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"output/dashcam_{timestamp}.mkv"

    out_container = av.open(filename, mode="w")
    out_stream = out_container.add_stream_from_template(stream)

    try:
        found_kframe = False
        for packet in buffer:
            if packet.pts is None or packet.dts is None: continue
            if found_kframe or packet.is_keyframe:
                found_kframe = True
                packet.stream = out_stream
                out_container.mux(packet)

        for packet in pos_buffer:
            if packet.pts is None or packet.dts is None: continue
            packet.stream = out_stream
            out_container.mux(packet)
    except Exception:
        print("Error in packet ...")
    finally:
        out_container.close()

collision_detector = CollisionDetector(int(STREAM_PROPS["rate"]), 30, 30, save_in_file)

try:
    print("Trying to connect ...")
    for packet in in_container.demux(in_stream):
        if packet.dts is None: continue

        buffer.append(packet)
        frames += 1

        collision_detector.handle(buffer, in_stream)

        if frames % 30 == 0:
            print(f"Buffering ... {frames / 30} seconds")

except KeyboardInterrupt:
    pass
finally:
    in_container.close()
    print("Buffering stopped")
