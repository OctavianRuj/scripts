"""ah_ping.py - pings albert heijn every 5 minutes and shows a Windows toast with the result.

Run:  python ah_ping.py
Standard library only.
"""
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime

URL = "https://www.ah.nl"
INTERVAL_SECS = 300  # 5 minutes


# ---------- DONE: toast helper (shells out to Windows PowerShell) ----------
def show_toast(title: str, message: str) -> None:
    def esc(s: str) -> str:
        return (s.replace("&", "&amp;").replace("<", "&lt;")
                 .replace(">", "&gt;").replace("'", "''"))

    ps = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml('<toast><visual><binding template="ToastGeneric"><text>{esc(title)}</text><text>{esc(message)}</text></binding></visual></toast>')
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\WindowsPowerShell\\v1.0\\powershell.exe').Show($toast)
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, check=False)


# ---------- ping ----------
def ping_ah(url: str) -> dict:
    """Request `url`; return {"status": int|None, "ms": int, "error": str|None}."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
        error = None
    except urllib.error.HTTPError as e:  # server answered 4xx/5xx
        status = e.code
        error = str(e.reason)
    except (urllib.error.URLError, TimeoutError) as e:  # no answer (DNS, offline, timeout)
        status = None
        error = str(getattr(e, "reason", e))
    ms = round((time.perf_counter() - start) * 1000)
    return {"status": status, "ms": ms, "error": error}


# ---------- notification text ----------
def format_result(result: dict) -> str:
    status, ms, error = result["status"], result["ms"], result["error"]
    if status is None:
        return f"FAILED: {error}"
    if status < 400:
        return f"{status} OK in {ms} ms"
    return f"{status} {error} in {ms} ms"


# ---------- DONE: main loop ----------
def main() -> None:
    print(f"Pinging {URL} every {INTERVAL_SECS} s. Ctrl+C to stop.")
    try:
        while True:
            text = format_result(ping_ah(URL))
            print(f"{datetime.now():%H:%M:%S}  {text}")
            show_toast("Albert Heijn ping", text)
            time.sleep(INTERVAL_SECS)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
