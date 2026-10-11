"""
Local server: serves the Hackathon folder + POST /api/refresh-trends
which re-runs scrape_china_tech_trends.py (incremental, cached).

    python3 trends_server.py        -> http://localhost:3000/china_megatrends.html
"""
import http.server
import os
import subprocess
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", 3000))
_lock = threading.Lock()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def do_POST(self):
        if self.path != "/api/refresh-trends":
            self.send_error(404)
            return
        with _lock:  # one scrape at a time
            proc = subprocess.run([sys.executable, os.path.join(HERE, "scrape_china_tech_trends.py")],
                                  cwd=HERE, capture_output=True, text=True, timeout=900)
        ok = proc.returncode == 0
        body = (proc.stdout[-2000:] if ok else proc.stderr[-2000:]).encode()
        self.send_response(200 if ok else 500)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    print(f"Serving {HERE} on http://localhost:{PORT}")
    http.server.ThreadingHTTPServer(("", PORT), Handler).serve_forever()
