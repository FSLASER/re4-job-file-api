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
   - [Get Workspace Bounds](#get-workspace-bounds)
   - [Process Vector Job (SVG)](#process-vector-job-svg)
   - [Process 3D Projected Vector Job (SVG)](#process-3d-projected-vector-job-svg)
   - [Process Raster Job (PNG)](#process-raster-job-png)
   - [Process Paths (NPZ)](#process-paths-npz)
   - [Process Points (NPZ)](#process-points-npz)
   - [Process GVDesign Job](#process-gvdesign-job)
   - [Process PDF Job](#process-pdf-job)
   - [Run LAP Job](#run-lap-job)
   - [Stop Job](#stop-job)
   - [Query Job Status](#query-job-status)
   - [Camera Capture](#capture-image)
   - [Gantry Move](#gantry-move)
   - [GPIO Pins](#gpio-pins)

3. [Test Scripts](#test-scripts)
4. [Contributing](#contributing)

---

## Getting Started

### Prerequisites

- Python 3.8+
- Dependencies listed in `requirements.txt`
- A known Re4/Re4b/beta server compatible with the job file API calls

### Authentication Requirements

- **User Passcode**: Required for all API endpoints. This can be found under your username after logging into the web interface (e.g., [https://beta.fslaser.com](https://beta.fslaser.com)). Note that for different website you will get a different user passcode.
- **Device ID**: Required for all API endpoints. This is a unique identifier for each machine.
  - The device must be added to the device list on the target API website
  - The device must be connected to the website
  - The generated `.lap` file will only work with the correct device
- **Device Auth Code**: Required for most API endpoints (except `get-workspace-bounds`). There are two authentication approaches available:
  - **Option 1 - Skip TOTP (Recommended for same network)**: If your API client is on the same local network as the device, the `device_auth_code` parameter can be omitted or left empty. The API will automatically detect same-network requests and skip TOTP validation.
  - **Option 2 - Use TOTP**: Provide a valid device auth code. This is a time-based one-time password (TOTP) that must be fetched from the device's `/2fa` endpoint.
    - **Getting TOTP Code**: The `/2fa` endpoint requires direct network access to the device's IP address. You must be on the same local network as the device or have VPN/routing access to reach the device's subnet.
    - **Using TOTP Code**: Once you have a valid TOTP code, you can use it from any network to authenticate with the API endpoints. The code has a limited lifespan (5 Minutes) and must be fresh for each API call.
    - Obtained by making a POST request to `https://{device_ip}/2fa` or `http://{device_ip}/2fa`
    - **Note**: Both HTTP and HTTPS work, but HTTPS requires SSL verification to be disabled (`verify=False` in Python, `-k` flag in curl)
    - The response contains a JSON object with a `success` field and nested `totp` object containing the auth code
    - Access the auth code via `response["totp"]["totp"]` after checking `response["success"]`
    - **Example TOTP Response**:
      ```json
      {
        "success": true,
        "totp": {
          "totp": "565244",
          "expire_time": 1757444100,
          "expire_time_str": "2025-09-09 11:55:00"
        }
      }
      ```

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

> **📝 Note**: For all endpoints that require `device_auth_code`, you have two authentication options: (1) Omit the `device_auth_code` parameter when your API client is on the same local network as the device - the API will automatically detect this and skip TOTP validation, or (2) Provide a `device_auth_code` obtained from the device's `/2fa` endpoint. Note that getting the TOTP code requires same-network access to the device, but once obtained, the code can be used from any network. Note the code refreshes every 5 minutes on the device.

> **💡 Tip**: You can omit the `device_auth_code` line entirely if you prefer not to use TOTP authentication. The API will automatically detect same-network requests and skip TOTP validation.

### Get Workspace Bounds

#### Endpoint: `/api/jobs/get-workspace-bounds`

**Description**: Retrieves the workspace bounds information from the specified device.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `device_id` (str): Device ID for authentication.

**Response**:
- Returns JSON data containing workspace bounds information for the device

**Example JSON Response**:
```json
{
  "workspaceX_mm_min": -50.0,
  "workspaceX_mm_max": 50.0,
  "workspaceY_mm_min": -50.0,
  "workspaceY_mm_max": 50.0
}
```

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/get-workspace-bounds" \
  -F "device_id=AE356O3E89D"
```

### Process Vector Job (SVG)

#### Endpoint: `/api/jobs/standard-svg-lap`

**Description**: Processes an SVG file **(contain vector paths only, endpoint will ignore raster data)** into a `.lap` job file.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `workspaceX_mm_min` (float, optional): Workspace X min in millimeters to position the file in the workspace correctly.
  - `workspaceX_mm_max` (float, optional): Workspace X max in millimeters to position the file in the workspace correctly.
  - `workspaceY_mm_min` (float, optional): Workspace Y min in millimeters to position the file in the workspace correctly.
  - `workspaceY_mm_max` (float, optional): Workspace Y max in millimeters to position the file in the workspace correctly.
- **Files**:
  - `svg_file`: The SVG file to process.
  - `json_file`: A JSON file containing color settings.

#### Example CURL (standard-svg-lap)

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-svg-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "workspaceX_mm_min=-50.0" \
  -F "workspaceX_mm_max=50.0" \
  -F "workspaceY_mm_min=-50.0" \
  -F "workspaceY_mm_max=50.0" \
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
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `workspaceX_mm_min` (float, optional): Workspace X min in millimeters to position the file in the workspace correctly.
  - `workspaceX_mm_max` (float, optional): Workspace X max in millimeters to position the file in the workspace correctly.
  - `workspaceY_mm_min` (float, optional): Workspace Y min in millimeters to position the file in the workspace correctly.
  - `workspaceY_mm_max` (float, optional): Workspace Y max in millimeters to position the file in the workspace correctly.
- **Files**:
  - `svg_file`: The SVG file to process.
  - `json_file`: A JSON file containing color settings.
  - `mesh_file`: A 3D mesh file (e.g., .obj) onto which the SVG will be projected.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/project3d-svg-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "workspaceX_mm_min=-50.0" \
  -F "workspaceX_mm_max=50.0" \
  -F "workspaceY_mm_min=-50.0" \
  -F "workspaceY_mm_max=50.0" \
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
  - `device_id` (str): Device ID for authentication.
  - `transform_params` (str): A JSON string with transformation parameters (`[sx, shy, shx, sy, tx, ty]`) which operates in mm space.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
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

#### Example CURL (standard-png-lap)

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-png-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "png_file=@path/to/your/image.png" \
  -F "json_file=@path/to/your/color_settings.json" \
  -F "transform_params=[0.1, 0, 0, 0.1, 20.0, 15.25]" \
  --output generated_file.lap
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

### Process Paths (NPZ)

#### Endpoint: `/api/jobs/standard-npz-paths2d-lap`

**Description**: Processes an NPZ file containing vector data into a `.lap` job file. Key name in NPZ file indicating vector data must be `paths`.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `color` (str): Stroke color for the vector paths.
- **Files**:
  - `npz_file`: The NPZ file containing vector paths.
  - `json_file`: A JSON file containing color settings.

#### Example CURL (standard-npz-paths2d-lap)

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-npz-paths2d-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "npz_file=@path/to/your/file.npz" \
  -F "json_file=@path/to/your/color_settings.json" \
  -F "color=#FF5733" \
  --output generated_file.lap
```

### Process Points (NPZ)

#### Endpoint: `/api/jobs/standard-npz-points2d-lap`

**Description**: Processes an NPZ file containing raster data into a `.lap` job file. Key name in NPZ file indicating raster data must be `points`.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
- **Files**:
  - `npz_file`: The NPZ file containing vector paths.
  - `json_file`: A JSON file containing color settings.

#### Example CURL (standard-npz-points2d-lap)

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-npz-points2d-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "npz_file=@path/to/your/file.npz" \
  -F "json_file=@path/to/your/color_settings.json" \
  --output generated_file.lap
```

### Process GVDesign Job

#### Endpoint: `/api/jobs/standard-gvdesign-lap`

**Description**: Processes a GVDesign file into a `.lap` job file.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): User pass code for authentication obtained from the API website under username.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `workspaceX_mm_min` (float, optional): Workspace X min in millimeters to position the file in the workspace correctly.
  - `workspaceX_mm_max` (float, optional): Workspace X max in millimeters to position the file in the workspace correctly.
  - `workspaceY_mm_min` (float, optional): Workspace Y min in millimeters to position the file in the workspace correctly.
  - `workspaceY_mm_max` (float, optional): Workspace Y max in millimeters to position the file in the workspace correctly.
- **Files**:
  - `gvdesign_file`: The GVDesign file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-gvdesign-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "workspaceX_mm_min=-50.0" \
  -F "workspaceX_mm_max=50.0" \
  -F "workspaceY_mm_min=-50.0" \
  -F "workspaceY_mm_max=50.0" \
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
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `workspaceX_mm_min` (float, optional): Workspace X min in millimeters to position the file in the workspace correctly.
  - `workspaceX_mm_max` (float, optional): Workspace X max in millimeters to position the file in the workspace correctly.
  - `workspaceY_mm_min` (float, optional): Workspace Y min in millimeters to position the file in the workspace correctly.
  - `workspaceY_mm_max` (float, optional): Workspace Y max in millimeters to position the file in the workspace correctly.
- **Files**:
  - `pdf_file`: The PDF file to process.
  - `json_file`: A JSON file containing color settings.

**Example cURL**:

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/standard-pdf-lap" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "workspaceX_mm_min=-50.0" \
  -F "workspaceX_mm_max=50.0" \
  -F "workspaceY_mm_min=-50.0" \
  -F "workspaceY_mm_max=50.0" \
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
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
- **Files**:
  - `lap_file`: The `.lap` file to execute.

#### Example CURL (api-run-lap-job)

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/api-run-lap-job" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "lap_file=@path/to/your/job.lap"
```

### Stop Job

#### Endpoint: `/api/jobs/api-stop-job`

**Description**: Stops the currently running job on the laser machine.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).

#### Example CURL (api-stop-job)

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/api-stop-job" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
```

### Query Job Status

#### Endpoint: `/api/jobs/api-query-job-status`

**Description**: Retrieves the current status of the job running on the laser machine.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).

#### Example CURL (api-query-job-status)

```bash
curl -X POST "https://beta.fslaser.com/api/jobs/api-query-job-status" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
```

### Capture Image

Captures an image from the specified device.

**Endpoint:** `/api/jobs/capture-image`

**Method:** `POST`

**Request Body:**

The request should be `multipart/form-data` and include the following fields:

- `device_id` (string, required): The id (MAC address) for the device.
- `pass_code` (string, required): The user's pass code.
- `device_auth_code` (string, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Only required when API caller is on a different network than the device.
- `is_corrected` (boolean, optional): Specifies whether the captured image should be corrected. If `true`, the corrected image is returned. Otherwise, the original image is returned. Defaults to `false` if not specified.

**Responses:**

- **`200 OK`**:
  - Content-Type: `image/jpeg`
  - Body: The raw image bytes.
- **`400 Bad Request` (or other error codes from `validate_device`)**:
  - Content-Type: `application/json`
  - Body: JSON object describing the validation error.

    ```json
    {
        "message": "Error message detailing validation failure"
    }
    ```

- **`500 Internal Server Error`**:
  - Content-Type: `application/json`
  - Body: JSON object describing the error.

    ```json
    {
        "message": "Failed to capture image"
    }
    ```

#### Example CURL (capture-image)

```bash
curl -X POST "YOUR_SERVER_URL/api/jobs/capture-image" \
     -F "pass_code=your_pass_code" \
     -F "device_id=your_device_id" \
     -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
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
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `x_mm` (float, optional): X position in millimeters. Can be `null` to skip moving along X.
  - `y_mm` (float, optional): Y position in millimeters. Can be `null` to skip moving along Y.
  - `z_mm` (float, optional): Z position in millimeters. Can be `null` to skip moving along Z.

> **Note:** At least one of `x_mm`, `y_mm`, or `z_mm` must be provided (not `null`). If a value is `null`, the gantry will not move along that axis.

This endpoint allows you to move the gantry of a device to a specific position. If you do not wish to move along a particular axis, set its value to `null` or omit it. The endpoint requires a valid device ID for authentication and device selection.

#### Example CURL (gantry-move)

```sh
curl -X POST "https://your-server/api/jobs/gantry-move" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "x_mm=100.0" \
  -F "y_mm=50.0" \
  -F "z_mm=" \
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

### GPIO Pins

#### Endpoint: `/api/jobs/set-gpio`

**Description:** Sets the specified GPIO pin high.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `gpio_pin` (int): The pin to set.

#### Example cURL (set-gpio)

```sh
curl -X POST "https://beta.fslaser.com/api/jobs/set-gpio" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "gpio_pin=1"
```

**Success Response**:

- **Status:** `200 OK`

**Error Responses**:

- **Status:** `4xx/5xx` (validation or device errors)
  - Returns a JSON error message describing the issue.

#### Endpoint: `/api/jobs/clear-gpio`

**Description:** Sets the specified GPIO pin low.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `gpio_pin` (int): The pin to clear.

#### Example CURL (clear-gpio)

```sh
curl -X POST "https://beta.fslaser.com/api/jobs/clear-gpio" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "gpio_pin=1"
```

**Success Response**:

- **Status:** `200 OK`

**Error Responses**:

- **Status:** `4xx/5xx` (validation or device errors)
  - Returns a JSON error message describing the issue.

#### Endpoint: `/api/jobs/get-gpio`

**Description:** Gets the status of the specified GPIO pin.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `gpio_pin` (int): The pin to get.

#### Example CURL (get-gpio)

```sh
curl -X POST "https://beta.fslaser.com/api/jobs/get-gpio" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "gpio_pin=1"
```

**Success Response**:

- **Status:** `200 OK`
- **Body:**

  ```json
  {
    "gpio_state": int
  }
  ```

**Error Responses**:

- **Status:** `4xx/5xx` (validation or device errors)
  - Returns a JSON error message describing the issue.

#### Endpoint: `/api/jobs/blink-gpio`

**Description:** Blinks the specified GPIO pin high with the specified duration.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `gpio_pin` (int): The pin to set.
  - `blink_duration_ms` (int, optional): The duration of the blink in milliseconds. Default is 1000, if not specified.

#### Example cURL (blink-gpio)

```sh
curl -X POST "https://beta.fslaser.com/api/jobs/blink-gpio" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "gpio_pin=1" \
  -F "blink_duration_ms=250"
```

**Success Response**:

- **Status:** `200 OK`

**Error Responses**:

- **Status:** `4xx/5xx` (validation or device errors)
  - Returns a JSON error message describing the issue.

#### Endpoint: `/api/jobs/send-gpio`

**Description:** Sends the specified command.

**Method**: `POST`

**Request Parameters**:

- **Form Fields**:
  - `pass_code` (str): The user's pass code obtained from RE4.
  - `device_id` (str): Device ID for authentication.
  - `device_auth_code` (str, optional): Device authentication code obtained from `http://{device_ip}/2fa` endpoint (lifespan 5 min). Can be omitted for same-network requests (API will auto-detect and skip TOTP validation).
  - `gpio_command` (str): The command to send.

#### Example cURL (send-gpio)

```sh
curl -X POST "https://beta.fslaser.com/api/jobs/send-gpio" \
  -F "pass_code=my-pass-code" \
  -F "device_id=AE356O3E89D" \
  -F "device_auth_code=$(curl -s -k https://192.168.1.100/2fa | jq -r '.totp.totp')" \
  -F "gpio_command=set pin1"
```

**Success Response**:

- **Status:** `200 OK`

**Error Responses**:

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
  - `api_gpio.py`

#### Running a Test Script

```bash
python standard_svg.py
```

Before running any script, make sure to:

1. Update the `pass_code` with your user passcode from the website
2. Update the `device_id` with your device's unique ID
3. Set the correct paths for input and output files

---

## Contributing

We welcome contributions! Please fork the repository and create a pull request for your changes. Ensure that your code adheres to the following guidelines:

1. Follow PEP 8 coding standards.
2. Write clear and concise documentation for new functions or features.
3. Include test scripts for new functionality.

---

For further assistance or questions, please [open an issue](https://github.com/your-username/re4-job-file-api/issues).
