import numpy as np
import matplotlib.pyplot as plt
import os

center_frequency = 876  # MHz
samp_rate = 20
file_name = r"D:\hack_rf_drone_13_05\nagranie_876MHz_2026-05-13_15-29-38.raw"
fft_size = 1024
min_db = 10
max_db = 60


sekundy_do_wczytania = 3


def rysuj_wodospad():

    ilosc_bajtow = int(samp_rate * 1_000_000 * 2 * sekundy_do_wczytania)

    rozmiar_pliku = os.path.getsize(file_name)
    ilosc_bajtow = min(ilosc_bajtow, rozmiar_pliku)

    print(f"Wczytywanie pierwszych {sekundy_do_wczytania} sekund (ok. {ilosc_bajtow / 1024 / 1024:.1f} MB z dysku)")

    dane_surowe = np.fromfile(file_name, dtype=np.int8, count=ilosc_bajtow)

    i_data = dane_surowe[0::2]
    q_data = dane_surowe[1::2]

    min_len = min(len(i_data), len(q_data))


    i_data = i_data[:min_len].astype(np.float32)
    q_data = q_data[:min_len].astype(np.float32)

    sygnal_zespolony = i_data + 1j * q_data
    sygnal_zespolony = sygnal_zespolony - np.mean(sygnal_zespolony)

    plt.figure(figsize=(12, 8))

    plt.specgram(
        sygnal_zespolony,
        NFFT=fft_size,
        Fs=samp_rate * 1_000_000,
        Fc=center_frequency * 1_000_000,
        cmap='turbo',
        scale='dB'
    )

    plt.title(f'Wodospad SDR - {samp_rate} MHz Pasma (Fragment {sekundy_do_wczytania} s)')
    plt.tight_layout()

    print("Wyświetlam wodospad.")
    plt.show()


if __name__ == "__main__":
    rysuj_wodospad()