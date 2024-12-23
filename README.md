# User Manual for Log Analysis Flask Application  

**Industrial Project - Katarzyna Góźdź, Jan Michalak, Wiktor Zborowski**  
*Date: 19.12.2024*

---

## Table of Contents

1. [Introduction](#introduction)  
2. [Features](#features)  
3. [Prerequisites](#prerequisites)  
4. [Installation](#installation)  
5. [Configuration](#configuration)  
6. [Running the Application](#running-the-application)  
7. [Application Usage](#application-usage)  
8. [Troubleshooting](#troubleshooting)

---

## Introduction  

This application is designed to process, analyze, and visualize log data. It provides a web interface for configuring analysis parameters, viewing metrics, generating visualizations, and downloading comprehensive reports.
More details in the PDF file `my_flask_app/Instruction_log_reader.pdf`
---

## Features  

- **File Processing**: The app processes `.log` files with specific naming conventions, converting them to `.csv` files for further analysis.  
- **Data Analysis**: Computes error metrics such as MAE, MSE, RMSE, MAPE, Max Error, and Std Error.  
- **Visualizations**: Generates histograms, line plots, and boxplots for error distributions across different degrees.  
- **Web Interface**: Provides routes for processing logs, configuring parameters, viewing data, and downloading reports.  
- **Report Generation**: Allows downloading analysis results in PDF format.

---

## Prerequisites  

Before installing and running the application, ensure that your system meets the following requirements:

- **Operating System**: Windows, macOS, or Linux.  
- **Python**: Version 3.10 or higher.  
- **Most Important Python Packages**:  
  - Flask  
  - pandas  
  - numpy  
  - matplotlib  
  - tabulate  
- **Additional Tools**:  
  - A web browser (e.g., Chrome, Firefox).

---

## Installation  

### Clone the Repository  

First, clone the application's repository to your local machine:

```bash
git clone https://github.com/Torekas/log-analysis-flask-app.git
cd log-analysis-flask-app
```

### Set Up a Virtual Environment  

It's recommended to use a virtual environment to manage dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:  

- **Windows**:  
    ```bash
    venv\Scripts\activate
    ```  
- **macOS/Linux**:  
    ```bash
    source venv/bin/activate
    ```

### Install Dependencies  

Install the required Python packages using `pip`:

```bash
pip install -r my_flask_app/requirements.txt
```

Ensure that your `requirements.txt` includes:

```
Flask
pandas
numpy
matplotlib
tabulate
requests
```

---

## Configuration  

### File Naming Conventions  

The application expects files to follow a specific naming structure. The following regular expression is used to validate filenames:

```
Putty_(Big|Small|BigSmall)_(\d+)cm_initf_115200_(\d+)_degree(?:_(\d+))?\.csv
```

#### Examples of Valid Filenames:

- `Putty_Big_100cm_initf_115200_0_degree.csv`  
- `Putty_Small_150cm_initf_115200_45_degree_1.csv`  
- `Putty_BigSmall_200cm_initf_115200_90_degree.csv`  

---

### Mapping Degrees to File Indices  

The following table maps file indices to specific degree angles:

| File Index | Degree |
|------------|--------|
| 1          | 0°     |
| 2          | 45°    |
| 3          | 90°    |
| 4          | 135°   |
| 5          | 180°   |
| 6          | 225°   |
| 7          | 270°   |
| 8          | 315°   |

---

## Running the Application  

### Start the Flask Server  

To run the application, execute the following command within the project directory:

```bash
python app.py
```

By default, Flask runs on `http://127.0.0.1:5000`.

### Accessing the Web Interface  

Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

---

## Application Usage  

### Processing Log Files  

1. Navigate to `/process_logs` through the web interface.  
2. Provide the following paths:  
   - Absolute path for the **logs folder**.  
   - Absolute path for the **output folder**.  
   - Absolute path for the **database file**.  
3. Click the button to start processing logs.  
4. Upon completion, logs are converted to CSV files, and tables are stored in a `.db` file.

---

### Configuring Analysis Parameters  

1. Navigate to `/configuer` through the web interface.  
2. Fill in the following fields:  
   - **Directory of CSV Files**: Path to the folder with CSV files.  
   - **Specific Value**: Status value for filtering (e.g., `SUCCESS` or `Ok`).  
   - **Distance Column**: Column name representing distances (`distance[cm]` or `D_cm`).  
   - **Status Column**: Column name representing statuses (`status` or `Status`).  

3. Submit the form to save the configuration.  
4. Analysis will run, and you will be redirected to the homepage.
5. It is important to analyse only one type of logs (Big, Small or BigSmall) due to missmatch of columns.

---

### Viewing Analysis Results  

1. On the homepage, select a specific `point_id`.  
2. The application will display:  
   - **Metrics Table**: MAE, MSE, RMSE, MAPE, Max Error, Std Error.  
   - **Chart Image**: Histograms, line plots, and boxplots.  

---

### Downloading Analysis Reports  

1. Access `/download_pdf` via the web interface.  
2. Click the button to download the PDF report.

---

## Troubleshooting  

### Common Issues  

#### Empty Metrics Table  
- **Cause**: No data matches the `specific_value` filter.  
- **Solution**: Verify that the `specific_value` matches the data.  

#### File Not Loaded  
- **Cause**: File naming does not match the required structure.  
- **Solution**: Ensure filenames follow the pattern:

```
Putty_Small_<distance>cm_initf_115200_<angle>_degree_<index>.<csv|log>
Putty_Big_<distance>cm_initf_115200_<angle>_degree_<index>.<csv|log>
```

---

### Checking Logs  

Monitor the Flask server console for error messages during processing and analysis.

---


