import subprocess
import time
from datetime import datetime

target_frequencies = [5760, 2440]
hop_interval = 1.0  # sekundy
samp_rate = 20  # mhz


print("Start\n")

freq_index = 0
process = None

try:
    while True:
        current_freq = target_frequencies[freq_index]

        timestamp = datetime.now().strftime("%Y-%m-%d___%H_%M_%S")
        filename = f"raw_iq_duration_{hop_interval}freq_{current_freq}MHz_{timestamp}.raw"

        cmd = [
            r"D:\Radioconda\Library\bin\hackrf_transfer.exe",
            "-r", filename,
            "-f", str(int(current_freq * 1_000_000)),
            "-s", str(int(samp_rate * 1_000_000)),
            "-a", "1",
            "-l", "24",
            "-g", "10"
        ]

        print(f"Nagrywanie: {filename} przez {hop_interval} s...")

        process = subprocess.Popen(cmd)

        time.sleep(hop_interval)

        process.terminate()
        process.wait()

        freq_index = (freq_index + 1) % len(target_frequencies)


finally:
    if process and process.poll() is None:
        process.terminate()
        process.wait()