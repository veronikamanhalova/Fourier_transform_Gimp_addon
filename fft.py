from krita import *
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PIL import Image

# Normalize data to a 0-255 scale
def normalize_spectrum(data):
    return (255 * (data / np.max(data))).astype(np.uint8)

# Convert numpy array data into a grayscale image
def data_to_frame(data):
    return Image.fromarray(data, mode="L")

# Extract magnitude, phase, and power spectrum from FFT result
def get_spectrum(fft_result):
    magnitude = np.log(np.abs(fft_result) + 1)
    phase = np.angle(fft_result)
    power = magnitude ** 2

    return magnitude, phase, power

# Perform 2D FFT on a single frame and shift frequency components
def apply_fft(frame):
    fft_result = np.fft.fft2(frame)
    fft_shifted = np.fft.fftshift(fft_result)

    return fft_shifted

class FFTPlugin(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.document = None
        self.frame_duration = 100
        self.width = None
        self.height = None
        self.gif_frames, self.magnitude_frames, self.phase_frames, self.power_frames = [], [], [], []

    # Create an FFT GIF plugin action in Krita's menu
    def createActions(self, window):
        action = window.createAction("fft_gif", "FFT GIF", "tools/scripts")
        action.triggered.connect(self.get_fft_gifs)

    def setup(self):
        pass

    # Load GIF, apply FFT, save magnitude, phase and power spectrums as GIFs and clear all frame lists
    def get_fft_gifs(self):
        # Load gif file frames into array
        if not self.load_gif():
            return

        # Apply FFT 2D for each gif frame
        for frame in self.gif_frames:
            fft_result = apply_fft(frame)
            self.append_spectrum_frames(fft_result)

        # Display the generated GIFs as layers in Krita
        if not self.show_results_in_krita():
            self.clear_all_frames()
            return

        QMessageBox.information(None, "Success", "FFT GIF results generated!")

        # Ask user if they want to save the generated GIFs
        reply = QMessageBox.question(
            None,
            "Save FFT GIFs",
            "Do you want to save the generated spectrum GIFs?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            # Save results as GIFs
            if not self.save_fft_results():
                self.clear_all_frames()
                return
            QMessageBox.information(None, "Success", "FFT GIF results saved!")

        # Clear all temporary frames
        self.clear_all_frames()

    # Load frames from a GIF file
    def load_gif(self):
        # Prompt the user to select a GIF file
        gif_path, _ = QFileDialog.getOpenFileName(None, "Select a GIF File", "", "GIF Files (*.gif)")
        if not gif_path:
            QMessageBox.critical(None, "Error", "Didn't select a GIF file.")
            return false

        gif = Image.open(gif_path)
        if gif.format != "GIF":
            QMessageBox.critical(None, "Error", "Selected file is not a GIF file.")
            return false

        self.width, self.height = gif.size

        frames = []
        # Load each frame as grayscale image data array
        for frame in range(gif.n_frames):
            gif.seek(frame)
            frame_data = gif.convert("L")
            frames.append(np.array(frame_data))

        if not frames:
            QMessageBox.critical(None, "Error", "Failed to load GIF frames.")
            return false

        self.gif_frames = frames
        return True

    # Append magnitude, phase and power spectrum frames into related lists
    def append_spectrum_frames(self, fft_result):
        magnitude, phase, power = get_spectrum(fft_result)
        self.magnitude_frames.append(data_to_frame(normalize_spectrum(magnitude)))
        self.phase_frames.append(data_to_frame(normalize_spectrum(phase)))
        self.power_frames.append(data_to_frame(normalize_spectrum(power)))

    # Display the original grayscale GIF and generated GIFs as layers in active Krita document
    def show_results_in_krita(self):
        # Get the active Krita document
        self.document = Krita.instance().activeDocument()
        if not self.document:
            QMessageBox.critical(None, "Error", "No active document.")
            return False

        # Create groups for layers of GIF frames for each GIF
        gif_group, magnitude_group, phase_group, power_group = self.get_spectrum_groups()

        # Add frames to each group
        for frame_index in range(len(self.magnitude_frames)):
            self.add_frame_to_group(frame_index, gif_group, self.gif_frames[frame_index])
            self.add_frame_to_group(frame_index, magnitude_group, self.magnitude_frames[frame_index])
            self.add_frame_to_group(frame_index, phase_group, self.phase_frames[frame_index])
            self.add_frame_to_group(frame_index, power_group, self.power_frames[frame_index])

        return True

    # Save magnitude, phase and power spectrums as separate GIFs
    def save_fft_results(self):
        save_path, _ = QFileDialog.getSaveFileName(None, "Save GIF", "", "GIF Files (*.gif)")
        if not save_path:
            QMessageBox.critical(None, "Error", "No path selected.")
            return False

        self.save_gif(self.magnitude_frames, "magnitude", save_path)
        self.save_gif(self.phase_frames, "phase", save_path)
        self.save_gif(self.power_frames, "power", save_path)

        return True

    # Save a list of frames as a GIF
    def save_gif(self, frames, spectrum_name, save_path):
        frames[0].save(
            save_path.replace(".gif", f"_{spectrum_name}.gif"),
            save_all=True,
            append_images=frames[1:],
            duration=self.frame_duration,
            loop=0 # infinite loop
        )

    # Clear all frame lists
    def clear_all_frames(self):
        self.gif_frames.clear()
        self.magnitude_frames.clear()
        self.phase_frames.clear()
        self.power_frames.clear()

    # Create groups for GIF layers in the Krita document
    def get_spectrum_groups(self):
        gif_group = self.document.createNode("Original grayscale", "groupLayer")
        magnitude_group = self.document.createNode("Magnitude", "groupLayer")
        phase_group = self.document.createNode("Phase", "groupLayer")
        power_group = self.document.createNode("Power", "groupLayer")

        # Add the groups to the root of the document
        self.document.rootNode().addChildNode(gif_group, None)
        self.document.rootNode().addChildNode(magnitude_group, None)
        self.document.rootNode().addChildNode(phase_group, None)
        self.document.rootNode().addChildNode(power_group, None)

        return gif_group, magnitude_group, phase_group, power_group

    # Add a spectrum frame to the specified group in the Krita document
    def add_frame_to_group(self, frame_index, group, frame):
        # Create a new paint layer
        new_layer = self.document.createNode(f"Frame {frame_index + 1}", "paintlayer")
        group.addChildNode(new_layer, None)

        # Convert the spectrum frame to a bytearray
        byte_array = bytearray()
        for value in np.array(frame).astype(np.uint8).flatten():
            byte_array.extend([value, value, value, 255])  # Set R, G, B, A

        # Update layer pixel data
        new_layer.setPixelData(byte_array, 0, 0, self.width, self.height)

# Register the plugin with Krita
Krita.instance().addExtension(FFTPlugin(Krita.instance()))
