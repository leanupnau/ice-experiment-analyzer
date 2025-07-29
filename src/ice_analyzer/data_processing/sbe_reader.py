import pandas as pd
import xarray as xr
import glob
import numpy as np  # Wichtig für find_closest_timestamp


__all__ = ['read_sbe_data', 'find_closest_timestamp']


# Funktion prüft, ob eine Zeile mit einem gültigen Zeitstempel in eckigen Klammern beginnt
def is_valid_datetime(line):
    if line.startswith('['):
        try:
            datetime_str = line[1:24]  # Timestamp ohne öffnende Klammer
            pd.to_datetime(datetime_str, format='%Y-%m-%d %H:%M:%S.%f')
            return True
        except ValueError:
            return False
    return False
    pass  


def read_sbe_data(file_path_pattern):
    """
    Liest und verarbeitet SBE-Logdateien in ein xarray Dataset.

    Args:
        file_path_pattern (str): Dateipfad-Muster, z.B. 'SBE*'

    Returns:
        ds_sbe (xarray.Dataset | None): Verarbeitetes Dataset oder None, wenn keine gültigen Daten
    """
    rows = []

    for n, sbe_file in enumerate(sorted(glob.glob(file_path_pattern))):
        print(f"Processing file: {sbe_file}")

        with open(sbe_file, 'r', encoding='utf8', errors='ignore') as file:
            lines = [line for line in file]

        print(f"First few lines in {sbe_file}:")
        print(lines[:5])

        valid_lines = [line for line in lines if is_valid_datetime(line)]

        print(f"Filtered valid lines in {sbe_file}:")
        # print(valid_lines[:5])  # Debug nur bei Bedarf aktivieren

        if not valid_lines:
            print(f"Warning: No valid lines found in {sbe_file}. Skipping this file.")
            continue

        for line in valid_lines:
            datetime_str = line[1:24]
            datetime_obj = pd.to_datetime(datetime_str, format='%Y-%m-%d %H:%M:%S.%f')

            if '#' in line:
                data_str = line.split('#')[1].strip()
                data_parts = data_str.split(',')
                if len(data_parts) >= 5:
                    try:
                        T_deg = float(data_parts[0].strip())
                        SV = float(data_parts[3].strip())
                        Sal = float(data_parts[2].strip())

                        rows.append({
                            'datetime': datetime_obj,
                            'T_deg': T_deg,
                            'Sal': Sal,
                            'SV': SV
                        })
                    except ValueError:
                        print(f"Warning: Invalid data format in line, skipping: {line}")
                        continue

    sbe_data = pd.DataFrame(rows)

    if not sbe_data.empty:
        ds_sbe = xr.Dataset(
            data_vars=dict(
                T_deg=('datetime', sbe_data['T_deg']),
                Sal=('datetime', sbe_data['Sal']),
                SV=('datetime', sbe_data['SV'])
            ),
            coords=dict(datetime=sbe_data['datetime'])
        )
        return ds_sbe
    else:
        print("No valid data was collected.")
        return None
    pass


def find_closest_timestamp(ds_sbe, target_datetime):
    """
    Findet den nächsten Zeitstempel zu target_datetime im SBE-Dataset.

    Args:
        ds_sbe (xarray.Dataset): Das geladene SBE-Dataset
        target_datetime (str or datetime): Der Zielzeitstempel

    Returns:
        tuple:
            - closest_timestamp (np.datetime64)
            - closest_T_deg (float)
            - closest_Sal (float)
            - closest_SV (float)
    """
    target_datetime = np.datetime64(target_datetime)
    time_diffs = np.abs(ds_sbe['datetime'].values - target_datetime)
    closest_idx = np.argmin(time_diffs)

    closest_timestamp = ds_sbe['datetime'].values[closest_idx]
    closest_T_deg = ds_sbe['T_deg'].values[closest_idx]
    closest_Sal = ds_sbe['Sal'].values[closest_idx]
    closest_SV = ds_sbe['SV'].values[closest_idx]

    return closest_timestamp, closest_T_deg, closest_Sal, closest_SV
    pass
