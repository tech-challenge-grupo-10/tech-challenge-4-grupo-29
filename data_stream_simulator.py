import threading
import time
import random
import json

class MedicalDeviceSimulator:
    def __init__(self):
        self.running = False
        self.data_callback = None

    def start(self):
        """Start the data stream in a background thread."""
        self.running = True
        self.thread = threading.Thread(target=self._generate_data, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the data stream."""
        self.running = False
        self.thread.join()

    def _generate_data(self):
        """Internal method to generate and emit data."""
        while self.running:
            data = {
                "timestamp": time.time(),
                "heart_rate": random.randint(60, 100),
                "blood_pressure": f"{random.randint(90, 140)}/{random.randint(60, 90)}",
                "spo2": random.randint(95, 100)
            }
            if self.data_callback:
                self.data_callback(data)
            time.sleep(1)

    def set_callback(self, callback):
        """Set a callback function to receive data."""
        self.data_callback = callback

# Example usage:
def handle_data(data):
    print(f"Received: {json.dumps(data)}")

simulator = MedicalDeviceSimulator()
simulator.set_callback(handle_data)
simulator.start()

# Let it run for 10 seconds
time.sleep(100)
simulator.stop()