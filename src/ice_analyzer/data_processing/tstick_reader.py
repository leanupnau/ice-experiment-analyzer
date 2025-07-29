import numpy as np
import pandas as pd
import xarray as xr
import glob
import re

# Nur diese beiden Funktionen sind Teil des öffentlichen API
__all__ = ['read_tstick_data', 'find_closest_tstick']


def read_tstick_data(file_path_pattern, downsample_rate=10):
    """
    Reads T-stick log files, validates format, processes into a dataframe,
    and returns an xarray dataset.

    Args:
        file_path_pattern (str): The glob pattern for T-stick log files (e.g., 'T_Stick*.log')
        downsample_rate (int): The rate at which to downsample the data (default is 10)

    Returns:
        ds_tsticks (xarray.Dataset): The processed xarray dataset with 'datetime' coordinate
    """
    files = sorted(glob.glob(file_path_pattern))
    valid_data = []
    total_lines_count = 0
    skipped_lines_count = 0

    # Regex: Zeilen mit gültigem Format (Zeitstempel + 16 Float-Werte)
    pattern = re.compile(
        r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]\s"
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\s"
        r"(-?\d+\.\d+\s){16}"
    )

    for T_file in files:
        print(f"Processing file: {T_file}")

        file_total = 0
        file_valid = 0

        try:
            with open(T_file, "r", encoding="utf-8") as f:
                for line in f:
                    file_total += 1
                    if pattern.match(line):
                        valid_data.append(line.strip())
                        file_valid += 1
                    else:
                        print(f"Skipping malformed line in {T_file}: {line.strip()}")
        except Exception as e:
            print(f"Error reading file {T_file}: {e}")
            continue

        file_skipped = file_total - file_valid
        total_lines_count += file_total
        skipped_lines_count += file_skipped

        print(f"File {T_file}: {file_valid}/{file_total} lines kept ({file_skipped} skipped)")

    if not valid_data:
        raise ValueError("No valid data was read from the files.")

    # Verarbeitung zu DataFrame
    data = pd.DataFrame([line.split() for line in valid_data])
    data.iloc[:, 0] = data.iloc[:, 0].str.strip('[')
    data.iloc[:, 1] = data.iloc[:, 1].str.strip(']')
    data['datetime'] = data.iloc[:, 0] + ' ' + data.iloc[:, 1]
    data = data.drop(columns=[0, 1, 2])
    data['datetime'] = pd.to_datetime(data['datetime'], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
    data = data[~data['datetime'].duplicated(keep=False)]
    data = data.sort_values(by='datetime', ascending=True)

    T_columns = [col for col in data.columns if col != 'datetime']
    data = data[['datetime'] + T_columns]
    data[T_columns] = data[T_columns].apply(pd.to_numeric, errors='coerce')

    print(data.head(1))  # Optionales Preview

    # xarray Dataset erzeugen
    ds_tsticks = xr.Dataset(
        data_vars=dict(
            T_deg=(('z', 'datetime'), data[T_columns].T.values),
        ),
        coords=dict(
            datetime=data['datetime'].values,
            z=np.arange(16) * 0.02 - 0.07
        )
    )

    print(ds_tsticks)
    print(ds_tsticks.dims)

    ds_tsticks = ds_tsticks.drop_duplicates(dim='datetime', keep='first')

    print(f"\nSummary: {total_lines_count - skipped_lines_count}/{total_lines_count} lines kept "
          f"({skipped_lines_count} skipped across all files)")

    return ds_tsticks
    pass


def find_closest_tstick(ds_tsticks, target_datetime):
    """
    Findet den nächsten Zeitstempel zu target_datetime im T-stick-Dataset
    und gibt das Temperaturprofil (über z) zurück.

    Args:
        ds_tsticks (xarray.Dataset): Das T-stick Dataset
        target_datetime (str or datetime): Der Zielzeitpunkt

    Returns:
        tuple:
            - closest_timestamp (np.datetime64)
            - closest_Tstick_Temp (xarray.DataArray): Temperaturprofil über z
    """
    if ds_tsticks is None:
        return None, None

    target_datetime = np.datetime64(target_datetime)
    time_diffs = np.abs(ds_tsticks['datetime'].values - target_datetime)
    closest_idx = np.argmin(time_diffs)

    closest_timestamp = ds_tsticks['datetime'].values[closest_idx]
    closest_Tstick_Temp = ds_tsticks['T_deg'].isel(datetime=closest_idx)

    return closest_timestamp, closest_Tstick_Temp
    pass
