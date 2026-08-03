from pathlib import Path
import re
import subprocess

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
UI = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify/_ui.xml"

subprocess.run([ADB, "-s", S, "shell", "am", "force-stop", "com.samsung.android.dialer"])
subprocess.run([ADB, "-s", S, "shell", "am", "start", "-n", "com.josspatech.handyhorology/.MainActivity"])
import time

time.sleep(3)
print(subprocess.run([ADB, "-s", S, "shell", "wm", "size"], capture_output=True, text=True).stdout)
subprocess.run([ADB, "-s", S, "shell", "uiautomator", "dump", "/sdcard/ui.xml"])
subprocess.run([ADB, "-s", S, "pull", "/sdcard/ui.xml", str(UI)])
xml = UI.read_text(encoding="utf-8", errors="ignore")
for lab in ["Home", "My Museum", "Tools", "Settings"]:
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if lab != text and lab != desc and lab not in desc:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        print(f"{lab}: center={(l+r)//2},{(t+b)//2} bounds=[{l},{t},{r},{b}] text={text!r} desc={desc!r}")
