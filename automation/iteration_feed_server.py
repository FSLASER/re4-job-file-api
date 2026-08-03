#!/usr/bin/env python3
"""
Iteration Automation value feed — a working example server.

Run it, point RE5's Fetch button at it, and edit it to suit. This is the whole
contract; there is nothing else to implement.

    pip install flask
    python3 iteration_feed_server.py
    # then in RE5: right-click Fetch -> http://<this-machine>:8420/data,http://<this-machine>:8420/confirm

Two endpoints, and the split matters:

  GET  /data      hand out the values for the next part. This is a READ - do
                  NOT consume a serial here, because nothing has been marked
                  yet and the operator may never press Play.
  POST /confirm   RE5 calls this when a job actually COMPLETES, echoing the
                  token /data returned. Commit here. A previewed, estimated or
                  aborted job never reaches this, so numbers are never burned
                  for parts that do not exist.

Images work the same way: return a filename that exists in RE5's Local
Resources, or a data: URI, or an http(s) URL - see /data-with-image below.
"""

import base64
import io
import json
import os
from datetime import date

from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

# ── your state. A file, a database, an ERP call — whatever you already have.
STATE_PATH = os.path.join(os.path.dirname(__file__), "feed_state.json")


def _load():
    try:
        with open(STATE_PATH) as f:
            return json.load(f)
    except Exception:
        return {"next": 1, "committed": 0}


def _save(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f)


# ─────────────────────────────────────────────────────────────────────────────
# 1. The simplest useful feed: one serial, keyed by the Object name in RE5.
#    Keyed beats positional because it survives someone reordering the rows.
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/data")
def data():
    st = _load()
    n = st["next"]                       # peek, do NOT increment
    return jsonify(
        values={
            "Serial": f"SN{n:05d}",
            "Batch": date.today().strftime("%y%m%d"),
        },
        token=str(n),                    # comes back on /confirm
        message=f"Staged SN{n:05d}",     # shown to the operator as a toast
    )


@app.post("/confirm")
def confirm():
    body = request.get_json(silent=True) or {}
    token = body.get("token")
    if token is None:
        return jsonify(error="no token"), 400
    st = _load()
    # Only now did a part physically get marked.
    st["next"] = int(token) + 1
    st["committed"] = int(token)
    _save(st)
    app.logger.info("committed %s (status=%s)", token, body.get("status"))
    return "", 204


# ─────────────────────────────────────────────────────────────────────────────
# 2. Positional form — fills the active column top to bottom. Use when the rows
#    are just "part 1..N" and their names do not matter.
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/data-positional")
def data_positional():
    st = _load()
    n = st["next"]
    return jsonify(values=[f"SN{n + i:05d}" for i in range(4)], token=str(n))


# ─────────────────────────────────────────────────────────────────────────────
# 3. CSV instead of JSON — set the content type and return name,value pairs
#    (or one value per line for the positional form).
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/data-csv")
def data_csv():
    st = _load()
    n = st["next"]
    body = f"Serial,SN{n:05d}\nBatch,{date.today():%y%m%d}\n"
    return app.response_class(body, mimetype="text/csv")


# ─────────────────────────────────────────────────────────────────────────────
# 4. IMAGES. An image row's value is resolved three ways, in this order:
#      a) a filename that already exists in RE5's Local Resources
#      b) a data: URI  (data:image/png;base64,....)  — self-contained
#      c) an http(s) URL RE5's server can reach — fetched and imported
#    (b) and (c) are how you serve images your operators have never seen.
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/data-with-image")
def data_with_image():
    st = _load()
    n = st["next"]

    # (b) inline the bytes. Good for small logos; keeps everything in one call.
    png = _tiny_png()
    data_uri = "data:image/png;base64," + base64.b64encode(png).decode("ascii")

    return jsonify(
        values={
            "Serial": f"SN{n:05d}",
            "Logo": data_uri,                       # inline
            # "Logo": f"http://{request.host}/image/{n}.png",   # or (c), by URL
            # "Logo": "acme.png",                                # or (a), local
        },
        token=str(n),
    )


@app.get("/image/<name>")
def image(name):
    """(c) serve the image itself, so the value above can just be a URL."""
    return send_file(io.BytesIO(_tiny_png()), mimetype="image/png",
                     download_name=name)


def _tiny_png() -> bytes:
    """A 1x1 png so the example runs with no assets. Replace with your own."""
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Operator-facing extras worth having in a real deployment
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/status")
def status():
    st = _load()
    return jsonify(next=st["next"], committed=st["committed"])


@app.post("/reset")
def reset():
    _save({"next": int(request.args.get("to", 1)), "committed": 0})
    return jsonify(ok=True)


if __name__ == "__main__":
    # 0.0.0.0 so the laser (or the RE5 server) can reach it across the LAN.
    # RE5 fetches this SERVER-side, so it does not need to be reachable from
    # the operator's browser — only from the machine running habanero.
    app.run(host="0.0.0.0", port=8420, debug=True)
