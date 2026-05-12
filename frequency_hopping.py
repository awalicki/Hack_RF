import subprocess
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time


# target_frequencies = [5760, 2440]
target_frequencies = [876, 2440]
hop_interval = 1.0

samp_rate = 20  # 2-20 mhz (20 to maks)
fft_size = 8196
history_rows = 100

min_db = 10
max_db = 60

waterfall_data = np.full((history_rows, fft_size), min_db, dtype=float)
is_running = True

current_freq_mhz = target_frequencies[0]


def read_hackrf_stream():
    global waterfall_data, is_running, current_freq_mhz

    freq_index = 0

    while is_running:
        current_freq_mhz = target_frequencies[freq_index]

        cmd = [
            r"D:\Radioconda\Library\bin\hackrf_transfer.exe",
            "-r", "-",
            "-f", str(int(current_freq_mhz * 1_000_000)),
            "-s", str(int(samp_rate * 1_000_000)),
            "-a", "1",  # wzmacniacz
            "-l", "32", # czułość LNA
            "-g", "40"  # czułość VGA
        ]

        process = None
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            CHUNK_BYTES = 1024 * 1024

            start_time = time.time()

            while is_running and (time.time() - start_time < hop_interval):
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
                process.wait()

        freq_index = (freq_index + 1) % len(target_frequencies)

        time.sleep(0.1)


def main():
    global is_running

    print(f"Main started, skakanie pomiędzy: {target_frequencies} MHz")

    thread = threading.Thread(target=read_hackrf_stream)
    thread.daemon = True
    thread.start()

    fig, ax = plt.subplots(figsize=(10, 6))

    min_frequency = current_freq_mhz - (samp_rate / 2)
    max_frequency = current_freq_mhz + (samp_rate / 2)

    img = ax.imshow(waterfall_data, aspect='auto', cmap='jet',
                    vmin=min_db, vmax=max_db,
                    extent=[min_frequency, max_frequency, history_rows, 0])

    title = ax.set_title(f'Widmo 20 MHz  - Center: {current_freq_mhz} MHz')

    cbar = fig.colorbar(img, ax=ax)
    cbar.set_label('Siła sygnału')

    def update(frame):
        title.set_text(f'Widmo 20 MHz  - Center: {current_freq_mhz} MHz')

        min_f = current_freq_mhz - (samp_rate / 2)
        max_f = current_freq_mhz + (samp_rate / 2)
        img.set_extent([min_f, max_f, history_rows, 0])

        img.set_array(waterfall_data)

        return [img, title]

    ani = animation.FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)

    try:
        plt.show(block=True)
    except KeyboardInterrupt:
        pass
    finally:
        is_running = False
        print("\nZakończono")


if __name__ == "__main__":
    main()