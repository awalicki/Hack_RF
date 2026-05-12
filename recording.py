import subprocess
import numpy as np
import time
import csv
from datetime import datetime


center_frequency = 5180  # mhz
samp_rate = 20  # 2-20 mhz (20 to maks)
fft_size = 8196


timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"widmo_{center_frequency}MHz_{timestamp_str}.csv"


def main():
    print(f"Nasłuch na częstotliwości: {center_frequency} MHz")

    cmd = [
        r"D:\Radioconda\Library\bin\hackrf_transfer.exe",
        "-r", "-",
        "-f", str(int(center_frequency * 1_000_000)),
        "-s", str(int(samp_rate * 1_000_000)),
        "-a", "1",  # wzmacniacz
        "-l", "32",  # czułość LNA
        "-g", "40"  # czułość VGA
    ]

    process = None

    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)

            header = ['Timestamp'] + [f'Bin_{i}' for i in range(fft_size)]
            writer.writerow(header)

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            CHUNK_BYTES = 1024 * 1024

            while True:
                raw_bytes = process.stdout.read(CHUNK_BYTES)

                if not raw_bytes:
                    print("[!] Brak danych ze strumienia HackRF.")
                    break

                needed_bytes = fft_size * 2
                if len(raw_bytes) >= needed_bytes:
                    data = np.frombuffer(raw_bytes[:needed_bytes], dtype=np.int8)
                    iq = data[0::2] + 1j * data[1::2]

                    fft_result = np.fft.fftshift(np.fft.fft(iq))

                    fft_mag = 10 * np.log10(np.abs(fft_result) + 1e-6)

                    fft_mag_rounded = np.round(fft_mag, 2)

                    row = [time.time()] + fft_mag_rounded.tolist()

                    writer.writerow(row)

    except KeyboardInterrupt:
        print("\nzatrzymano.")
    except Exception as e:
        print(f"\nbłąd: {e}")
    finally:
        if process:
            process.terminate()
        print("Zakończono, plik został poprawnie zamknięty.")


if __name__ == "__main__":
    main()