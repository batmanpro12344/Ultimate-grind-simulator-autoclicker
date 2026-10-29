# Ultimate Grind Auto Clicker — Universal Roblox Edition

Version **1.0.0** — a community-made Windows desktop auto-clicker and macro recorder.
**Not an official Roblox product. Not affiliated with or endorsed by Roblox Corporation.**

## Features
- F6: toggle left-button auto clicker (1–20 clicks/second)
- F7: record/stop keyboard events, mouse clicks, and wheel scrolls
- F8: emergency stop and release held inputs
- F9: play recorded macro; optional loop
- Save/load JSON macro recordings
- Desktop GUI; no injection or access to Roblox client internals

## Use
Install the Windows release setup EXE, launch the app, then use shortcuts. Some games block simulated inputs or prohibit automation. Do not use where against game rules.

## Build from source on Windows
1. Install **Python 3.12+** (select Add Python to PATH) and **Inno Setup 6**.
2. Download or clone this repository, then run `powershell -ExecutionPolicy Bypass -File .\build_windows.ps1` in this folder.
3. Find the setup EXE in `release/`.

For development: `py -3 -m pip install -r requirements.txt` then `py -3 app.py`.

## Security / distribution notes
- Releases are **unsigned**. Windows SmartScreen might warn about unfamiliar executables; source availability and hashes are useful but do not replace code signing, malware scanning, and real Windows testing.
- Do not claim this is official Roblox software.
- Macro files are untrusted inputs. Only open recordings you trust.
- We cannot verify compatibility inside Roblox from a non-Windows environment.

## Privacy
The tool captures input events *while recording* (including keystrokes), and stores them in the file only when you save a macro. Avoid recording passwords or personal information. No telemetry or network functionality is implemented.
