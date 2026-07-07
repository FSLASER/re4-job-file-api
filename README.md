# FSL Job File API

HTTP API for running laser jobs headlessly on Full Spectrum Laser machines —
no browser, no RE5 UI. Upload a design file (**SVG / DXF / PDF / PNG / FSL5 /
GVDesign / NPZ**) plus a settings JSON, get back a `.lap` job file, and run it
on your machine. Also: job status/stop, camera capture, gantry moves, GPIO.

The API is served by the RE5 server — default **`https://re5.fslaser.com`**
(the examples below use it; `beta.fslaser.com` works the same way).

> This repo was historically called *re4-job-file-api*; the same endpoints
> now live on the RE5 servers and this client targets those.

## Quick start

```bash
git clone https://github.com/FSLASER/re4-job-file-api.git
cd re4-job-file-api
pip install -r requirements.txt

export FSL_PASS_CODE="your-pass-code"   # shown under your username on the website
export FSL_DEVICE_ID="AABBCCDDEEFF"     # your device id from the device list
# export FSL_SERVER="https://re5.fslaser.com"   # default

# 1) design file + settings -> .lap
python3 fsl_api.py lap design.svg -s color_settings.json -o design.lap

# 2) run it
python3 fsl_api.py run design.lap

# or both in one step:
python3 fsl_api.py job design.svg -s color_settings.json
```

`fsl_api.py` is both a CLI and an importable library:

```python
from fsl_api import FSLJobFileAPI

api = FSLJobFileAPI(pass_code="...", device_id="...")   # or env vars
lap = api.file_to_lap("design.dxf", "color_settings.json")
api.run_lap(lap)
print(api.job_status())
```

Other CLI commands: `bounds`, `status`, `stop`, `capture`, `gantry`,
`gpio`, `totp` — run `python3 fsl_api.py --help`.

## Authentication

Every endpoint (except `get-workspace-bounds`) needs:

| Credential | Where to get it |
|---|---|
| `pass_code` | Log into the website (e.g. re5.fslaser.com); it's shown under your username. Pass codes are **per-site** — a beta pass code won't work on re5. |
| `device_id` | Your machine's id from the website's device list. The device must be added to your account **and currently connected** to that site. |
| `device_auth_code` | **Optional.** Only needed when the API caller is on a *different network* than the device. |

**Same network (recommended):** if your client is on the same LAN as the
device, omit `device_auth_code` entirely — the server detects the shared
network and skips TOTP.

**Different network:** fetch a TOTP from the device itself (requires LAN/VPN
access to the device at least once per code):

```bash
curl -s -k https://DEVICE_IP/2fa | jq -r '.totp.totp'    # valid ~5 minutes
# or: python3 fsl_api.py totp --device-ip DEVICE_IP
# or pass --totp auto to any CLI command (uses FSL_DEVICE_IP)
```

## The settings JSON

Every LAP-generation endpoint takes a `json_file` with the engraving
settings. It is the same format as the `settings.json` embedded in RE5
`.fsl5` project archives — `color_settings.json` in this repo is a working
template. The parts you'll usually edit:

```jsonc
{
  "version": "2",
  "global":  { "jobType": "Default", "jobPasses": 1, ... },
  "raster":  { "dpi": 250, "power_percent": 50, "speed_mms": 500, "passes": 1, ... },
  "vector":  {
    // one entry per stroke color in your design:
    "#000000": {
      "order": 0,             // engraving order across colors
      "colorPasses": 1,
      "speed_mms": 300,
      "power_percent": 20,
      "frequency_kHz": 67,    // fiber/galvo lasers
      "infill":  { "infill_type": "none", ... },
      "wobble":  { "isEnabled": false, ... }
    }
  }
}
```

- **Vector paths** are matched to `vector` entries by their stroke color.
  A color present in the file but absent from the JSON is skipped.
- **Raster images** (PNG, images inside PDFs/FSL5) use the `raster` section.
- Easiest way to get a tuned settings file: build the job once in RE5, save
  the project (`.fsl5` is a ZIP), and pull `settings.json` out of it.

## Supported design files

| Type | Endpoint | Notes |
|---|---|---|
| `.svg` | `standard-svg-lap` | Vector paths (lines + cubic béziers). 96 DPI assumed. |
| `.dxf` | `standard-dxf-lap` | Converted server-side (same converter RE5 import uses). Units = mm; all paths come out **black (`#000000`)** — give the settings JSON a `#000000` entry. |
| `.pdf` | `standard-pdf-lap` | Vector paths *and* embedded raster images preserved (pdf2lvx pipeline). 96 DPI. |
| `.png` | `standard-png-lap` | Raster. Requires `transform_params` (see below). 96 DPI base. |
| `.fsl5` | `standard-fsl5-lap` | **RE5 project archive — highest fidelity.** Settings JSON optional (falls back to the `settings.json` inside the archive); workspace bounds default to the device's own. Design in RE5, save, run via API. |
| `.gvdesign` | `standard-gvdesign-lap` | Legacy RE4 project format. |
| `.npz` (key `paths`) | `standard-npz-paths2d-lap` | Object array of `(n_points, 2)` float arrays, mm. Pass a `color` to select the settings entry. |
| `.npz` (key `points`) | `standard-npz-points2d-lap` | `(N, 2)` float array, mm — engraved as a point cloud. |

**A note on file import fidelity:** the RE5 editor imports DXF/PDF in the
browser with WASM importers. A headless API client can't run those, so the
API converts server-side with the same `py_gravit_convert` converters that
back RE5's server import endpoints. For anything complex (text, images,
multi-color layouts, exact placement), the recommended path is: **import and
arrange in RE5 → save project → submit the `.fsl5` to
`standard-fsl5-lap`** — that runs the exact same geometry the editor shows,
including embedded per-color settings.

## Endpoint reference

All endpoints are `POST` with `multipart/form-data` under
`https://re5.fslaser.com/api/jobs/`. Auth form fields (`pass_code`,
`device_id`, optional `device_auth_code`) are implied below — see
[Authentication](#authentication).

### LAP generation

All LAP endpoints stream back the binary `.lap` on success (save it with
`--output file.lap`) and return a JSON `{"message": ...}` body on error.
⚠️ A LAP is signed **for the device that generated it** — it will only run
on the `device_id` you passed.

**`standard-svg-lap`** / **`standard-dxf-lap`** / **`standard-pdf-lap`** /
**`standard-gvdesign-lap`** / **`standard-fsl5-lap`**

- Files: `svg_file` / `dxf_file` / `pdf_file` / `gvdesign_file` / `fsl5_file`, plus `json_file`
- Optional workspace placement fields (mm): `workspaceX_mm_min`,
  `workspaceX_mm_max`, `workspaceY_mm_min`, `workspaceY_mm_max`
  (get real values from `get-workspace-bounds`)

```bash
curl -X POST "https://re5.fslaser.com/api/jobs/standard-svg-lap" \
  -F "pass_code=$FSL_PASS_CODE" -F "device_id=$FSL_DEVICE_ID" \
  -F "workspaceX_mm_min=-50" -F "workspaceX_mm_max=50" \
  -F "workspaceY_mm_min=-50" -F "workspaceY_mm_max=50" \
  -F "svg_file=@design.svg" -F "json_file=@color_settings.json" \
  --output design.lap
```

**`standard-png-lap`** — files: `png_file`, `json_file`; field
`transform_params`: JSON array `[sx, shy, shx, sy, tx, ty]` mapping image
pixels (96 DPI, origin top-left) into device mm space:

```text
[scaleX  shearX  translateX]      e.g. scale 0.5 + move 20mm right:
[shearY  scaleY  translateY]      [0.5, 0, 0, 0.5, 20.0, 0]
[0       0       1         ]      rotate 90° CW: [0, 1, -1, 0, 0, 0]
```

Sizing example: for a 1179×2794 px image to come out 99.8×236.6 mm at the
96 DPI base: `scale = (99.8/25.4*96)/1179 ≈ 0.32` → `[0.32,0,0,0.32,0,0]`.

**`standard-npz-paths2d-lap`** — files: `npz_file` (key `paths`),
`json_file`; field `color` (e.g. `#000000`) selects the vector settings
entry. **`standard-npz-points2d-lap`** — files: `npz_file` (key `points`),
`json_file`.

**`project3d-svg-lap`** / **`project3d-png-lap`** — like their standard
counterparts plus `mesh_file` (`.obj`); wraps the design onto the 3D mesh.
3D-galvo machines only (others get an empty LAP).

### Job control

| Endpoint | Fields | Returns |
|---|---|---|
| `api-run-lap-job` | file `lap_file`, optional `soft_limit_check` (bool) | `{"message": "Job started successfully", ...}` — device must be **idle** and connected |
| `api-stop-job` | — | stop result |
| `api-query-job-status` | — | `{"user_job_status": "idle" \| "processing" \| ...}` |
| `get-workspace-bounds` | only `device_id` (no pass_code) | `{"workspaceX_mm_min": -50.0, ...}` |

### Device utilities

| Endpoint | Fields | Returns |
|---|---|---|
| `capture-image` | optional `is_corrected` (bool) | JPEG bytes |
| `gantry-move` | `x_mm`, `y_mm`, `z_mm` — each optional; omit or send empty to skip an axis (at least one required) | `{"message": "Gantry moved successfully"}` |
| `set-gpio` / `clear-gpio` / `get-gpio` | `gpio_pin` (int) | 200 / `{"gpio_state": int}` |
| `blink-gpio` | `gpio_pin`, optional `blink_duration_ms` (default 1000) | 200 |
| `send-gpio` | `gpio_command` (str) | 200 |

## Legacy example scripts

The original per-endpoint scripts (`standard_svg.py`, `standard_png.py`,
`api_run_lap_job.py`, …) still work and show raw `requests` usage, but they
have hard-coded credentials/paths at the bottom — edit before running.
New integrations should use `fsl_api.py`.

## Troubleshooting

- **HTTP 405 on every endpoint** — the server is running a build with the
  deferred-router bug (routes shadowed by the static-file mount). Fixed in
  habanero `server/_main.py`; the server needs that version deployed.
- **"Invalid pass_code"** — pass codes are per-site; get yours from the same
  site you're calling.
- **"User device association not found"** — add the device to your account
  on the website.
- **"Device not active"** — the machine must be powered on and connected to
  the site (`api-run-lap-job`, `capture-image`, etc. need a live device;
  LAP generation needs the device known + connected so the LAP can be signed).
- **"Invalid device auth code"** — TOTP expired (5 min lifespan) or from the
  wrong device. Same-network callers should omit it entirely.
- **Job fails to start with a LAP from another machine** — LAPs are signed
  per-device; regenerate with the right `device_id`.

## Contributing

PRs welcome. Follow PEP 8, document new endpoints in this README, and add a
test to habanero's `server/tests/test_jobs_api.py` for server-side changes.
