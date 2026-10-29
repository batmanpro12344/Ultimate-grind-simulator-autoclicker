"""Ultimate Grind Auto Clicker — Universal Roblox Edition.
Community-made Windows input automation; no game injection or API access.
"""
from __future__ import annotations
import json
import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from pynput import keyboard, mouse
except ImportError:
    raise SystemExit('Missing dependency. Install with: pip install -r requirements.txt')

APP_NAME = 'Ultimate Grind Auto Clicker — Universal Roblox Edition'
VERSION = '1.0.0'
HOTKEYS = {keyboard.Key.f6, keyboard.Key.f7, keyboard.Key.f8, keyboard.Key.f9}
MAX_ACTIONS = 25000


def serialize_key(key):
    if isinstance(key, keyboard.KeyCode):
        return {'kind': 'char', 'value': key.char} if key.char else None
    if isinstance(key, keyboard.Key):
        return {'kind': 'special', 'value': key.name}
    return None


def deserialize_key(data):
    if data.get('kind') == 'char':
        return keyboard.KeyCode.from_char(data['value'])
    if data.get('kind') == 'special':
        return getattr(keyboard.Key, data['value'])
    raise ValueError('Invalid key')


class MacroApp:
    def __init__(self, root):
        self.root = root
        root.title(APP_NAME + ' v' + VERSION)
        root.geometry('650x520')
        root.minsize(610, 490)
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()
        self.events = []
        self.event_lock = threading.Lock()
        self.state_lock = threading.Lock()
        self.recording = False
        self.playing = False
        self.clicking = False
        self.stop_event = threading.Event()
        self.record_start = 0.0
        self.recorded_keys = set()
        self.held_keys = set()
        self.held_buttons = set()
        self.hotkeys_down = set()
        self.messages = queue.Queue()
        self.cps = tk.StringVar(value='8')
        self.loop_macro = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value='Ready. Use F6–F9 global shortcuts.')
        self._build_ui()
        self.key_listener = keyboard.Listener(on_press=self._key_press, on_release=self._key_release)
        self.mouse_listener = mouse.Listener(on_click=self._mouse_click, on_scroll=self._mouse_scroll)
        self.key_listener.start()
        self.mouse_listener.start()
        root.after(100, self._poll)
        root.protocol('WM_DELETE_WINDOW', self.close)

    def _build_ui(self):
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        outer = ttk.Frame(self.root, padding=20)
        outer.pack(fill='both', expand=True)
        ttk.Label(outer, text='ULTIMATE GRIND', font=('Segoe UI', 23, 'bold')).pack(anchor='w')
        ttk.Label(outer, text='AUTO CLICKER  •  UNIVERSAL ROBLOX EDITION', font=('Segoe UI', 11)).pack(anchor='w')
        ttk.Label(outer, text='Community-made utility • Not affiliated with Roblox', foreground='#666666').pack(anchor='w', pady=(3, 16))
        settings = ttk.LabelFrame(outer, text='Auto Clicker', padding=12)
        settings.pack(fill='x')
        line = ttk.Frame(settings)
        line.pack(fill='x')
        ttk.Label(line, text='Clicks per second (1–20):').pack(side='left')
        ttk.Entry(line, textvariable=self.cps, width=7).pack(side='left', padx=10)
        ttk.Button(line, text='Toggle Clicker (F6)', command=self.toggle_clicker).pack(side='right')
        recording = ttk.LabelFrame(outer, text='Macro Recorder', padding=12)
        recording.pack(fill='x', pady=14)
        actions = ttk.Frame(recording)
        actions.pack(fill='x')
        ttk.Button(actions, text='Record / Stop (F7)', command=self.toggle_recording).pack(side='left', padx=(0, 7))
        ttk.Button(actions, text='Play (F9)', command=self.play_macro).pack(side='left', padx=(0, 7))
        ttk.Checkbutton(actions, text='Loop playback', variable=self.loop_macro).pack(side='left')
        file_buttons = ttk.Frame(recording)
        file_buttons.pack(fill='x', pady=(12, 0))
        ttk.Button(file_buttons, text='Save Macro…', command=self.save_macro).pack(side='left', padx=(0, 8))
        ttk.Button(file_buttons, text='Load Macro…', command=self.load_macro).pack(side='left')
        ttk.Button(file_buttons, text='STOP ALL (F8)', command=self.stop_all).pack(side='right')
        self.count_label = ttk.Label(recording, text='Recorded events: 0')
        self.count_label.pack(anchor='w', pady=(10, 0))
        ttk.Separator(outer).pack(fill='x', pady=12)
        ttk.Label(outer, textvariable=self.status, wraplength=585).pack(anchor='w')
        ttk.Label(outer, text='Shortcuts: F6 click • F7 record • F8 emergency stop • F9 replay', foreground='#555555').pack(anchor='w', pady=(15, 0))
        ttk.Label(outer, text='Automation depends on game rules and whether a game accepts simulated input.', wraplength=570, foreground='#555555').pack(anchor='w', pady=(8, 0))

    def _post(self, text):
        self.messages.put(('status', text))

    def _poll(self):
        try:
            while True:
                kind, value = self.messages.get_nowait()
                if kind == 'status':
                    self.status.set(value)
                if kind == 'count':
                    self.count_label.configure(text=f'Recorded events: {value}')
        except queue.Empty:
            pass
        self.root.after(100, self._poll)

    def _key_press(self, key):
        if key in HOTKEYS:
            with self.state_lock:
                if key in self.hotkeys_down:
                    return
                self.hotkeys_down.add(key)
            self.root.after(0, {keyboard.Key.f6: self.toggle_clicker,
                                keyboard.Key.f7: self.toggle_recording,
                                keyboard.Key.f8: self.stop_all,
                                keyboard.Key.f9: self.play_macro}[key])
            return
        with self.state_lock:
            should_record = self.recording and not self.playing and key not in self.recorded_keys
            if should_record:
                self.recorded_keys.add(key)
        if should_record:
            self._add_event('key_down', key=serialize_key(key))

    def _key_release(self, key):
        if key in HOTKEYS:
            with self.state_lock:
                self.hotkeys_down.discard(key)
            return
        with self.state_lock:
            should_record = self.recording and not self.playing
            self.recorded_keys.discard(key)
        if should_record:
            self._add_event('key_up', key=serialize_key(key))

    def _mouse_click(self, x, y, button, pressed):
        with self.state_lock:
            should_record = self.recording and not self.playing and not self.clicking
        if should_record:
            self._add_event('mouse_down' if pressed else 'mouse_up', x=x, y=y, button=button.name)

    def _mouse_scroll(self, x, y, dx, dy):
        with self.state_lock:
            should_record = self.recording and not self.playing
        if should_record:
            self._add_event('scroll', x=x, y=y, dx=dx, dy=dy)

    def _add_event(self, kind, **data):
        if data.get('key') is None and kind.startswith('key_'):
            return
        with self.event_lock:
            if len(self.events) >= MAX_ACTIONS:
                self._post('Recording limit reached. Press F7 to stop.')
                return
            self.events.append({'time': round(time.monotonic()-self.record_start, 4), 'kind': kind, **data})
            count = len(self.events)
        self.messages.put(('count', count))

    def stop_all(self):
        with self.state_lock:
            self.clicking = False
            self.playing = False
            self.recording = False
            self.recorded_keys.clear()
        self.stop_event.set()
        self._release_inputs()
        self._post('Stopped all automation.')

    def _release_inputs(self):
        with self.state_lock:
            keys, buttons = list(self.held_keys), list(self.held_buttons)
            self.held_keys.clear()
            self.held_buttons.clear()
        for k in keys:
            try: self.keyboard.release(k)
            except Exception: pass
        for b in buttons:
            try: self.mouse.release(b)
            except Exception: pass

    def toggle_clicker(self):
        with self.state_lock:
            active = self.clicking
        if active:
            self.stop_all()
            return
        try:
            cps = float(self.cps.get())
            if not 1 <= cps <= 20:
                raise ValueError
        except ValueError:
            messagebox.showerror('Invalid CPS', 'Enter a number from 1 to 20.')
            return
        self.stop_all()
        self.stop_event.clear()
        with self.state_lock:
            self.clicking = True
        threading.Thread(target=self._click_worker, args=(cps,), daemon=True).start()
        self._post(f'Clicking at {cps:g} CPS. Press F8 to stop.')

    def _click_worker(self, cps):
        while not self.stop_event.is_set():
            try:
                self.mouse.click(mouse.Button.left)
            except Exception as exc:
                self._post('Click failed: ' + str(exc))
                break
            if self.stop_event.wait(1/cps):
                break
        with self.state_lock:
            self.clicking = False

    def toggle_recording(self):
        with self.state_lock:
            active = self.recording
        if active:
            with self.state_lock:
                self.recording = False
                self.recorded_keys.clear()
            self._post(f'Recording stopped. {len(self.events)} events.')
            return
        self.stop_all()
        with self.event_lock:
            self.events = []
            self.record_start = time.monotonic()
        self.messages.put(('count', 0))
        with self.state_lock:
            self.recording = True
        self._post('Recording mouse buttons, scrolling and keyboard. Press F7 to finish.')

    def play_macro(self):
        with self.event_lock:
            events = [dict(e) for e in self.events]
        if not events:
            self._post('No macro to play. Record with F7 or load a file.')
            return
        self.stop_all()
        self.stop_event.clear()
        with self.state_lock:
            self.playing = True
        looping = self.loop_macro.get()
        threading.Thread(target=self._play_worker, args=(events, looping), daemon=True).start()
        self._post('Playing macro. Press F8 to stop.')

    def _play_worker(self, events, looping):
        try:
            while not self.stop_event.is_set():
                previous = 0.0
                for e in events:
                    if self.stop_event.wait(max(0, e['time']-previous)):
                        return
                    previous = e['time']
                    self._execute(e)
                self._release_inputs()
                if not looping:
                    break
            self._post('Macro playback finished.')
        except Exception as exc:
            self._post('Playback error: ' + str(exc))
        finally:
            self._release_inputs()
            with self.state_lock:
                self.playing = False

    def _execute(self, e):
        kind = e['kind']
        if kind.startswith('key_'):
            k = deserialize_key(e['key'])
            if kind == 'key_down':
                self.keyboard.press(k)
                with self.state_lock: self.held_keys.add(k)
            else:
                self.keyboard.release(k)
                with self.state_lock: self.held_keys.discard(k)
        elif kind in ('mouse_down', 'mouse_up'):
            self.mouse.position = (e['x'], e['y'])
            b = getattr(mouse.Button, e['button'])
            if kind == 'mouse_down':
                self.mouse.press(b)
                with self.state_lock: self.held_buttons.add(b)
            else:
                self.mouse.release(b)
                with self.state_lock: self.held_buttons.discard(b)
        elif kind == 'scroll':
            self.mouse.position = (e['x'], e['y'])
            self.mouse.scroll(e['dx'], e['dy'])

    def save_macro(self):
        with self.event_lock: events = list(self.events)
        if not events:
            messagebox.showinfo('Nothing to save', 'Record a macro first.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.ugmacro.json', filetypes=[('Macro JSON', '*.json')])
        if path:
            Path(path).write_text(json.dumps({'version': 1, 'events': events}, indent=2), encoding='utf-8')
            self._post('Macro saved to ' + path)

    def load_macro(self):
        path = filedialog.askopenfilename(filetypes=[('Macro JSON', '*.json')])
        if not path: return
        try:
            if Path(path).stat().st_size > 5_000_000:
                raise ValueError('File too large')
            payload = json.loads(Path(path).read_text(encoding='utf-8'))
            events = payload['events']
            allowed = {'key_down', 'key_up', 'mouse_down', 'mouse_up', 'scroll'}
            if payload.get('version') != 1 or not isinstance(events, list) or len(events) > MAX_ACTIONS:
                raise ValueError('Unsupported macro format')
            for e in events:
                if not isinstance(e, dict) or e.get('kind') not in allowed or not isinstance(e.get('time'), (int,float)) or not 0 <= e['time'] <= 36000:
                    raise ValueError('Invalid event')
                if e['kind'].startswith('key_'):
                    k = deserialize_key(e['key'])
                    if k in HOTKEYS:
                        raise ValueError('Macros may not contain control hotkeys')
                if e['kind'].startswith('mouse_'):
                    if e['button'] not in ('left', 'right', 'middle'):
                        raise ValueError('Invalid button')
                    int(e['x']); int(e['y'])
                if e['kind'] == 'scroll':
                    int(e['x']); int(e['y']); int(e['dx']); int(e['dy'])
            if any(events[i]['time'] > events[i+1]['time'] for i in range(len(events)-1)):
                raise ValueError('Events are not ordered')
            self.stop_all()
            with self.event_lock: self.events = events
            self.messages.put(('count', len(events)))
            self._post(f'Loaded {len(events)} events.')
        except Exception as exc:
            messagebox.showerror('Invalid macro file', str(exc))

    def close(self):
        self.stop_all()
        self.key_listener.stop()
        self.mouse_listener.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    MacroApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
