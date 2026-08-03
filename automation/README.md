# RE5 Automation examples

Scripts for RE5's **Iteration Automation** — marking a different value on every
part without editing the job between runs. These are meant to be copied and
edited, not installed.

Unlike the rest of this repo (which drives jobs *headlessly* over HTTP), these
work *with* the RE5 UI: RE5 pulls values from a server you run, and the
operator triggers each part with a foot switch or a barcode scan.

| File | What it is |
|---|---|
| `iteration_feed_server.py` | A complete value-feed server (Flask). Serves serials, dates, text and images to RE5, and commits only when a job actually completes. |

## The idea

RE5's Iteration Automation panel holds a sheet: each **row** is bound to an
object in the job (text, a barcode/QR, or an image), and each **column** is one
run. Values can be typed, pasted from Excel, generated with tokens like
`{SERIAL}` and `{DATE:MM/DD/YY HH:MM}`, scanned from a barcode gun with
`{SCAN}` — or **fetched from your own server**, which is what these scripts do.

## Running the feed server

```bash
pip install flask
python3 iteration_feed_server.py          # listens on 0.0.0.0:8420
```

Then in RE5: open **Iteration Automation**, right-click (or hold) the **Fetch**
button, and enter:

```
http://<this-machine>:8420/data,http://<this-machine>:8420/confirm
```

Click **Fetch** to pull values into the active column, **Replace** to write them
onto the objects, then **Play**.

## The contract, in one paragraph

`GET /data` returns the values for the next part. `POST /confirm` is called by
RE5 **only when a job completes**, echoing the token your `/data` returned.

That split is the whole point. A fetch is a **read** — at that moment nothing
has been marked, and the operator may never press Play. If you increment your
serial in `/data`, a preview or an aborted run burns a number for a part that
does not exist. Increment in `/confirm` instead and it cannot happen.

### Response shapes

Both JSON and CSV work; content-type decides.

```jsonc
{"values": {"Serial": "SN00042", "Batch": "260803"}}   // keyed by Object name
{"values": ["SN00042", "SN00043"]}                     // positional, top row first
```

Keyed is safer — positional silently shifts if someone reorders the rows.

Optional: `token` (echoed on confirm) and `message` (shown to the operator as a
toast — use it for "batch 7 of 12" or "low stock").

### Images

An image row's value can be:

- a **`data:` URI** — self-contained, always works, no second request;
- an **`http(s)` URL** — fetched by the browser, so your host must send CORS
  headers;
- a **filename** already in the operator's Local Resources.

Prefer the data URI for images the operator has never seen.

### Notes

- RE5 fetches this **server-side**, so your endpoint only has to be reachable
  from the machine running the RE5 server — not from the operator's browser.
  Plain `http://` on your LAN is fine.
- A timeout **fails stop**: nothing on the canvas changes. Stale values are
  never reused.
- An optional auth header can be sent with both calls.

Full contract: `docs/API_REFERENCE.md` §6b in the habanero repo, and the
**Automation & Serialising** topic in RE5's own Help.
