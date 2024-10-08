# LiDAR Data Processing Application

This Python application reads LiDAR data and outputs both a PCAP file and a CSV file of the processed data.

## Prerequisites

- Python 3.11

## Setup

1. Clone this repository:

   ```bash
   # install the repository and change directory to it
   
   cd lidar-data-processor
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python3.11 -m venv .venv
   # or
   py -3.11 -m venv .venv
   
   # To activate the virtual environment
   # On Windows:
   .venv\Scripts\activate
   
   # On macOS and Linux:
   source .venv/bin/activate
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Create `out` folder

    ```bash
    mkdir out
    ```

## Usage

<!-- I Want to say that you might need to change the ip in the live_reader file to 0.0.0.0 to listen to all  -->

To run the application, you need to have the LiDAR sensor connected to the computer. The application will read the data from the sensor and output the processed data to a PCAP file and a CSV file.

Change the IP address in the `live_reader.py` file to the IP address of the LiDAR sensor. Or Change to `0.0.0.0` to Bind to all available interfaces

To run the application:

```bash
python live_reader.py
```
