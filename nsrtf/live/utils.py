import time

class CountsPerSec:
    """
    Class that tracks the number of occurrences ("counts") of an
    arbitrary event and returns the frequency in occurrences
    (counts) per second. The caller must increment the count.
    """

    def __init__(self):
        self._start_time = None
        self.full_counter = 0
        self.tick_counter = 0
        self._tick_secs = 1

    def start(self):
        self._start_time = time.time()
        return self

    def increment(self):
        self.full_counter += 1
        self.tick_counter += 1

    def countsPerSec(self):
        elapsed_time = time.time() - self._start_time
        fps = self.tick_counter / elapsed_time
        if elapsed_time > self._tick_secs:
            self._start_time = time.time()
            self.tick_counter = 0
        
        return fps
