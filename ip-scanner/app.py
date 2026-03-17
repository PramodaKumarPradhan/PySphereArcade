from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import socket
import json

app = Flask(__name__)
CORS(app)

IP_API_BASE = "http://ip-api.com/json"
IPIFY_URL   = "https://api.ipify.org?format=json"

# ── helpers ────────────────────────────────────────────────────────────────────

def fetch_ip_info(ip: str) -> dict:
    """Fetch detailed info for a single IP from ip-api.com (free, no key)."""
    try:
        fields = (
            "status,message,continent,continentCode,country,countryCode,"
            "region,regionName,city,district,zip,lat,lon,timezone,offset,"
            "isp,org,as,asname,reverse,mobile,proxy,hosting,query"
        )
        resp = requests.get(f"{IP_API_BASE}/{ip}", params={"fields": fields}, timeout=8)
        data = resp.json()

        if data.get("status") == "fail":
            return {"error": data.get("message", "Lookup failed"), "ip": ip}

        # Attempt reverse hostname
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception:
            hostname = data.get("reverse", "—")

        return {
            "ip":           data.get("query", ip),
            "hostname":     hostname,
            "city":         data.get("city", "—"),
            "district":     data.get("district", ""),
            "region":       data.get("regionName", "—"),
            "region_code":  data.get("region", ""),
            "zip":          data.get("zip", "—"),
            "country":      data.get("country", "—"),
            "country_code": data.get("countryCode", ""),
            "continent":    data.get("continent", "—"),
            "lat":          data.get("lat", 0),
            "lon":          data.get("lon", 0),
            "timezone":     data.get("timezone", "—"),
            "utc_offset":   data.get("offset", 0),
            "isp":          data.get("isp", "—"),
            "org":          data.get("org", "—"),
            "asn":          data.get("as", "—"),
            "asn_name":     data.get("asname", "—"),
            "is_mobile":    data.get("mobile", False),
            "is_proxy":     data.get("proxy", False),
            "is_hosting":   data.get("hosting", False),
        }
    except requests.exceptions.ConnectionError:
        return {"error": "Network error: could not reach lookup service.", "ip": ip}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out.", "ip": ip}
    except Exception as e:
        return {"error": str(e), "ip": ip}


def get_caller_ip() -> str:
    """Best-effort to get the real client IP behind proxies."""
    for header in ("X-Forwarded-For", "X-Real-IP", "CF-Connecting-IP"):
        val = request.headers.get(header)
        if val:
            return val.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


# ── routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/lookup")
def api_lookup():
    ip = request.args.get("ip", "").strip()
    if not ip:
        return jsonify({"error": "No IP provided."}), 400
    result = fetch_ip_info(ip)
    return jsonify(result)


@app.route("/api/myip")
def api_myip():
    """Detect caller's own public IP, then look it up."""
    try:
        # Try ipify for accurate public IP (works even behind NAT)
        ext = requests.get(IPIFY_URL, timeout=5).json()
        public_ip = ext.get("ip", get_caller_ip())
    except Exception:
        public_ip = get_caller_ip()

    result = fetch_ip_info(public_ip)
    return jsonify(result)


@app.route("/api/bulk", methods=["POST"])
def api_bulk():
    """Accept JSON body: { "ips": ["1.1.1.1", "8.8.8.8", ...] }"""
    body = request.get_json(silent=True) or {}
    ips  = body.get("ips", [])
    if not ips:
        return jsonify({"error": "No IPs provided."}), 400
    if len(ips) > 20:
        return jsonify({"error": "Maximum 20 IPs per bulk request."}), 400

    results = []
    for ip in ips:
        ip = str(ip).strip()
        if ip:
            results.append(fetch_ip_info(ip))
    return jsonify({"results": results})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
