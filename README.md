# Ice Experiment Data Analyzer 🧊

A Python tool for processing and analyzing ice mechanical testing data, matching mechanical test results with environmental measurements from CTD and T-Stick sensors.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features

- **Automated Data Processing**: Batch processes multiple experiment folders
- **Matching Data in time**: Match mechanical test data and their timing with CTD and T-Stick measurements
- **Flexible Output**: Generate both individual folder summaries and master datasets
- **Custom Processing**: Skip already processed folders to save time
- **Logging**: Track processing status and errors
- **Configurable**: Configuration via YAML files

## Installation

### Prerequisites

- Python 3.8 or higher
- Required dependencies (see `requirements.txt`)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ice-experiment-analyzer.git
cd ice-experiment-analyzer
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure paths:**
   - Copy `config/example_config.yaml` to `config/config.yaml`
   - Update paths in the configuration file to match your system

## Quick Start

### Basic Usage

```python
from src.ice_analyzer.main import IceExperimentAnalyzer

# Initialize analyzer
analyzer = IceExperimentAnalyzer(
    base_experiment_path="/path/to/your/ByExperiment/folder"
)

# Run analysis (skip already processed folders)
analyzer.run_analysis(skip_existing=True)
```

### Command Line Usage

```bash
# Process all new experiments
python -m src.ice_analyzer.main

# Reprocess all experiments
python -m src.ice_analyzer.main --no-skip-existing
```

## Data Structure

### Input Data Expected

Your experiment folders should be organized as follows:

```
ByExperiment/
├── KW30Plate/
│   ├── SBE*.log          # CTD data files
│   ├── T_Stick_2025*.log # T-Stick temperature profiles
│   ├── SBE*.cnv             # Density data
│   ├── Test02_*.txt      # Mechanical test data
│   ├── BiegeF_*.txt      # Bending strength tests
│   └── Emodul_*.txt      # E-modulus tests
├── KW31/
│   └── ...
└── ...
```

### Output Files

For each experiment folder:
- `info_*.txt`: Information for each test file
- `experiment_summary.csv`: Tabular summary of all tests in the folder ( e.g. summarizes all results for files in in the KW31 directory )

Master output:
- `ALL_EXPERIMENTS_SUMMARY.csv`: Combined data from all experiments

## Configuration

Edit `config/config.yaml` to customize:

- **Paths**: Base experiment directory, output locations
- **Processing Settings**: Downsampling rates, file patterns
- **Output Format**: CSV separators, timestamp formats
- **Logging**: Log levels and formats

Example configuration:

```yaml
paths:
  base_experiment_path: "/path/to/ByExperiment"

processing:
  tstick_downsample_rate: 10
  skip_existing_by_default: true

output:
  csv_separator: ";"
  decimal_separator: ","
```

## Output Data Schema

The generated CSV files contain the following columns:

| Column | Description |
|--------|-------------|
| `experiment_folder` | Name of the experiment folder |
| `measurement_file_[.txt]` | Original test file name |
| `Experiment_PeakTime` | Timestamp of maximum force |
| `ctd_time` | Closest CTD measurement timestamp |
| `ctd_T` | CTD temperature (°C) |
| `ctd_S` | CTD salinity (psu) |
| `ctd_SV` | CTD sound velocity (m/s) |
| `ctd_rho` | CTD density (kg/m³) |
| `tstick_time` | Closest T-Stick measurement timestamp |
| `tstick_profile` | Temperature profile (semicolon-separated) |
| `caution` | Quality flags or warnings |

## Advanced Usage

### Custom Processing

```python
# Process specific folders only
analyzer = IceExperimentAnalyzer("/path/to/data")
specific_folders = ["KW30Plate", "KW31Plate"]

for folder in specific_folders:
    result = analyzer.process_single_experiment(
        analyzer.base_experiment_path / folder
    )
```

### Integration with Analysis Pipelines

```python
import pandas as pd
from src.ice_analyzer.main import IceExperimentAnalyzer

# Run analysis
analyzer = IceExperimentAnalyzer("/path/to/data")
analyzer.run_analysis()

# Load results for further analysis
df = pd.read_csv("ALL_EXPERIMENTS_SUMMARY.csv", sep=';', decimal=',')

# Your analysis code here...
```

## Development   (-> Testing is not yet available!)

### Project Structure

```
ice-experiment-analyzer/
├── src/ice_analyzer/          # Main package
│   ├── main.py               # Main analyzer class
│   ├── data_processing/      # Data reading modules
│   ├── utils/               # Utility functions
│   └── visualization/       # Plotting functions
├── tests/                   # Unit tests
├── config/                  # Configuration files
├── examples/               # Usage examples
└── docs/                   # Documentation
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/ice_analyzer
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Dependencies

Key dependencies include:
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `matplotlib`: Plotting and visualization
- `xarray`: N-dimensional labeled arrays (for CTD data)
- `pyyaml`: Configuration file parsing

See `requirements.txt` for complete list.

## Troubleshooting

### Common Issues

**Q: "No SBE data found" error**
A: Ensure your SBE log files follow the pattern `SBE*.log` and are in the correct folder.

**Q: Analysis runs but no data in output**
A: Check that your test files match the expected patterns (`Test02_*.txt`, `BiegeF_*.txt`, `Emodul_*.txt`).

### Logging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Citation

If you use this software in your research, please cite:

```bibtex
@software{ice_experiment_analyzer,
  author = {tbd},
  title = {Ice Experiment Data Analyzer},
  url = {https://github.com/yourusername/ice-experiment-analyzer},
  year = {2025}
}
```

## Contact

- **Author**: [tbd]
- **Email**: [tbd]
- **Institution**: [Ifm Hamburg University]

## Acknowledgments

- TBD
