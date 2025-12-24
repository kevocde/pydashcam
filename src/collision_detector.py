from datetime import datetime
from collections import deque
from datetime import datetime
import subprocess
import json
import multiprocessing
import math
import av

class CollisionDetector:

    FILE_PREFIX = "collision_"
    GRAVITY = 9.806
    THRESHOLD = 40.0

    def __init__(self, duration: int = 60):
        self.__initalized = False
        self.__duration = duration
        self.__collision = False


    def handle(self, stream, buffer):
        self.__initialize(stream)
        if not self.__sensors.empty():
            acc = math.sqrt(sum([value**2 for value in self.__sensors.get()["gravity"]["values"]]))
            print("G-Force: " + str((acc / self.GRAVITY)))
            if acc > self.THRESHOLD:
                self.__collision = True

        if self.__collision:
            self.__collision = False
            self.__copy_buffer(buffer)

        if len(self.__buffer) > 0:
            self.__posbuffer.append(buffer.pop())
            if len(self.__posbuffer) >= int((self.__duration / 2) * self.__rate):
                self.__save_clip()
                self.__buffer = deque(maxlen=int((self.__duration / 2) * self.__rate))
                self.__posbuffer = self.__buffer.copy()


    def __initialize(self, stream):
        if not self.__initalized:
            self.__initalized = True
            self.__rate = int(stream.base_rate)
            self.__buffer = deque(maxlen=int((self.__duration / 2) * self.__rate))
            self.__posbuffer = self.__buffer.copy()
            self.__sensors = multiprocessing.Manager().Queue()
            self.__event = multiprocessing.Event()
            self.__process = multiprocessing.Process(
                target=self.read_sensors,
                args=(self.__event,)
            )
            self.__process.start()


    def __copy_buffer(self, buffer):
        kframe_idx = int(len(buffer) - ((self.__duration / 2) * self.__rate))
        self.__buffer = deque(list(buffer.copy())[kframe_idx:])


    def __save_clip(self, stream):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/{self.FILE_PREFIX}_{timestamp}.mkv"
        out_container = av.open(filename, mode="w")
        out_stream = out_container.add_stream_from_template(stream)
        all_frames = list(self.__buffer) + list(self.__posbuffer)
        found_kframe = False

        try:
            for packet in all_frames[:-2]:
                if packet.is_corrupt:
                    continue
                else:
                    if found_kframe or packet.is_keyframe:
                        found_kframe = True
                        packet.stream = out_stream
                        out_container.mux(packet)
        except Exception:
            pass
        finally:
            out_container.close()


    def read_sensors(self, stop_event):
        try:
            while not stop_event.is_set():
                result = subprocess.run(["./src/sensor.sh"], capture_output=True, text=True)
                if self.__sensors.full():
                    self.__sensors.get()

                self.__sensors.put(json.loads(result.stdout))
        except KeyboardInterrupt:
            pass


    def destroy(self):
        self.__event.set()
        self.__process.join()