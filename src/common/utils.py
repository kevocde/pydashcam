import argparse
from typing import Optional

def get_arg(name: str)-> Optional[str]:
    """Get an argument from the comman invoke."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--stream', help="The streaming URL", default="rtsp://192.168.1.10:8080/h264_aac.sdp")

    return parser.parse_args().__dict__[name] if name in parser.parse_args().__dict__ else None