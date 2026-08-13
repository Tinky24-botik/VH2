import threading
import queue
import time
import tkinter as tk

_queue = queue.Queue()
_started = False

COLORS = {
    "success": "#2ecc71",
    "error": "#e74c3c",
    "info": "#3498db",
}


def _run():
    root = tk.Tk()
    root.withdraw()

    def show_popup(text, kind):
        popup = tk.Toplevel(root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.attributes("-alpha", 0.7)

        color = COLORS.get(kind, COLORS["info"])
        popup.configure(bg=color)

        label = tk.Label(
            popup,
            text=text,
            bg=color,
            fg="white",
            font=("Segoe UI", 11),
            padx=16,
            pady=10,
            wraplength=300,
            justify="left",
        )
        label.pack()

        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        margin = 20
        x = margin
        y = margin

        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.after(2700, popup.destroy)

    def check_queue():
        try:
            while True:
                text, kind = _queue.get_nowait()
                show_popup(text, kind)
        except queue.Empty:
            pass
        root.after(100, check_queue)

    root.after(100, check_queue)
    root.mainloop()


def start():
    global _started
    if _started:
        return
    _started = True
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    time.sleep(0.3)


def notify(text: str, kind: str = "info"):
    _queue.put((text, kind))