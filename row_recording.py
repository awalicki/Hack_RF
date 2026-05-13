import subprocess
import time
import datetime
import os


katalog_docelowy = r"D:\hack_rf_drone_13_05"

center_frequency = 876  # mhz
samp_rate = 20  # 2-20 mhz (20 to maks)
duration = 10


def nagraj_sygnal():
    czas_startu = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nazwa_pliku = f"nagranie_{center_frequency}MHz_{czas_startu}.raw"
    pelna_sciezka = os.path.join(katalog_docelowy, nazwa_pliku)

    print(f"Częstotliwość: {center_frequency } MHz")
    print(f"Szerokość pasma: {samp_rate } MHz")


    komenda = [
        r"D:\Radioconda\Library\bin\hackrf_transfer.exe",
        "-r", pelna_sciezka,
        "-f", str(center_frequency * 1_000_000),
        "-s", str(samp_rate * 1_000_000),
        "-a", "1",  # wzmacniacz
        "-l", "24",  # czułość LNA
        "-g", "10"  # czułość VGA
    ]

    proces = subprocess.Popen(komenda)

    try:

        time.sleep(duration)
    finally:

        proces.terminate()
        proces.wait()


if __name__ == "__main__":
    nagraj_sygnal()