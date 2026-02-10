import gradio as gr
import numpy as np
import cv2
import threading
import time
import random
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Medical Device Simulator
class MedicalDeviceSimulator:
    def __init__(self):
        self.running = False
        self.data_callback = None
        self.data_history = []
        self.max_history = 100  # Keep last 100 data points

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
            self.data_history.append(data)
            if len(self.data_history) > self.max_history:
                self.data_history.pop(0)

            if self.data_callback:
                self.data_callback(data)
            time.sleep(1)

    def get_plot(self):
        """Generate a plot of the historical data."""
        if not self.data_history:
            return go.Figure()

        fig = make_subplots(rows=3, cols=1, subplot_titles=("Heart Rate", "Blood Pressure", "SpO2"))

        # Heart Rate
        timestamps = [d["timestamp"] for d in self.data_history]
        heart_rates = [d["heart_rate"] for d in self.data_history]
        fig.add_trace(go.Scatter(x=timestamps, y=heart_rates, name="Heart Rate"), row=1, col=1)

        # Blood Pressure (systolic)
        bp_systolic = [int(d["blood_pressure"].split("/")[0]) for d in self.data_history]
        fig.add_trace(go.Scatter(x=timestamps, y=bp_systolic, name="Systolic"), row=2, col=1)

        # SpO2
        spo2 = [d["spo2"] for d in self.data_history]
        fig.add_trace(go.Scatter(x=timestamps, y=spo2, name="SpO2"), row=3, col=1)

        fig.update_layout(height=800, showlegend=True)
        return fig

# Image Transformation Function
def transform_cv2(frame, transform):
    if transform == "cartoon":
        img_color = cv2.pyrDown(cv2.pyrDown(frame))
        for _ in range(6):
            img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
        img_color = cv2.pyrUp(cv2.pyrUp(img_color))

        img_edges = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        img_edges = cv2.adaptiveThreshold(
            cv2.medianBlur(img_edges, 7),
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            2,
        )
        img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)
        img = cv2.bitwise_and(img_color, img_edges)
        return img
    elif transform == "edges":
        img = cv2.cvtColor(cv2.Canny(frame, 100, 200), cv2.COLOR_GRAY2BGR)
        return img
    else:
        return np.flipud(frame)

# Create the simulator instance
simulator = MedicalDeviceSimulator()

# Gradio Interface
with gr.Blocks() as app:
    with gr.Row():
        with gr.Column():
            # Image Processing Section
            transform = gr.Dropdown(
                choices=["cartoon", "edges", "flip"],
                value="flip",
                label="Image Transformation",
            )
            input_img = gr.Image(sources=["webcam"], type="numpy")
            output_img = gr.Image(streaming=True)

            # Medical Device Section
            with gr.Accordion("Medical Device Data", open=True):
                start_stop_btn = gr.Button("Start Data Stream")
                data_plot = gr.Plot(label="Medical Device Data")
                data_log = gr.Textbox(label="Data Log", lines=5)

                # Control the data stream
                def start_stream():
                    simulator.start()
                    return "Data stream started"

                def stop_stream():
                    simulator.stop()
                    return "Data stream stopped"

                start_stop_btn.click(
                    lambda: start_stream(),
                    outputs=data_log
                ).then(
                    fn=lambda: None,  # Just to keep the button click chain
                    outputs=[]
                )

                # Update the plot periodically
                def update_plot():
                    return simulator.get_plot()

                # Create a timer component
                timer = gr.Timer(1.0)

                # Connect the timer to the update_plot function
                timer.trigger(
                    fn=update_plot,
                    outputs=data_plot
                )

    # Image processing stream
    dep = input_img.stream(
        transform_cv2,
        [input_img, transform],
        [output_img],
        time_limit=30,
        stream_every=0.1,
        concurrency_limit=30,
    )

app.launch()