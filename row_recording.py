import subprocess
import time


center_frequency = 876  # mhz
samp_rate = 20  # 2-20 mhz (20 to maks)
file_name = "test1.raw"
duration = 10


def nagraj_sygnal():
    print(f"Rozpoczynam nasłuch.")
    print(f"Częstotliwość: {center_frequency } MHz")
    print(f"Szerokość pasma: {samp_rate } MHz")


    komenda = [
        r"D:\Radioconda\Library\bin\hackrf_transfer.exe",
        "-r", file_name,
        "-f", str(center_frequency * 1_000_000),
        "-s", str(samp_rate * 1_000_000),
        "-a", "1",  # wzmacniacz
        "-l", "32",  # czułość LNA
        "-g", "40"  # czułość VGA
    ]

    proces = subprocess.Popen(komenda)

    try:

        time.sleep(duration)
    finally:

        proces.terminate()
        proces.wait()
        print(f"\nzapisano plik: {file_name}")


if __name__ == "__main__":
    nagraj_sygnal()