from datetime import datetime
from collections import deque
import subprocess
import json
import random

class CollisionDetector:

    def __init__(self, fps: int = 30, pre_collision_time: int = 30, pos_collision_time: int = 30, saver = None):
        self.__fps = fps
        self.__pre_time = pre_collision_time
        self.__pos_time = pos_collision_time
        self.__collision = False
        self.__buffer = deque(maxlen=(fps * pre_collision_time))
        self.__pos_buffer = deque(maxlen=(fps * pos_collision_time))
        self.__saver = saver


    def handle(self, buffer, stream):
        if self.__collision:
            self.__collision = False
            self.__store_pre_buffer(buffer)

        if len(self.__buffer) > 0:
            self.__pos_buffer.append(buffer.pop())
            if len(self.__pos_buffer) >= (self.__fps * self.__pos_time):
                self.__save_as_file(stream)
                self.__buffer = deque(maxlen=(self.__fps * self.__pre_time))
                self.__pos_buffer = deque(maxlen=(self.__fps * self.__pos_time))

        self.__collision = self.__detect_collision()


    def __store_pre_buffer(self, buffer):
        initial_frame = len(buffer) - (self.__fps * self.__pre_time)
        self.__buffer = deque(list(buffer.copy())[initial_frame:])


    def __save_as_file(self, stream):
        if self.__saver:
            self.__saver(self.__buffer, self.__pos_buffer, stream, datetime.now())


    def __detect_collision(self):
        try:
            #result = subprocess.run(["termux-sensor", "-s", "gravity", "-n", "1"], capture_output=True, text=True)
            #data = json.loads(result.stdout)
            random_integer = random.randint(1, 500)
            return (random_integer == 99)
        except Exception:
            return False