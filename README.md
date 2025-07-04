# Re4 Job File API

The **Re4 Job File API** provides endpoints to process job files, including vector-based files (SVG/NPZ) and raster-based files (PNG/NPZ), for laser engravers. This repository is designed for developers to interact with the API and generate `.lap` files, which are used to execute jobs on compatible laser machines.

## Features

- Process 2D vector files (`.svg`, `.npz`) and raster files (`.png`, `.npz`) into `.lap` job files.
- Support for various transformation parameters (scaling, Shearing, translation, etc.).
- API endpoints to validate and process user inputs.
- Easy integration with laser machine configurations
- Image capture from Laser Camera supported by API
- Move CNC gantry XYZ supported by API

## Table of Contents

1. [Getting Started](#getting-started)
2. [Endpoints](#endpoints)
   - [Get Workspace Size](#get-workspace-size)
   - [Process Vector Job (SVG)](#process-vector-job-svg)
   - [Process 3D Projected Vector Job (SVG)](#process-3d-projected-vector-job-svg)
   - [Process Raster Job (PNG)](#process-raster-job-png)
   - [Process 3D Projected Raster Job (PNG)](#process-3d-projected-raster-job-png)
   - [Process Paths (NPZ)](#process-paths-npz)
   - [Process Points (NPZ)](#process-points-npz)
   - [Process GVDesign Job](#process-gvdesign-job)
   - [Process PDF Job](#process-pdf-job)
   - [Run LAP Job](#run-lap-job)
   - [Stop Job](#stop-job)
   - [Query Job Status](#query-job-status)
   - [Camera Capture](#capture-image)
   - [Gantry Move](#gantry-move)

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

### Get Workspace Size

#### Endpoint: `/api/jobs/get-workspace-size`

**Description**: Retrieves the workspace size information from the specified device.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `device_access_code` (str): Device access code obtained from device touchscreen.

**Response**:
- Returns JSON data containing workspace size information for the device

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/get-workspace-size" \
  -F "device_access_code=my-device-access-code"
```

### Process Vector Job (SVG)

#### Endpoint: `/api/jobs/standard-svg-lap`

**Description**: Processes an SVG file **(contain vector paths only, endpoint will ignore raster data)** into a `.lap` job file.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
  - `workspace_width_mm` (float, optional): Workspace width in millimeters to place the file at top left of the workspace.
  - `workspace_height_mm` (float, optional): Workspace height in millimeters to place the file at top left of the workspace.
- **Files**:
  - `svg_file`: The SVG file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-svg-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_access_code=my-device-access-code" \
  -F "workspace_width_mm=100.0" \
  -F "workspace_height_mm=100.0" \
  -F "svg_file=@path/to/your/file.svg" \
  -F "json_file=@path/to/your/color_settings.json" \
  --output generated_file.lap
```

### Process 3D Projected Vector Job (SVG)

#### Endpoint: `/api/jobs/project3d-svg-lap`

**Description**: Processes an SVG file **(contain vector paths only, endpoint will ignore raster data)** and wraps it onto a 3D mesh surface to create a `.lap` job file.

⚠️ **Warning**: This endpoint will produce an empty LAP file result if you do not own a 3D galvo laser.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
  - `workspace_width_mm` (float, optional): Workspace width in millimeters to place the file at top left of the workspace.
  - `workspace_height_mm` (float, optional): Workspace height in millimeters to place the file at top left of the workspace.
- **Files**:
  - `svg_file`: The SVG file to process.
  - `json_file`: A JSON file containing color settings.
  - `mesh_file`: A 3D mesh file (e.g., .obj) onto which the SVG will be projected.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/project3d-svg-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_access_code=my-device-access-code" \
  -F "workspace_width_mm=100.0" \
  -F "workspace_height_mm=100.0" \
  -F "svg_file=@path/to/your/file.svg" \
  -F "json_file=@path/to/your/color_settings.json" \
  -F "mesh_file=@path/to/your/mesh.obj" \
  --output generated_file.lap
```

### Process Raster Job (PNG)

#### Endpoint: `/api/jobs/standard-png-lap`

**Description**: Processes a PNG file into a `.lap` job file with transformation parameters.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
  - `transform_params` (str): A JSON string with transformation parameters (`[sx, shy, shx, sy, tx, ty]`) which operates in mm space.
    - `sx`: Scale factor in the x-direction
    - `shy`: Shear factor in the y-direction
    - `shx`: Shear factor in the x-direction
    - `sy`: Scale factor in the y-direction
    - `tx`: Translation in the x-direction (in mm)
    - `ty`: Translation in the y-direction (in mm)
    These parameters form a 2D affine transformation matrix that transforms the input image coordinates to the desired output coordinates.

- **Files**:
  - `png_file`: The PNG file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-png-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "png_file=@path/to/your/image.png"   -F "json_file=@path/to/your/color_settings.json"   -F "transform_params=[0.1, 0, 0, 0.1, 20.0, 15.25]"   --output generated_file.lap
```

**NOTE**:
Transform matrix is laid out like this:

```text
[scaleX, shearX, translationX]
[shearY, scaleY, translationY]
[     0,      0,            1]
```

Local origin of the image is at its top-left corner. Device coordinates start at 0,0 with X increasing towards the right and Y increasing towards the top.

To rotate an image and center it:

 - θ: The angle of the image
 - W: The width of the image, in mm
 - H: The height of the image, in mm

Multiply these matrices R * T (order is important!):
```text
          R                 T
[cos(θ)  -sin(θ)  0] · [1  0  -W/2]
[sin(θ)   cos(θ)  0]   [0  1   H/2]
[0        0       1]   [0  0   1  ]
```

Extract the resulting matrix into an array to use as `transform_params`:

```text
[scaleX, shearY, shearX, translationX, translationY]
```

Common transformation examples:
- Scale to 0.1: `[0.1, 0, 0, 0.1, 0, 0]`
- Rotate 90 degrees clockwise: `[0, 1, -1, 0, 0, 0]`
- Rotate 180 degrees: `[-1, 0, 0, -1, 0, 0]`
- Rotate 270 degrees clockwise: `[0, -1, 1, 0, 0, 0]`
- Scale to 0.1 and rotate 90 degrees clockwise: `[0, 0.1, -0.1, 0, 0, 0]`
- Scale to 0.1 and translate by (20mm, 15.25mm): `[0.1, 0, 0, 0.1, 20.0, 15.25]`
- Mirror horizontally: `[-1, 0, 0, 1, 0, 0]`
- Mirror vertically: `[1, 0, 0, -1, 0, 0]`
- Scale to 0.1 and rotate 45 degrees clockwise: `[0.0707, 0.0707, -0.0707, 0.0707, 0, 0]`
- Scale to 0.1 and rotate 45 degrees counter-clockwise: `[0.0707, -0.0707, 0.0707, 0.0707, 0, 0]`
- Scale to 0.1 and rotate 90 degrees clockwise and translate by (20mm, 15.25mm): `[0, 0.1, -0.1, 0, 20.0, 15.25]`
- Scale to 0.1 and rotate 45 degrees clockwise and translate by (20mm, 15.25mm): `[0.0707, 0.0707, -0.0707, 0.0707, 20.0, 15.25]`

Note: The transformation is applied in the order: scale → shear → rotate → translate.

For more detailed technical information about affine transformations, see:
- [MathWorks documentation](https://www.mathworks.com/discovery/affine-transformation.html)
- [Apache Sedona documentation](https://sedona.apache.org/1.6.1/api/sql/Raster-affine-transformation/)


**DPI and Scaling**:
The API assumes all input images are at 96 DPI (dots per inch) when converting to millimeters. This is important for calculating the correct scale factor:

1. **Base DPI**: All images are treated as 96 DPI when converting to millimeters
2. **Scaling Calculation**:
   - Convert desired output size from millimeters to inches
   - Calculate required pixels at 96 DPI
   - Divide by original image dimensions to get scale factor
   - Example: For 99.82mm × 236.56mm output:
     - Convert to inches: 3.93" × 9.31"
     - At 96 DPI: 377.28 × 894.08 pixels needed
     - If input is 1179 × 2794 pixels
     - Scale factor = 377.28/1179 = 0.32

3. **Two Approaches to Handle Scaling**:
   a. **Using Transform Matrix (Recommended)**:
      - Use transform: `[0.32, 0, 0, 0.32, 0, 0]`
      - Preserves original image resolution
      - Backend uses full resolution for better quality
      - More flexible for combining with other transformations
   
   b. **Pre-scaling the Image**:
      - Resize your image to the target pixel dimensions (e.g., 377×894 pixels)
      - Simpler but may reduce quality if original image is higher resolution
      - Less flexible for combining with other transformations
      
### Process 3D Projected Raster Job (PNG)

#### Endpoint: `/api/jobs/project3d-png-lap`

**Description**: Processes a PNG file with transformation parameters and wraps it onto a 3D mesh surface to create a `.lap` job file.

**Notes**:
This endpoint follows the same PNG transformation, DPI and scaling instructions as the [Process Raster Job (PNG)](#process-raster-job-png) endpoint above. Please refer to that section for detailed information about:
- Base 96 DPI assumptions
- Scaling calculations
- Transform matrix vs. pre-scaling approaches

⚠️ **Warning**: This endpoint works for 3D galvo laser. It will produce lap result with your PNG if you have a 2D galvo laser, but it will result in moving the laser head in Z gantry direction when traveling through the vertical layers of the job.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
  - `transform_params` (str): A JSON string with transformation parameters (`[sx, shy, shx, sy, tx, ty]`) which operates in mm space. These parameters follow the same format and transformation matrix layout as described in the [Process Raster Job (PNG)](#process-raster-job-png) section.

- **Files**:
  - `png_file`: The PNG file to process.
  - `json_file`: A JSON file containing color settings.
  - `mesh_file`: A 3D mesh file (e.g., .obj) onto which the PNG will be projected.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/project3d-png-lap"   -F "pass_code=my-pass-code"   -F "device_access_code=my-device-access-code"   -F "png_file=@path/to/your/image.png"   -F "json_file=@path/to/your/color_settings.json"   -F "mesh_file=@path/to/your/mesh.obj"   -F "transform_params=[0.1, 0, 0, 0.1, 20.0, 15.25]"   --output generated_file.lap
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
### Process GVDesign Job

#### Endpoint: `/api/jobs/standard-gvdesign-lap`

**Description**: Processes a GVDesign file into a `.lap` job file.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
  - `workspace_width_mm` (float, optional): Workspace width in millimeters to place the file at top left of the workspace.
  - `workspace_height_mm` (float, optional): Workspace height in millimeters to place the file at top left of the workspace.
- **Files**:
  - `gvdesign_file`: The GVDesign file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-gvdesign-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_access_code=my-device-access-code" \
  -F "workspace_width_mm=100.0" \
  -F "workspace_height_mm=100.0" \
  -F "gvdesign_file=@path/to/your/file.gvdesign" \
  -F "json_file=@path/to/your/color_settings.json" \
  --output generated_file.lap
```

### Process PDF Job

#### Endpoint: `/api/jobs/standard-pdf-lap`

**Description**: Processes a PDF file into a `.lap` job file.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_access_code` (str): Device access code obtained from device touchscreen.
  - `workspace_width_mm` (float, optional): Workspace width in millimeters to place the file at top left of the workspace.
  - `workspace_height_mm` (float, optional): Workspace height in millimeters to place the file at top left of the workspace.
- **Files**:
  - `pdf_file`: The PDF file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-pdf-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_access_code=my-device-access-code" \
  -F "workspace_width_mm=100.0" \
  -F "workspace_height_mm=100.0" \
  -F "pdf_file=@path/to/your/file.pdf" \
  -F "json_file=@path/to/your/color_settings.json" \
  --output generated_file.lap
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
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_access_code` (str): Device access code obtained from RE4 or the device touchscreen.

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
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_access_code` (str): Device access code obtained from RE4 or the device touchscreen.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/api-query-job-status" \
  -F "pass_code=my-pass-code" \
  -F "device_access_code=my-device-access-code"
```

### Capture Image

Captures an image from the specified device.

**Endpoint:** `/api/jobs/capture-image`

**Method:** `POST`

**Request Body:**

The request should be `multipart/form-data` and include the following fields:

  *   `device_access_code` (string, required): The access code for the device.
  * `pass_code` (string, required): The user's pass code.
  *   `is_corrected` (boolean, optional): Specifies whether the captured image should be corrected. If `true`, the corrected image is returned. Otherwise, the original image is returned. Defaults to `false` if not specified.

**Responses:**

*   **`200 OK`**:
    *   Content-Type: `image/jpeg`
    *   Body: The raw image bytes.
*   **`400 Bad Request` (or other error codes from `validate_device`)**:
    *   Content-Type: `application/json`
    *   Body: JSON object describing the validation error.
    ```json
    {
        "message": "Error message detailing validation failure"
    }
    ```
*   **`500 Internal Server Error`**:
    *   Content-Type: `application/json`
    *   Body: JSON object describing the error.
    ```json
    {
        "message": "Failed to capture image"
    }
    ```

**Example Curl:**

```bash
curl -X POST "YOUR_SERVER_URL/api/jobs/capture-image" \
     -F "pass_code=your_pass_code" \
     -F "device_access_code=your_device_access_code" \
     -F "is_corrected=true" \
     --output captured_image.jpg
```

---

### Gantry Move

#### Endpoint: `/api/jobs/gantry-move`

**Description:** Moves the gantry of a device to a specified position along the X, Y, and/or Z axes (in millimeters).

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_access_code` (str): Device access code obtained from RE4 or the device touchscreen.
  - `x_mm` (float, optional): X position in millimeters. Can be `null` to skip moving along X.
  - `y_mm` (float, optional): Y position in millimeters. Can be `null` to skip moving along Y.
  - `z_mm` (float, optional): Z position in millimeters. Can be `null` to skip moving along Z.

> **Note:** At least one of `x_mm`, `y_mm`, or `z_mm` must be provided (not `null`). If a value is `null`, the gantry will not move along that axis.

This endpoint allows you to move the gantry of a device to a specific position. If you do not wish to move along a particular axis, set its value to `null` or omit it. The endpoint requires a valid device access code for authentication and device selection.

### Example cURL

```sh
curl -X POST "https://your-server/api/jobs/gantry-move" \
  -F "x_mm=100.0" \
  -F "y_mm=50.0" \
  -F "z_mm=" \
  -F "device_access_code=YOUR_DEVICE_ACCESS_CODE"
```

### Success Response

- **Status:** `200 OK`
- **Body:**
  ```json
  {
    "message": "Gantry moved successfully"
  }
  ```

### Error Responses

- **Status:** `500 Internal Server Error`
  ```json
  {
    "message": "An unexpected error occurred while moving the gantry."
  }
  ```
- **Status:** `4xx/5xx` (validation or device errors)
  - Returns a JSON error message describing the issue.

---

### Test Scripts

- Clone the repository and test scripts are in root folder.
- Example scripts are available for each endpoint:
  - `standard_svg.py`
  - `project3d_svg.py`
  - `standard_png.py`
  - `project3d_png.py`
  - `standard_npz_paths2d.py`
  - `standard_npz_points2d.py`
  - `standard_gvdesign.py`
  - `standard_pdf.py`
  - `api_run_lap_job.py`
  - `api_stop_job.py`
  - `api_query_job_status.py`
  - `api_capture_image.py`

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

