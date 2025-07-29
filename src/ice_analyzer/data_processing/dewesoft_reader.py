import numpy as np
from datetime import datetime, timedelta

__all__ = ['read_data']


def read_data(file_path):
    """
    Liest .txt Datei und extrahiert Metadaten, Zeit und Kraftdaten.
    Korrigiert außerdem die Startzeit um -1h 44min (UTC).

    Args:
        file_path (str): Pfad zur .txt-Datei

    Returns:
        tuple:
            - metadata (list of str): ggf. korrigierte Metadaten
            - time_vals (np.ndarray): Zeitwerte in Sekunden
            - force_vals (np.ndarray): Kraftwerte
            - corrected_start_time (datetime or None): UTC-Zeit, wenn gefunden
    """

    def correct_start_time(metadata):
        for i, line in enumerate(metadata):
            if line.startswith("Start time:"):
                time_str = line.split(": ", 1)[1]
                original_time = datetime.strptime(time_str, "%m/%d/%Y %H:%M:%S.%f")
                corrected_time = original_time - timedelta(hours=1, minutes=44)
                metadata[i] = f"Start time (Corrected, UTC): {corrected_time.strftime('%m/%d/%Y %H:%M:%S')}"
                return metadata, corrected_time
        return metadata, None

    # Datei lesen
    with open(file_path, "r") as file:
        lines = file.readlines()

    metadata = []
    data_start = False
    time_vals, force_vals = [], []

    # Dateiinhalt verarbeiten
    for line in lines:
        line = line.strip()
        if line.startswith("Data1"):
            data_start = True
            continue
        if not data_start:
            metadata.append(line)
        else:
            if line and not line.startswith("Time"):
                parts = line.split("\t")
                time_vals.append(float(parts[0]))
                force_vals.append(float(parts[1]))

    # Startzeit korrigieren
    metadata, corrected_time = correct_start_time(metadata)

    return metadata, np.array(time_vals), np.array(force_vals), corrected_time
    pass
