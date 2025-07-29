"""
Ice Experiment Data Analyzer

This module processes ice mechanical testing data and correlates it with 
environmental measurements (CTD, T-Stick) to create comprehensive datasets.

Author: Lea Nupnau, Niels Fuchs, Markus Ritschel
Email: my-e-mail
Date: 2025
"""

import os
import glob
import logging
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from file_utils import *
from plots import *
from dewesoft_reader import *
from sbe_reader import *
from sbe_w_density_reader import *
from tstick_reader import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IceExperimentAnalyzer:
    """
    Main class for analyzing ice experiment data.
    
    This class handles the processing of mechanical test data and combining them with
     environmental measurements from CTD and T-Stick sensors.
    """
    
    def __init__(self, base_experiment_path: str, reference_time: datetime = None):
        """
        Initialize the analyzer.
        
        Args:
            base_experiment_path: Path to the ByExperiment directory
            reference_time: Reference time for calculating "Antauzeit"
        """
        self.base_experiment_path = Path(base_experiment_path)
        self.reference_time = reference_time or datetime(2025, 7, 28, 0, 0, 0)  # Default reference
        self.master_csv_path = self.base_experiment_path / "ALL_EXPERIMENTS_SUMMARY.csv"
        
        # DataFrame columns definition
        self.df_columns = [
            "experiment_folder",
            "measurement_file_[.txt]",
            "Experiment_PeakTime",
            "ctd_time",
            "ctd_T",
            "ctd_S",
            "ctd_SV",
            "ctd_rho",
            "tstick_time",
            "tstick_profile",
            "caution"
        ]
    
    def find_experiment_folders(self) -> List[str]:
        """
        Find all experiment folders in the base directory.
        
        Returns:
            List of experiment folder names
        """
        if not self.base_experiment_path.exists():
            raise FileNotFoundError(f"Base path not found: {self.base_experiment_path}")
        
        folders = [
            f.name for f in self.base_experiment_path.iterdir()
            if f.is_dir() and not f.name.startswith('.')
        ]
        
        logger.info(f"Found {len(folders)} experiment folders: {folders}")
        return folders
    
    def get_processed_folders(self) -> set:
        """
        Get set of already processed folders from master CSV.
        
        Returns:
            Set of processed folder names
        """
        processed_folders = set()
        
        if self.master_csv_path.exists():
            try:
                existing_df = pd.read_csv(self.master_csv_path, sep=';', decimal=',')
                if 'experiment_folder' in existing_df.columns:
                    processed_folders = set(existing_df['experiment_folder'].unique())
                    logger.info(f"Already processed folders: {sorted(processed_folders)}")
            except Exception as e:
                logger.warning(f"Error loading existing CSV: {e}")
        
        return processed_folders
    
    def process_single_experiment(self, folder_path: Path) -> Optional[pd.DataFrame]:
        """
        Process a single experiment folder.
        
        Args:
            folder_path: Path to the experiment folder
            
        Returns:
            DataFrame with experiment results or None if processing failed
        """
        logger.info(f"Processing folder: {folder_path}")
        
        try:
            # Load environmental data
            env_data = self._load_environmental_data(folder_path)
            if not env_data:
                logger.warning(f"No environmental data found in {folder_path}")
                return None
            
            # Find test files
            test_files = self._find_test_files(folder_path)
            if not test_files:
                logger.warning(f"No test files found in {folder_path}")
                return None
            
            logger.info(f"Found {len(test_files)} test files")
            
            # Process each test file
            df_rows = []
            for test_file in test_files:
                row_data = self._process_test_file(test_file, env_data)
                if row_data:
                    row_data["experiment_folder"] = folder_path.name
                    df_rows.append(row_data)
            
            if df_rows:
                df_result = pd.DataFrame(df_rows)
                self._save_folder_summary(folder_path, df_result)
                return df_result
            
        except Exception as e:
            logger.error(f"Error processing {folder_path}: {str(e)}")
            return None
    
    def _load_environmental_data(self, folder_path: Path) -> Dict[str, Any]:
        """Load all environmental data for a folder."""
        env_data = {}
        
        try:
            # Load SBE data
            sbe_pattern = str(folder_path / "SBE*.log")
            env_data['ds_sbe'] = read_sbe_data(sbe_pattern)  # Your existing function
            
            # Load T-Stick data
            tstick_pattern = str(folder_path / "T_Stick_2025*.log")
            try:
                env_data['ds_tsticks'] = read_tstick_data(tstick_pattern, downsample_rate=10)
            except ValueError:
                env_data['ds_tsticks'] = None
            
            # Load density data
            density_pattern = str(folder_path / "*.cnv")
            try:
                env_data['ds_density'] = process_sbe37cnv_data(density_pattern)
            except (FileNotFoundError, ValueError):
                env_data['ds_density'] = None
            
            return env_data
            
        except Exception as e:
            logger.error(f"Error loading environmental data: {e}")
            return {}
    
    def _find_test_files(self, folder_path: Path) -> List[Path]:
        """Find all test files in a folder."""
        patterns = ["Test02_*.txt", "BiegeF_*.txt", "Emodul_*.txt"]
        test_files = []
        
        for pattern in patterns:
            files = list(folder_path.glob(pattern))
            test_files.extend(files)
        
        return sorted(test_files)
    
    def _process_test_file(self, test_file: Path, env_data: Dict) -> Optional[Dict]:
        """Process a single test file and extract relevant data."""
        try:
            # Read test data (your existing function)
            meta, time_data, force_data, corrected time = read_data(str(test_file))
            #meta, corrected_time = correct_start_time(meta) #(old line)
            
            # Convert to datetime
            time_data_dt = np.array([
                corrected_time + timedelta(seconds=t) for t in time_data
            ])
            
            # Find maximum force timestamp
            max_idx = np.argmax(force_data)
            max_timestamp = time_data_dt[max_idx]
            
            # Find closest measurements
            closest_data = self._find_closest_measurements(max_timestamp, env_data)
            
            # Create info file
            self._create_info_file(test_file, max_timestamp, closest_data)
            
            # Prepare row data for DataFrame
            row_data = {
                "measurement_file_[.txt]": test_file.name,
                "Experiment_PeakTime": pd.Timestamp(max_timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-6],
                "ctd_time": closest_data.get('ctd_time', 'N/A'),
                "ctd_T": closest_data.get('ctd_T', np.nan),
                "ctd_S": closest_data.get('ctd_S', np.nan),
                "ctd_SV": closest_data.get('ctd_SV', np.nan),
                "ctd_rho": closest_data.get('ctd_rho', np.nan),
                "tstick_time": closest_data.get('tstick_time', 'N/A'),
                "tstick_profile": closest_data.get('tstick_profile', 'N/A'),
                "caution": ""
            }
            
            return row_data
            
        except Exception as e:
            logger.error(f"Error processing test file {test_file}: {e}")
            return None
    
    def _find_closest_measurements(self, timestamp: datetime, env_data: Dict) -> Dict:
        """Find closest environmental measurements to given timestamp."""
        closest_data = {}
        
        # Find closest CTD data (your existing functions)
        if env_data.get('ds_sbe'):
            sbe_timestamp, sbe_T, sbe_S, sbe_SV = find_closest_timestamp(
                env_data['ds_sbe'], timestamp
            )
            closest_data.update({
                'sbe_time': pd.Timestamp(sbe_timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-6],
                'sbe_T': sbe_T,
                'sbe_S': sbe_S,
                'sbe_SV': sbe_SV
            })
        
        if env_data.get('ds_density'):
            density_timestamp, density_T, density_S, density_SV, density_rho = find_closest_density(
                env_data['ds_density'], timestamp
            )
            closest_data.update({
                'ctd_time': pd.Timestamp(density_timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-6],
                'ctd_T': density_T,
                'ctd_S': density_S,
                'ctd_SV': density_SV,
                'ctd_rho': density_rho
            })
        
        if env_data.get('ds_tsticks'):
            tstick_timestamp, tstick_temps = find_closest_tstick(
                env_data['ds_tsticks'], timestamp
            )
            if tstick_temps is not None:
                closest_data.update({
                    'tstick_time': pd.Timestamp(tstick_timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-6],
                    'tstick_profile': ';'.join([f"{temp:.3f}" for temp in tstick_temps])
                })
        
        return closest_data
    
    def _create_info_file(self, test_file: Path, max_timestamp: datetime, closest_data: Dict):
        """Create the info text file for a test."""
        output_file = test_file.parent / f"info_{test_file.name}"
        
        antauzeit_hours = (max_timestamp - self.reference_time).total_seconds() / 3600
        
        content = f"""File: {test_file}
Max Force Timestamp: {pd.Timestamp(max_timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")[:-6]}
Antauzeit (hours since {self.reference_time.strftime("%Y-%m-%d %H:%M:%S")}): {antauzeit_hours:.2f} h

CTD Data:
- Timestamp: {closest_data.get('ctd_time', 'N/A')}
- Temperature: {closest_data.get('ctd_T', 'N/A'):.4f} °C
- Salinity: {closest_data.get('ctd_S', 'N/A'):.4f} [psu]
- Sound Speed: {closest_data.get('ctd_SV', 'N/A'):.3f} m/s
- Density: {closest_data.get('ctd_rho', 'N/A'):.3f} kg/m³

T-Stick Data:
- Timestamp: {closest_data.get('tstick_time', 'N/A')}
- Profile: {closest_data.get('tstick_profile', 'N/A')}
"""
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Info file saved: {output_file}")
    
    def _save_folder_summary(self, folder_path: Path, df: pd.DataFrame):
        """Save summary CSV for individual folder."""
        csv_path = folder_path / "experiment_summary.csv"
        df.to_csv(csv_path, index=False, sep=';', decimal=',')
        logger.info(f"Folder summary saved: {csv_path}")
    
    def run_analysis(self, skip_existing: bool = True) -> None:
        """
        Run the complete analysis pipeline.
        
        Args:
            skip_existing: If True, skip folders already processed
        """
        logger.info("Starting ice experiment analysis")
        
        # Find all experiment folders
        experiment_folders = self.find_experiment_folders()
        
        # Determine which folders to process
        if skip_existing:
            processed_folders = self.get_processed_folders()
            folders_to_process = [f for f in experiment_folders if f not in processed_folders]
            
            if not folders_to_process:
                logger.info("All folders already processed!")
                return
            
            logger.info(f"Processing {len(folders_to_process)} new folders: {folders_to_process}")
            
            # Load existing data
            existing_df = pd.DataFrame()
            if self.master_csv_path.exists():
                existing_df = pd.read_csv(self.master_csv_path, sep=';', decimal=',')
        else:
            folders_to_process = experiment_folders
            existing_df = pd.DataFrame()
            logger.info(f"Processing all {len(folders_to_process)} folders")
        
        # Process folders
        all_results = [existing_df] if not existing_df.empty else []
        
        for folder_name in sorted(folders_to_process):
            folder_path = self.base_experiment_path / folder_name
            result_df = self.process_single_experiment(folder_path)
            
            if result_df is not None:
                all_results.append(result_df)
                logger.info(f"✅ Successfully processed {folder_name}")
            else:
                logger.warning(f"⚠️ Skipped {folder_name}")
        
        # Combine and save results
        if all_results:
            final_df = pd.concat(all_results, ignore_index=True)
            final_df.to_csv(self.master_csv_path, index=False, sep=';', decimal=',')
            
            logger.info(f"🎉 Master summary saved: {self.master_csv_path}")
            logger.info(f"📊 Total measurements: {len(final_df)}")
            
            # Show folder statistics
            folder_counts = final_df['experiment_folder'].value_counts()
            logger.info("Folder statistics:")
            for folder, count in folder_counts.items():
                logger.info(f"  - {folder}: {count} measurements")


def main():
    """Main entry point for the analysis."""
    # Configuration - move to config file later
    BASE_EXPERIMENT_PATH = "/Users/u241363/Desktop/Smilla/Data/Work/ByExperiment"
    REFERENCE_TIME = datetime(2025, 7, 28, 0, 0, 0)  # Adjust as needed
    
    # Create analyzer instance
    analyzer = IceExperimentAnalyzer(
        base_experiment_path=BASE_EXPERIMENT_PATH,
        reference_time=REFERENCE_TIME
    )
    
    # Run analysis
    analyzer.run_analysis(skip_existing=True)


if __name__ == "__main__":
    main()