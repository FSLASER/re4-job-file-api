#!/usr/bin/env python3
"""FSL Job File API client — library + CLI.

Talks to the /api/jobs/* endpoints on an RE5 server (default:
https://re5.fslaser.com). Core flow: upload a design file (svg / dxf / pdf /
png / fsl5 / gvdesign / npz) + a settings JSON, receive a .lap job file,
then run it on your machine.

Configuration (constructor args, CLI flags, or environment variables):
    FSL_SERVER      server URL           (default https://re5.fslaser.com)
    FSL_PASS_CODE   user pass code       (shown under your username on the site)
    FSL_DEVICE_ID   device id            (device list on the site)
    FSL_DEVICE_IP   device LAN IP        (only needed for TOTP when calling
                                          from a different network)

Quick start (same LAN as the device — no TOTP needed):
    export FSL_PASS_CODE=... FSL_DEVICE_ID=...
    python3 fsl_api.py lap design.svg -s color_settings.json -o design.lap
    python3 fsl_api.py run design.lap
    # or both in one step:
    python3 fsl_api.py job design.svg -s color_settings.json

Only dependency: requests
"""
import argparse
import json
import os
import sys

import requests

DEFAULT_SERVER = "https://re5.fslaser.com"

# design-file extension -> (endpoint, form field name)
FILE_ENDPOINTS = {
    ".svg": ("/api/jobs/standard-svg-lap", "svg_file"),
    ".dxf": ("/api/jobs/standard-dxf-lap", "dxf_file"),
    ".pdf": ("/api/jobs/standard-pdf-lap", "pdf_file"),
    ".png": ("/api/jobs/standard-png-lap", "png_file"),
    ".fsl5": ("/api/jobs/standard-fsl5-lap", "fsl5_file"),
    ".gvdesign": ("/api/jobs/standard-gvdesign-lap", "gvdesign_file"),
}


class ApiError(RuntimeError):
    """Raised when the server answers with an error; .body holds the JSON."""

    def __init__(self, message, status_code=None, body=None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class FSLJobFileAPI:
    def __init__(self, server=None, pass_code=None, device_id=None,
                 device_ip=None, device_auth_code=None, timeout=330):
        self.server = (server or os.environ.get("FSL_SERVER") or DEFAULT_SERVER).rstrip("/")
        self.pass_code = pass_code or os.environ.get("FSL_PASS_CODE")
        self.device_id = device_id or os.environ.get("FSL_DEVICE_ID")
        self.device_ip = device_ip or os.environ.get("FSL_DEVICE_IP")
        self.device_auth_code = device_auth_code
        self.timeout = timeout

    # ── auth ────────────────────────────────────────────────────────────

    def get_device_auth_code(self):
        """Fetch a fresh TOTP from the device's /2fa endpoint (device LAN only).

        Only needed when the API caller is NOT on the same network as the
        device; same-network callers can omit the auth code entirely.
        """
        if not self.device_ip:
            raise ApiError("device_ip (FSL_DEVICE_IP) is required to fetch a TOTP code")
        last_error = None
        for scheme in ("https", "http"):
            try:
                r = requests.post(f"{scheme}://{self.device_ip}/2fa", verify=False, timeout=10)
                data = r.json()
                if data.get("success"):
                    return data["totp"]["totp"]
                last_error = ApiError(f"/2fa returned {data}")
            except Exception as e:  # noqa: BLE001 - try the other scheme
                last_error = e
        raise ApiError(f"Could not fetch TOTP from {self.device_ip}/2fa: {last_error}")

    def _auth_fields(self, need_pass_code=True):
        fields = {}
        if need_pass_code:
            if not self.pass_code:
                raise ApiError("pass_code is required (set FSL_PASS_CODE or --pass-code)")
            fields["pass_code"] = self.pass_code
        if not self.device_id:
            raise ApiError("device_id is required (set FSL_DEVICE_ID or --device-id)")
        fields["device_id"] = self.device_id
        code = self.device_auth_code
        if code == "auto":
            code = self.get_device_auth_code()
        if code:
            fields["device_auth_code"] = code
        return fields

    # ── plumbing ────────────────────────────────────────────────────────

    def _post(self, path, data=None, files=None, need_pass_code=True, stream_to=None):
        url = self.server + path
        payload = self._auth_fields(need_pass_code=need_pass_code)
        payload.update(data or {})
        r = requests.post(url, data=payload, files=files, timeout=self.timeout)
        content_type = r.headers.get("content-type", "")
        if r.status_code != 200:
            body = r.json() if content_type.startswith("application/json") else {"raw": r.text[:500]}
            raise ApiError(f"{path} -> HTTP {r.status_code}: {body.get('message', body)}",
                           status_code=r.status_code, body=body)
        if stream_to:
            # A JSON body on 200 would mean an error dressed as success — guard it.
            if content_type.startswith("application/json"):
                raise ApiError(f"{path} returned JSON instead of a file: {r.text[:500]}")
            with open(stream_to, "wb") as f:
                f.write(r.content)
            return stream_to
        return r.json() if content_type.startswith("application/json") else r.content

    @staticmethod
    def _workspace_fields(workspace):
        """workspace = (x_min, x_max, y_min, y_max) in mm, or None."""
        if not workspace:
            return {}
        x_min, x_max, y_min, y_max = workspace
        return {
            "workspaceX_mm_min": x_min, "workspaceX_mm_max": x_max,
            "workspaceY_mm_min": y_min, "workspaceY_mm_max": y_max,
        }

    # ── info ────────────────────────────────────────────────────────────

    def get_workspace_bounds(self):
        """Workspace bounds of the device (no pass_code required)."""
        return self._post("/api/jobs/get-workspace-bounds", need_pass_code=False)

    def job_status(self):
        return self._post("/api/jobs/api-query-job-status")

    # ── file → LAP ──────────────────────────────────────────────────────

    def file_to_lap(self, design_path, settings_path=None, out_path=None,
                    workspace=None, transform=None, npz_color="#000000"):
        """Convert a design file into a .lap using the endpoint matching its
        extension. Returns the output path.

        transform: only for .png — [sx, shy, shx, sy, tx, ty] affine (mm space).
        npz_color: only for .npz paths files — stroke color to assign.
        settings_path: optional for .fsl5 (falls back to the embedded settings.json).
        """
        ext = os.path.splitext(design_path)[1].lower()
        out_path = out_path or os.path.splitext(design_path)[0] + ".lap"

        if ext == ".npz":
            return self._npz_to_lap(design_path, settings_path, out_path, npz_color)
        if ext not in FILE_ENDPOINTS:
            raise ApiError(f"Unsupported design file type: {ext}. "
                           f"Supported: {', '.join(FILE_ENDPOINTS)}, .npz")
        endpoint, field = FILE_ENDPOINTS[ext]

        data = self._workspace_fields(workspace)
        if ext == ".png":
            data["transform_params"] = json.dumps(list(transform or (1, 0, 0, 1, 0, 0)))

        files = {field: open(design_path, "rb")}
        if settings_path:
            files["json_file"] = open(settings_path, "rb")
        elif ext != ".fsl5":
            raise ApiError(f"settings JSON is required for {ext} files")
        try:
            return self._post(endpoint, data=data, files=files, stream_to=out_path)
        finally:
            for f in files.values():
                f.close()

    def _npz_to_lap(self, npz_path, settings_path, out_path, color):
        import numpy as np  # optional dep, only for npz introspection
        keys = np.load(npz_path, allow_pickle=True).files
        if "paths" in keys:
            endpoint, extra = "/api/jobs/standard-npz-paths2d-lap", {"color": color}
        elif "points" in keys:
            endpoint, extra = "/api/jobs/standard-npz-points2d-lap", {}
        else:
            raise ApiError(f"NPZ must contain a 'paths' or 'points' key, has: {keys}")
        if not settings_path:
            raise ApiError("settings JSON is required for .npz files")
        with open(npz_path, "rb") as nf, open(settings_path, "rb") as sf:
            return self._post(endpoint, data=extra,
                              files={"npz_file": nf, "json_file": sf},
                              stream_to=out_path)

    # ── run / control ───────────────────────────────────────────────────

    def run_lap(self, lap_path, soft_limit_check=False):
        """Run a .lap on the device. The LAP must have been generated for
        this same device_id."""
        with open(lap_path, "rb") as f:
            return self._post("/api/jobs/api-run-lap-job",
                              data={"soft_limit_check": json.dumps(bool(soft_limit_check))},
                              files={"lap_file": f})

    def stop_job(self):
        return self._post("/api/jobs/api-stop-job")

    def capture_image(self, out_path="capture.jpg", corrected=False):
        return self._post("/api/jobs/capture-image",
                          data={"is_corrected": json.dumps(bool(corrected))},
                          stream_to=out_path)

    def gantry_move(self, x_mm=None, y_mm=None, z_mm=None):
        data = {}
        if x_mm is not None:
            data["x_mm"] = x_mm
        if y_mm is not None:
            data["y_mm"] = y_mm
        if z_mm is not None:
            data["z_mm"] = z_mm
        if not data:
            raise ApiError("at least one of x_mm / y_mm / z_mm is required")
        return self._post("/api/jobs/gantry-move", data=data)

    def gpio(self, action, pin=None, blink_duration_ms=None, command=None):
        """action: set | clear | get | blink | send"""
        if action == "send":
            return self._post("/api/jobs/send-gpio", data={"gpio_command": command})
        data = {"gpio_pin": pin}
        if action == "blink" and blink_duration_ms is not None:
            data["blink_duration_ms"] = blink_duration_ms
        return self._post(f"/api/jobs/{action}-gpio", data=data)


# ── CLI ────────────────────────────────────────────────────────────────────

def _build_parser():
    p = argparse.ArgumentParser(
        description="FSL Job File API client (see README.md)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--server", default=None, help="server URL (env FSL_SERVER)")
    p.add_argument("--pass-code", default=None, help="user pass code (env FSL_PASS_CODE)")
    p.add_argument("--device-id", default=None, help="device id (env FSL_DEVICE_ID)")
    p.add_argument("--device-ip", default=None, help="device LAN IP for TOTP (env FSL_DEVICE_IP)")
    p.add_argument("--totp", default=None,
                   help="device auth code, or 'auto' to fetch from the device's /2fa "
                        "(omit entirely when on the same network as the device)")
    sub = p.add_subparsers(dest="cmd", required=True)

    lap = sub.add_parser("lap", help="convert a design file to a .lap")
    lap.add_argument("design", help="svg/dxf/pdf/png/fsl5/gvdesign/npz file")
    lap.add_argument("-s", "--settings", help="settings JSON (optional for .fsl5)")
    lap.add_argument("-o", "--output", help="output .lap path")
    lap.add_argument("--workspace", nargs=4, type=float,
                     metavar=("XMIN", "XMAX", "YMIN", "YMAX"),
                     help="workspace bounds in mm")
    lap.add_argument("--transform", nargs=6, type=float,
                     metavar=("SX", "SHY", "SHX", "SY", "TX", "TY"),
                     help="png only: affine transform in mm space")
    lap.add_argument("--color", default="#000000", help="npz paths only: stroke color")

    job = sub.add_parser("job", help="convert a design file to .lap AND run it")
    for a in ("design",):
        job.add_argument(a)
    job.add_argument("-s", "--settings")
    job.add_argument("-o", "--output")
    job.add_argument("--workspace", nargs=4, type=float,
                     metavar=("XMIN", "XMAX", "YMIN", "YMAX"))
    job.add_argument("--transform", nargs=6, type=float,
                     metavar=("SX", "SHY", "SHX", "SY", "TX", "TY"))
    job.add_argument("--color", default="#000000")
    job.add_argument("--soft-limit-check", action="store_true")

    run = sub.add_parser("run", help="run an existing .lap file")
    run.add_argument("lap")
    run.add_argument("--soft-limit-check", action="store_true")

    sub.add_parser("stop", help="stop the current job")
    sub.add_parser("status", help="query job status")
    sub.add_parser("bounds", help="get device workspace bounds")
    sub.add_parser("totp", help="fetch a TOTP auth code from the device (needs --device-ip)")

    cap = sub.add_parser("capture", help="capture a camera image")
    cap.add_argument("-o", "--output", default="capture.jpg")
    cap.add_argument("--corrected", action="store_true")

    move = sub.add_parser("gantry", help="move the gantry (mm)")
    move.add_argument("-x", type=float, default=None)
    move.add_argument("-y", type=float, default=None)
    move.add_argument("-z", type=float, default=None)

    gpio = sub.add_parser("gpio", help="GPIO control")
    gpio.add_argument("action", choices=["set", "clear", "get", "blink", "send"])
    gpio.add_argument("--pin", type=int)
    gpio.add_argument("--duration-ms", type=int, default=1000)
    gpio.add_argument("--command", help="raw command for 'send'")
    return p


def main(argv=None):
    args = _build_parser().parse_args(argv)
    api = FSLJobFileAPI(server=args.server, pass_code=args.pass_code,
                        device_id=args.device_id, device_ip=args.device_ip,
                        device_auth_code=args.totp)
    try:
        if args.cmd == "lap":
            out = api.file_to_lap(args.design, args.settings, args.output,
                                  workspace=tuple(args.workspace) if args.workspace else None,
                                  transform=tuple(args.transform) if args.transform else None,
                                  npz_color=args.color)
            print(f"LAP saved to {out}")
        elif args.cmd == "job":
            out = api.file_to_lap(args.design, args.settings, args.output,
                                  workspace=tuple(args.workspace) if args.workspace else None,
                                  transform=tuple(args.transform) if args.transform else None,
                                  npz_color=args.color)
            print(f"LAP saved to {out} — starting job...")
            print(json.dumps(api.run_lap(out, args.soft_limit_check), indent=2))
        elif args.cmd == "run":
            print(json.dumps(api.run_lap(args.lap, args.soft_limit_check), indent=2))
        elif args.cmd == "stop":
            print(json.dumps(api.stop_job(), indent=2))
        elif args.cmd == "status":
            print(json.dumps(api.job_status(), indent=2))
        elif args.cmd == "bounds":
            print(json.dumps(api.get_workspace_bounds(), indent=2))
        elif args.cmd == "totp":
            print(api.get_device_auth_code())
        elif args.cmd == "capture":
            print(f"image saved to {api.capture_image(args.output, args.corrected)}")
        elif args.cmd == "gantry":
            print(json.dumps(api.gantry_move(args.x, args.y, args.z), indent=2))
        elif args.cmd == "gpio":
            print(json.dumps(api.gpio(args.action, pin=args.pin,
                                      blink_duration_ms=args.duration_ms,
                                      command=args.command), indent=2))
    except ApiError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
