# Re4 Job File API

The **Re4 Job File API** provides endpoints to process job files, including vector-based files (SVG/NPZ) and raster-based files (PNG/NPZ), for laser engravers. This repository is designed for developers to interact with the API and generate `.lap` files, which are used to execute jobs on compatible laser machines.

## Features

- Process 2D vector files (`.svg`, `.npz`) and raster files (`.png`, `.npz`) into `.lap` job files.
- Support for various transformation parameters (scaling, Shearing, translation, etc.).
- API endpoints to validate and process user inputs.
- Easy integration with laser machine configurations.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Endpoints](#endpoints)
   - [Process Vector Job (SVG)](#process-vector-job-svg)
   - [Process Raster Job (PNG)](#process-raster-job-png)
   - [Process Paths (NPZ)](#process-paths-npz)
   - [Process Points (NPZ)](#process-points-npz)
   - [Run LAP Job](#run-lap-job)
   - [Stop Job](#stop-job)
   - [Query Job Status](#query-job-status)

3. [Example Usage](#example-usage)
   - [Test Scripts](#test-scripts)
4. [Contributing](#contributing)

---

## Getting Started

### Prerequisites

- Python 3.8+
- Dependencies listed in `requirements.txt`
- A known Re4/Re4b/beta server compatible with the job file API calls

### Authentication Requirements

- **User Passcode**: Required for all API endpoints. This can be found under your username after logging into the web interface (e.g., https://beta.fslaser.com). Note that for different website you will get a different user passcode.
- **Device Access Code**: Required for all API endpoints. This is displayed on the device's touchscreen and is unique to each machine.
  - The device must be added to the device list on the target API website
  - The device must be connected to the website
  - The generated `.lap` file will only work with the correct device

### File Requirements

- **SVG Files**: Must contain only line and/or cubic bezier paths
- **NPZ Files**:
  - For vector data: Must contain a key named `paths`
  - For raster data: Must contain a key named `points`
- **Color Settings**: Required JSON file for all processing endpoints
- **Output Files**: Generated `.lap` files will be saved to the specified output path

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/FSLASER/re4-job-file-api.git
   cd re4-job-file-api
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## Endpoints

### Process Simple Vector Job (SVG)

#### Endpoint: `/api/jobs/standard-svg-lap`

**Description**: Processes an simple SVG file **(contain line and/or cubic bezier paths only)** into a `.lap` job file.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
- **Files**:
  - `svg_file`: The SVG file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-svg-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "svg_file=@path/to/your/file.svg"   -F "json_file=@path/to/your/color_settings.json"   --output generated_file.lap
```

### Process Raster Job (PNG)

#### Endpoint: `/api/jobs/standard-png-lap`

**Description**: Processes a PNG file into a `.lap` job file with transformation parameters.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
  - `transform_params` (str): A JSON string with transformation parameters (`[sx, shx, shy, sy, tx, ty]`) which operates in mm space.
    - `sx`: Scale factor in the x-direction
    - `shx`: Shear factor in the x-direction
    - `shy`: Shear factor in the y-direction
    - `sy`: Scale factor in the y-direction
    - `tx`: Translation in the x-direction (in mm)
    - `ty`: Translation in the y-direction (in mm)
    These parameters form a 2D affine transformation matrix that transforms the input image coordinates to the desired output coordinates.

    Common transformation examples:
    - Scale to 0.1: `[0.1, 0, 0, 0.1, 0, 0]`
    - Rotate 90 degrees clockwise: `[0, 1, -1, 0, 0, 0]`
    - Rotate 180 degrees: `[-1, 0, 0, -1, 0, 0]`
    - Rotate 270 degrees clockwise: `[0, -1, 1, 0, 0, 0]`
    - Scale to 0.1 and rotate 90 degrees clockwise: `[0, 0.1, -0.1, 0, 0, 0]`
    - Scale to 0.1 and translate by (20mm, 15.25mm): `[0.1, 0, 0, 0.1, 20.0, 15.25]`
    - Mirror horizontally: `[-1, 0, 0, 1, 0, 0]`
    - Mirror vertically: `[1, 0, 0, -1, 0, 0]`
    - Scale to 0.1 and mirror horizontally: `[-0.1, 0, 0, 0.1, 0, 0]`
    - Scale to 0.1 and mirror vertically: `[0.1, 0, 0, -0.1, 0, 0]`
    - Scale to 0.1 and rotate 45 degrees clockwise: `[0.0707, 0.0707, -0.0707, 0.0707, 0, 0]`
    - Scale to 0.1 and rotate 45 degrees counter-clockwise: `[0.0707, -0.0707, 0.0707, 0.0707, 0, 0]`
    - Scale to 0.1 and shear horizontally by 0.5: `[0.1, 0.05, 0, 0.1, 0, 0]`
    - Scale to 0.1 and shear vertically by 0.5: `[0.1, 0, 0.05, 0.1, 0, 0]`
    - Scale to 0.1 and rotate 90 degrees clockwise and translate by (20mm, 15.25mm): `[0, 0.1, -0.1, 0, 20.0, 15.25]`
    - Scale to 0.1 and rotate 45 degrees clockwise and translate by (20mm, 15.25mm): `[0.0707, 0.0707, -0.0707, 0.0707, 20.0, 15.25]`

    Note: The transformation is applied in the order: scale → shear → rotate → translate.

    For more detailed technical information about affine transformations, see:
    - [MathWorks documentation](https://www.mathworks.com/discovery/affine-transformation.html)
    - [Apache Sedona documentation](https://sedona.apache.org/1.6.1/api/sql/Raster-affine-transformation/)
- **Files**:
  - `png_file`: The PNG file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-png-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "png_file=@path/to/your/image.png"   -F "json_file=@path/to/your/color_settings.json"   -F "transform_params=[0.1, 0, 0, 0.1, 20.0, 15.25]"   --output generated_file.lap
```

### Process Paths (NPZ)

#### Endpoint: `/api/jobs/standard-npz-paths2d-lap`

**Description**: Processes an NPZ file containing vector data into a `.lap` job file. Key name in NPZ file indicating vector data must be `paths`.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
  - `color` (str): Stroke color for the vector paths.
- **Files**:
  - `npz_file`: The NPZ file containing vector paths.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-npz-paths2d-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "npz_file=@path/to/your/file.npz"   -F "json_file=@path/to/your/color_settings.json"   -F "color=#FF5733"   --output generated_file.lap
```

### Process Points (NPZ)

#### Endpoint: `/api/jobs/standard-npz-points2d-lap`

**Description**: Processes an NPZ file containing raster data into a `.lap` job file. Key name in NPZ file indicating raster data must be `points`.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
- **Files**:
  - `npz_file`: The NPZ file containing vector paths.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-npz-points2d-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "npz_file=@path/to/your/file.npz"   -F "json_file=@path/to/your/color_settings.json"   --output generated_file.lap
```

> **Note**: The following three endpoints require you to add your device to the device list on the target API website and have the device connected to the website.

### Run LAP Job

#### Endpoint: `/api/jobs/api-run-lap-job`

**Description**: Executes a `.lap` job file on the laser machine.

⚠️ **IMPORTANT NOTE**: The LAP file must be generated using the same device ID as the target machine, otherwise the job will fail to run.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
- **Files**:
  - `lap_file`: The `.lap` file to execute.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/api-run-lap-job" \
  -F "pass_code=my-pass-code" \
  -F "device_access_code=my-device-access-code" \
  -F "lap_file=@path/to/your/job.lap"
```

### Stop Job

#### Endpoint: `/api/jobs/api-stop-job`

**Description**: Stops the currently running job on the laser machine.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/api-stop-job" \
  -F "pass_code=my-pass-code" \
  -F "device_access_code=my-device-access-code"
```

### Query Job Status

#### Endpoint: `/api/jobs/api-query-job-status`

**Description**: Retrieves the current status of the job running on the laser machine.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/api-query-job-status" \
  -F "pass_code=my-pass-code" \
  -F "device_access_code=my-device-access-code"
```

---

## Example Usage

### Test Scripts

- Clone the repository and test scripts are in root folder.
- Example scripts are available for each endpoint:
  - `standard_svg.py`
  - `standard_png.py`
  - `standard_npz_paths2d.py`
  - `standard_npz_points2d.py`
  - `api_run_lap_job.py`
  - `api_stop_job.py`
  - `api_query_job_status.py`

#### Running a Test Script

```bash
python standard_svg.py
```

Before running any script, make sure to:
1. Update the `pass_code` with your user passcode from the website
2. Update the `device_access_code` with the code from your device's touchscreen
3. Set the correct paths for input and output files

---

## Contributing

We welcome contributions! Please fork the repository and create a pull request for your changes. Ensure that your code adheres to the following guidelines:

1. Follow PEP 8 coding standards.
2. Write clear and concise documentation for new functions or features.
3. Include test scripts for new functionality.

---

For further assistance or questions, please [open an issue](https://github.com/your-username/re4-job-file-api/issues).