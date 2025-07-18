# 2D: Application and Visualization of 3D Fourier Transform for GIF Files

This semester project focuses on applying and visualizing the 3D Fourier Transform for GIF-format files. It computes the amplitude, phase, and power spectra.

[![Watch the video](https://img.youtube.com/vi/hQY2kOMyiOw/0.jpg)](https://www.youtube.com/watch?v=hQY2kOMyiOw)

## User Documentation

The plugin is written in Python and is designed for the Krita application.

### How to Use:

1. Place the plugin files into the `pykrita` plugin folder in Krita.
2. Restart Krita and enable the plugin named **"fft"** in the Python Plugin Manager.
3. Open the menu: **Tools > Scripts > FFT GIF**.
4. Select the GIF file you want to process. It's recommended to use GIFs with fewer frames for faster processing.
5. The plugin loads each frame of the GIF, performs a 2D Fourier Transform on each one, and displays the results (amplitude, phase, and power spectra) as separate layers in the Krita document.
6. After processing, you will be prompted to optionally save the results as separate GIFs for each spectrum.

## Theoretical Documentation

Fourier Transform is a mathematical method for decomposing a signal into its frequency components.  
In this case, a 3D FT is applied by processing each frame of the GIF with a 2D FT, treating the frame sequence as the third dimension.

The FT decomposes the image into frequency components:

- **Amplitude Spectrum**:  
  - Shows which frequencies dominate in the image—whether it's rich in details (high frequencies) or has large uniform areas (low frequencies).
  - Low frequencies are centered in the image; high frequencies are toward the edges.
  - Useful for texture analysis or identifying repeating patterns.

- **Phase Spectrum**:  
  - Represents the phase shift of individual frequencies—i.e., where the frequency components are located in the image.
  - Hard to interpret visually as the values range from -π to π.
  - Like the amplitude spectrum, low-frequency phases are in the center, high-frequency near the edges.
  - Crucial for reconstructing the original signal or image.

- **Power Spectrum**:  
  - Indicates the intensity or energy of individual frequencies in the image.
  - Visually similar to the amplitude spectrum but with higher contrast.
  - Highest values (energy) appear in the center, with lower values toward the edges.

### FT Computation

- **`fft_result = np.fft.fft2(frame)`**  
  - `frame`: Grayscale frame of the GIF.  
  - Applies a 2D discrete FT. Low frequencies are initially on the edges.

- **`fft_shifted = np.fft.fftshift(fft_result)`**  
  - Re-centers low frequencies to the middle of the frame.

### Computing Amplitude, Phase, and Power Spectra

- **Amplitude**:  
  - `magnitude = np.log(np.abs(fft_result) + 1)`  
  - Calculates the absolute value and applies a logarithm to enhance lower frequencies' visibility. Adding 1 avoids log(0).

- **Phase**:  
  - `phase = np.angle(fft_result)`  
  - Computes the phase angle of complex numbers.

- **Power**:  
  - `power = magnitude ** 2`  
  - Squares the amplitude to emphasize differences between high and low frequencies.

### Spectrum Normalization

- `255 * (data / np.max(data)).np.uint8`  
  - Scales spectrum values between 0–255 and converts them to integers for image display.

## Developer Documentation

The plugin is written in Python and uses the following libraries:
- `krita`: To interact with Krita's document and layer system.
- `numpy`: For numerical computations and FFT.
- `Pillow`: For image processing.
- `PyQt5`: For user interaction (dialogs, confirmations, etc.).

### Plugin Workflow

**1. Plugin Activation**
- Activated via **Tools -> Scripts -> FFT GIF**
- Calls the `get_fft_gifs()` method which controls the main logic.

**2. GIF File Selection**
- A dialog prompts the user to choose a GIF file.
- If a file is selected:
  - It's split into individual frames and converted to grayscale.
  - If the file has no frames, an error message is shown: *"Failed to load GIF frames."*
- If no file is selected:
  - Error message: *"Didn't select a GIF file"*
  - Plugin terminates.

**3. Fourier Transform Calculation**
For each frame:
1. **FFT**:  
   - `apply_fft(frame)` performs a 2D FFT.
2. **Spectrum Calculation**:  
   - `get_spectrum(fft_result)` calculates and normalizes amplitude, phase, and power spectra.
3. **Storing Results**:  
   - Results are stored in `magnitude_frames`, `phase_frames`, and `power_frames`.

**4. Displaying Results in Krita**
- Uses `show_results_in_krita()` to show original frames and their spectra as layers in the active document.
- If no active document exists, shows: *"No active document"*, clears memory, and exits.
- Creates layer groups: `Original grayscale`, `Magnitude`, `Phase`, `Power`.
- Each frame is added to its corresponding group.

**5. Saving Results**
- User is prompted: *"Do you want to save the generated spectrum GIFs?"*

- If **Yes**:
  - Asks for save path.
  - Saves three separate GIFs:
    - **Amplitude Spectrum**
    - **Phase Spectrum**
    - **Power Spectrum**
  - If no path is selected: *"No path selected."*

- If **No**:
  - Proceeds to memory cleanup and exits.

**6. Memory Cleanup**
- Temporary frames are removed using `clear_all_frames()`.

## Sources

The following sources were used during the project:

- **BI-PGA Lecture Slides**: Provided the theoretical foundation on Fourier Transform and its applications.  
- **Krita Documentation**: Helped with understanding the plugin API, layers, and Python integration.  
- **ChatGPT Inquiries**: Used to explain complex parts of the code, structure the plugin, and clarify mathematical operations related to the Fourier Transform.
