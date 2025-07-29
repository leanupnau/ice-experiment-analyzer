import pandas as pd
import xarray as xr
import glob
import numpy as np  

# Öffentliche Funktionen deklarieren – nur diese werden mit `from process_sbe37 import *` geladen
__all__ = ['process_sbe37cnv_data', 'find_closest_density']


def process_sbe37cnv_data(file_path_pattern):
    """
    Processes SBE37 .cnv data files and returns an xarray Dataset.

    Args:
        file_path_pattern (str): The file path pattern to match the SBE37 .cnv files
            (e.g., 'data/sbe37sm-rs232_03707247_*.cnv').

    Returns:
        ds_sbe_pro (xarray.Dataset): The processed dataset with Salinity, Temperature,
            and other variables, including correct datetime coordinates.
    """
    file_paths = sorted(glob.glob(file_path_pattern))
    if not file_paths:
        raise FileNotFoundError(f"No files found matching the pattern: {file_path_pattern}")

    data = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Find data section after '*END*'
        end_index = next((i for i, line in enumerate(lines) if '*END*' in line), None)
        if end_index is None:
            raise ValueError(f"*END* marker not found in file: {file_path}")
        data_lines = lines[end_index + 1:]

        # Extract year from "# start_time = ..."
        start_time_line = next((line for line in lines if line.lower().startswith('# start_time')), None)
        if start_time_line:
            try:
                time_str = start_time_line.split('=')[1].strip().split(' [')[0]
                start_dt = pd.to_datetime(time_str)
                year = start_dt.year
            except Exception:
                year = 2025  # fallback
        else:
            year = 2025  # fallback

        for line in data_lines:
            parts = line.split()
            if len(parts) >= 7:
                try:
                    row = [float(part) for part in parts[:7]]
                    data.append(row)
                except ValueError:
                    continue

    df = pd.DataFrame(data, columns=[
        'Salinity', 'Temperature', 'ElapsedTime', 'JulianTime',
        'SoundVelocity', 'Density', 'Flag'
    ])

    # Convert Julian day-of-year to datetime
    julian_base_time = pd.to_datetime(f"{year}-01-01 00:00:00")
    df['DateTime'] = julian_base_time + pd.to_timedelta(df['JulianTime'] - 1, unit='D')

    # Convert to xarray Dataset
    ds_sbe_pro = xr.Dataset(
        data_vars={
            'Salinity': ('datetime', df['Salinity']),
            'Temperature': ('datetime', df['Temperature']),
            'ElapsedTime': ('datetime', df['ElapsedTime']),
            'SoundVelocity': ('datetime', df['SoundVelocity']),
            'Density': ('datetime', df['Density']),
            'Flag': ('datetime', df['Flag']),
        },
        coords={
            'datetime': df['DateTime']
        }
    )

    print("Letzter Zeitstempel:", pd.to_datetime(ds_sbe_pro['datetime'].values[-1]))

    return ds_sbe_pro
    pass


def find_closest_density(ds_sbe, target_datetime):
    """
    Findet den nächsten Zeitstempel zu target_datetime im SBE37-Datensatz und gibt relevante Werte zurück.

    Args:
        ds_sbe (xarray.Dataset): Der verarbeitete Datensatz mit Zeitreihe
        target_datetime (str or datetime-like): Der Zielzeitpunkt

    Returns:
        tuple: (datetime64, Temperature, Salinity, SoundVelocity, Density)
    """
    target_datetime = np.datetime64(target_datetime)
    time_diffs = np.abs(ds_sbe['datetime'].values - target_datetime)
    closest_idx = np.argmin(time_diffs)

    closest_timestamp2 = ds_sbe['datetime'].values[closest_idx]
    closest_T_deg2 = ds_sbe['Temperature'].values[closest_idx]
    closest_Sal2 = ds_sbe['Salinity'].values[closest_idx]
    closest_SV2 = ds_sbe['SoundVelocity'].values[closest_idx]
    closest_Density = ds_sbe['Density'].values[closest_idx]

    return closest_timestamp2, closest_T_deg2, closest_Sal2, closest_SV2, closest_Density
    pass
