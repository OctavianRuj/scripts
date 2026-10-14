"""whip_idle.py - plays a whip crack when there has been no mouse/keyboard input for 3 minutes.

Run:  python whip_idle.py        (Ctrl+C to stop)
You write the TODOs. A finished version is in whip_idle_solution.py - peek only when stuck.
"""
import ctypes
import time

IDLE_LIMIT_SECS = 180   # 3 minutes without input -> whip
REPEAT_SECS = 30        # while still idle, whip again this often
POLL_SECS = 2
WHIP_WAV = r"C:\Users\MKLab\Downloads\freesound_community-mixed-whip-crack-1-102825.mp3"


# ---------- DONE: the ctypes struct Windows fills in for us ----------
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


# ---------- TODO 1: how long since the last mouse/keyboard input? ----------
# Return seconds as a float. Steps:
#   1. info = LASTINPUTINFO(); info.cbSize = ctypes.sizeof(LASTINPUTINFO)
#   2. ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info))   # fills info.dwTime
#   3. now = ctypes.windll.kernel32.GetTickCount()                 # same clock, in ms
#   4. idle ms = now - info.dwTime  (both are 32-bit and wrap around, so mask with & 0xFFFFFFFF)
#   5. return ms / 1000
# Test alone: python -c "import whip_idle as w; print(w.idle_seconds())"
#   then don't touch anything for 10 s and run it again - it should be ~10.
def idle_seconds() -> float:
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info))
    now = ctypes.windll.kernel32.GetTickCount()
    idle_ms = (now - info.dwTime) & 0xFFFFFFFF  # tick counter wraps at 32 bits
    return idle_ms / 1000


# ---------- TODO 2: play the sound ----------
# winsound.PlaySound(WHIP_WAV, winsound.SND_FILENAME) plays a .wav and blocks until done.
# Need a whip sound? Download any whip .wav, or ask me for the synthesizer in the solution file.
# Bonus: fall back to winsound.Beep(1000, 300) if the file is missing.
def play_whip() -> None:
    # winsound only plays .wav, so use Windows' MCI (winmm) which handles .mp3; "wait" blocks until done
    ctypes.windll.winmm.mciSendStringW(f'play "{WHIP_WAV}" wait', None, 0, None)


# ---------- TODO 3: main loop ----------
# Every POLL_SECS: if idle_seconds() >= IDLE_LIMIT_SECS AND at least REPEAT_SECS have passed
# since the last whip, print a line and play the whip.
# Hints:
#   - keep last_whip = 0.0 and compare with time.monotonic()
#   - wrap the while loop in try/except KeyboardInterrupt so Ctrl+C exits cleanly
#   - playing sound is NOT input, so it won't reset the idle timer - that's why REPEAT_SECS exists
# Tip: set IDLE_LIMIT_SECS = 10 while testing, then put it back to 180.
def main() -> None:
    print(f"Whip after {IDLE_LIMIT_SECS}s idle (repeats every {REPEAT_SECS}s). Ctrl+C to stop.")
    last_whip = 0.0
    try:
        while True:
            if idle_seconds() >= IDLE_LIMIT_SECS and time.monotonic() - last_whip >= REPEAT_SECS:
                print(f"{time.strftime('%H:%M:%S')}  idle {idle_seconds():.0f}s -> WHIP")
                play_whip()
                last_whip = time.monotonic()
            time.sleep(POLL_SECS)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
