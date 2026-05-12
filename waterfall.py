import subprocess
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading


center_frequency = 5180  # mhz
samp_rate = 20 # 2-20 mhz (20 to maks)
fft_size = 8196
history_rows = 100


min_freguency = center_frequency - (samp_rate / 2)
max_frequency = center_frequency + (samp_rate / 2)

min_db = 10
max_db = 60


waterfall_data = np.full((history_rows, fft_size), min_db, dtype=float)
is_running = True
process = None


def read_hackrf_stream():
    global waterfall_data, is_running, process


    cmd = [
        r"D:\Radioconda\Library\bin\hackrf_transfer.exe",
        "-r", "-",
        "-f", str(int(center_frequency * 1_000_000)),
        "-s", str(int(samp_rate * 1_000_000)),
        "-a", "1",  # wzmacniacz
        "-l", "32",  # czułość LNA
        "-g", "40"  # czułość VGA
    ]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        CHUNK_BYTES = 1024 * 1024

        while is_running:
            raw_bytes = process.stdout.read(CHUNK_BYTES)

            if not raw_bytes:
                break

            needed_bytes = fft_size * 2
            if len(raw_bytes) >= needed_bytes:
                data = np.frombuffer(raw_bytes[:needed_bytes], dtype=np.int8)
                iq = data[0::2] + 1j * data[1::2]

                fft_result = np.fft.fftshift(np.fft.fft(iq))

                fft_mag = 10 * np.log10(np.abs(fft_result) + 1e-6)

                waterfall_data = np.roll(waterfall_data, 1, axis=0)
                waterfall_data[0, :] = fft_mag

    except Exception as e:
        print(f"\n read_hackrf_stream(): {e}")
    finally:
        if process:
            process.terminate()



def main():
    global is_running

    print(f"Main started, frequency: {center_frequency}")

    thread = threading.Thread(target=read_hackrf_stream)
    thread.daemon = True
    thread.start()

    fig, ax = plt.subplots(figsize=(10, 6))

    img = ax.imshow(waterfall_data, aspect='auto', cmap='jet',
                    vmin=min_db, vmax=max_db,
                    extent=[min_freguency, max_frequency, history_rows, 0])

    ax.set_title(f'Widmo 20 MHz  - Center: {center_frequency} MHz')

    cbar = fig.colorbar(img, ax=ax)
    cbar.set_label('Siła sygnału')

    def update(frame):
        img.set_array(waterfall_data)
        return [img]

    ani = animation.FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)

    try:
        plt.show(block=True)
    except KeyboardInterrupt:
        pass
    finally:
        is_running = False
        if process:
            process.terminate()
        print("\nZakończono")


if __name__ == "__main__":
    main()