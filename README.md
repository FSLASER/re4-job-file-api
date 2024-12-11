
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

3. [Example Usage](#example-usage)
   - [Test Scripts](#test-scripts)
4. [Contributing](#contributing)

---

## Getting Started

### Prerequisites

- Python 3.8+
- Dependencies listed in `requirements.txt`
- A known Re4/Re4b/beta server compatible with the job file API calls

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

**Description**: Processes an simple SVG file (contain paths only) into a `.lap` job file.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication.
  - `device_access_code` (str): Device access code.
- **Files**:
  - `svg_file`: The SVG file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-svg-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "svg_file=@path/to/your/file.svg"   -F "json_file=@path/to/your/color_settings.json"   --output generated_file.lap
```

---

### Process Raster Job (PNG)

#### Endpoint: `/api/jobs/standard-png-lap`

**Description**: Processes a PNG file into a `.lap` job file with transformation parameters.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication.
  - `device_access_code` (str): Device access code.
  - `transform_params` (str): A JSON string with transformation parameters (`[sx, shx, shy, sy, tx, ty]`).
- **Files**:
  - `png_file`: The PNG file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-png-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "png_file=@path/to/your/image.png"   -F "json_file=@path/to/your/color_settings.json"   -F "transform_params=[0.1, 0, 0, 0.1, 20.0, 15.25]"   --output generated_file.lap
```

---

### Process Paths (NPZ)

#### Endpoint: `/api/jobs/standard-npz-paths2d-lap`

**Description**: Processes an NPZ file containing vector data into a `.lap` job file. Key name in NPZ file indicating vector data must be `paths`.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication.
  - `device_access_code` (str): Device access code.
  - `color` (str): Stroke color for the vector paths.
- **Files**:
  - `npz_file`: The NPZ file containing vector paths.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-npz-paths2d-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "npz_file=@path/to/your/file.npz"   -F "json_file=@path/to/your/color_settings.json"   -F "color=#FF5733"   --output generated_file.lap
```

---

### Process Points (NPZ)

#### Endpoint: `/api/jobs/standard-npz-points2d-lap`

**Description**: Processes an NPZ file containing raster data into a `.lap` job file. Key name in NPZ file indicating raster data must be `points`.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication.
  - `device_access_code` (str): Device access code.
- **Files**:
  - `npz_file`: The NPZ file containing vector paths.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-npz-points2d-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "npz_file=@path/to/your/file.npz"   -F "json_file=@path/to/your/color_settings.json"   --output generated_file.lap
```

---

## Example Usage

### Test Scripts

- Clone the repository and navigate to the `api_demo` folder.
- Example scripts are available for each endpoint:
  - `standard_svg.py`
  - `standard_png.py`
  - `standard_npz_paths2d.py`
  - `standard_npz_points2d.py`

#### Running a Test Script

```bash
python api_demo/standard_svg.py
```

Replace parameters like `pass_code`, `device_access_code`, and file paths in the scripts as needed.

---

## Contributing

We welcome contributions! Please fork the repository and create a pull request for your changes. Ensure that your code adheres to the following guidelines:

1. Follow PEP 8 coding standards.
2. Write clear and concise documentation for new functions or features.
3. Include test scripts for new functionality.

---

For further assistance or questions, please [open an issue](https://github.com/your-username/re4-job-file-api/issues).
