import time

class Timer:
    def __init__(self):
        self.start_time = None

    def measure(self, start=True):
        if start:
            self.start_time = time.perf_counter()
        else:
            if self.start_time is None:
                raise ValueError("Timer has not been started. Call with start=True first.")
            elapsed_time = time.perf_counter() - self.start_time
            self.start_time = None  # Reset the timer
            return elapsed_time