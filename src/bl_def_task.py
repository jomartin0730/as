from queue import Queue
import datetime

class Bl_Def_Task():

    def __init__(self):
        self._task_Length = 0
        self.scheduled_Task = Queue()
        print("│ Task queue is ready                 │")

    def __del__(self):
        print("All task is deleted.")

    @property
    def task_Length(self):
        return self._task_Length

    @task_Length.setter
    def task_Length(self, value):
        self._task_Length = value

    def task_Queue_Size(self):
        length = self.scheduled_Task.qsize()
        return length
