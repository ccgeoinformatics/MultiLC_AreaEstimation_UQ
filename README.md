# Multi-class Land Cover Map Accuracy Assessment, Area Estimation, and Uncertainty Quantification

This repository provides a tool for assessing the accuracy of multi-class land cover maps, estimating area, and quantifying uncertainty. It includes a graphical user interface (GUI) that simplifies input of data and displays results, with options to save the results for further analysis.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Methodology](#methodology)
- [Output Explanation](#output-explanation)
- [Contact](#contact)

## Features
- **GUI for Input**: Easily enter pixel size, error matrix values, and mapped pixel counts using an intuitive interface.
- **Interactive Tooltips**: Hover over fields for guidance on required input.
- **Accuracy Metrics**: Calculates user’s accuracy, producer’s accuracy, and overall accuracy for each class.
- **Area Estimation**: Provides error-adjusted area estimates per class.
- **Uncertainty Quantification**: Computes standard errors and 95% confidence intervals for each metric.
- **CSV Export**: Option to save the results to a CSV file.

## Requirements
- **Python**: Version 3.7 or higher
- **Libraries**: Install necessary Python libraries by running:
  ```bash
  pip install numpy pandas scipy tkinter
  ```
  > Note: `tkinter` comes pre-installed with most Python distributions.

## Installation
### Option 1: Clone the Repository

Download the repository using Git:

```bash
git clone https://github.com/ccgeoinformatics/MultiLC_AreaEstimation_UQ
cd MultiLC_AreaEstimation_UQ
```
### Option 2: Download as a ZIP File
1. Go to the [repository on GitHub](https://github.com/ccgeoinformatics/MultiLC_AreaEstimation_UQ).
2. Click on the "Code" button.
3. Select "Download ZIP" and extract the downloaded file.

## Usage
1. Run the script in your Python environment:
   ```bash
   python multilc_accuracy_areaEstimation_uq_interactive.py
   ```
2. The GUI will open, prompting you to:
   - Enter the **number of land cover classes** and configure the matrix.
   - Input the **pixel size**.
   - Fill out the **error matrix** with counts for each class, and provide the **total mapped pixels** for each class.
3. Click **Run Analysis** to calculate metrics.
4. Save the results as a CSV file if desired.

## Methodology
The methodology follows these references:
1. **Olofsson et al. (2013)**: Making better use of accuracy data in land change studies: Estimating accuracy and area and quantifying uncertainty using stratified estimation. *Remote Sensing of Environment*, 129, 122-131.
   [https://doi.org/10.1016/j.rse.2012.10.031](https://doi.org/10.1016/j.rse.2012.10.031)
2. **Olofsson et al. (2014)**: Good practices for estimating area and assessing accuracy of land change. *Remote Sensing of Environment*, 148, 42-57.
   [https://doi.org/10.1016/j.rse.2014.02.015](https://doi.org/10.1016/j.rse.2014.02.015)
   
Users of the scripts are advised to read the above references for the theoretical concepts behind the methods, including the assumptions (for example, the error matrix shall be generated from a stratified random sampling design).

## Output Explanation

The following explanations are from Olofsson et al. (2013):
- **User's Accuracy**: "the proportion of the area mapped as a particular category that is actually that category “on the ground” where the reference classification is the best assessment of ground condition."
- **Producer's Accuracy**: "the proportion of the area that is a particular category on the ground that is also mapped as that category."
- **Overall Accuracy**: the proportion of the area mapped correctly. It provides the user of the map with the probability that a randomly selected location on the map is correctly classified."
- **Error-Adjusted Area**: The area estimate per class, adjusted based on accuracy metrics.
- **Standard Errors and Confidence Intervals**: Provides uncertainty metrics for accuracy metrics and area estimates.

Each metric includes:
- **Standard Error (SE)**: The variability or uncertainty in the metric.
- **95% Confidence Interval (CI)**: The range within which the true value is likely to fall, with 95% confidence.

## Contact
For any questions or issues, please reach out to:

**Jojene R. Santillan**  
Institute of Photogrammetry and GeoInformation (IPI), Leibniz University Hannover, Germany  
& Caraga Center for Geo-Informatics & Department of Geodetic Engineering, College of Engineering and Geosciences, Caraga State University, Butuan City, Philippines  
santillan@ipi.uni-hannover.de, jrsantillan@carsu.edu.ph
