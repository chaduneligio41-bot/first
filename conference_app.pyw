#!/usr/bin/env python3
"""
Conference Room — საერთო დესკტოპ ჩატი (User + Claude + Antigravity).

მარტივი Tkinter ფანჯარა, რომელიც:
  • აჩვენებს `Conference Room.md` thread-ს ფერადად (ვინ წერს);
  • შენ წერ ქვემოთ და [Send] → შენი შეტყობინება ემატება thread-ს;
  • ავტომატურად ეკითხება Claude-ს (`claude -p`) და მის პასუხს ჩასვამს thread-ში;
  • ფონურად აკვირდება ფაილს — როცა Antigravity (ან Claude) წერს, თვითონ ნახლდება;
  • [Antigravity-ს ცნობა] ღილაკი ბუფერში აკოპირებს ნუდჯ-ტექსტს.

ჩაშენებული წესი: append-only — სხვისი შეტყობინება არასოდეს იცვლება.
გასაშვებად: ორმაგი დაწკაპუნება, ან `python conference_app.pyw`.
"""

import os
import re
import shutil
import subprocess
import threading
from datetime import datetime

import tkinter as tk
from tkinter import scrolledtext, messagebox

# --- გზები ---
VAULT = os.path.dirname(os.path.abspath(__file__))
THREAD_FILE = os.path.join(VAULT, "Conference Room.md")

USER_TAG = "🧑 User"
CLAUDE_TAG = "🟣 Claude"
ANTIGRAVITY_NUDGE = "გადახედე Conference Room-ს და უპასუხე."

MSG_RE = re.compile(r"^### \[(.*?)\] — (.+?)\s*$", re.MULTILINE)


# ---------- Claude CLI ----------
def find_claude():
    """პოულობს claude CLI-ს (npm global shim)."""
    for name in ("claude.cmd", "claude.exe", "claude"):
        p = shutil.which(name)
        if p:
            return p
    fallback = os.path.expandvars(r"%APPDATA%\npm\claude.cmd")
    return fallback if os.path.exists(fallback) else None


def ask_claude(prompt):
    """უშვებს `claude -p` headless რეჟიმში და აბრუნებს ტექსტურ პასუხს."""
    claude = find_claude()
    if not claude:
        return "[შეცდომა] claude CLI ვერ მოიძებნა PATH-ზე."
    # Windows-ზე .cmd shim საჭიროებს cmd /c-ს საიმედო გაშვებისთვის.
    cmd = (["cmd", "/c", claude, "-p", prompt]
           if os.name == "nt" else [claude, "-p", prompt])
    try:
        proc = subprocess.run(
            cmd, cwd=VAULT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=240,
        )
    except subprocess.TimeoutExpired:
        return "[შეცდომა] Claude-მა დიდხანს ვერ უპასუხა (timeout)."
    out = (proc.stdout or "").strip()
    if not out:
        err = (proc.stderr or "").strip()
        return f"[შეცდომა] ცარიელი პასუხი. {err[:300]}"
    return out


# ---------- ფაილის I/O ----------
def read_messages():
    """აბრუნებს [(timestamp, speaker, body), ...] thread-ფაილიდან."""
    if not os.path.exists(THREAD_FILE):
        return []
    with open(THREAD_FILE, encoding="utf-8") as f:
        text = f.read()
    # ვიწყებთ "## 🧵 Thread"-ის შემდეგ, რომ პროტოკოლი არ აირიოს
    idx = text.find("## 🧵 Thread")
    if idx != -1:
        text = text[idx + len("## 🧵 Thread"):]
    out = []
    matches = list(MSG_RE.finditer(text))
    for i, m in enumerate(matches):
        ts, speaker = m.group(1), m.group(2)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((ts, speaker.strip(), text[start:end].strip()))
    return out


def append_message(speaker, body):
    """append-only: ბოლოში ამატებს ერთ შეტყობინებას."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    block = f"\n### [{ts}] — {speaker}\n{body.strip()}\n"
    with open(THREAD_FILE, "a", encoding="utf-8") as f:
        f.write(block)


def build_prompt(messages):
    """ბოლო შეტყობინებებიდან ქმნის prompt-ს Claude-სთვის."""
    recent = messages[-15:]
    convo = "\n".join(f"{sp}: {body}" for _, sp, body in recent)
    return (
        "You are 🟣 Claude, a participant in a shared \"Conference Room\" chat "
        "with the User (🧑) and Antigravity (🔵, a Google AI collaborator). "
        "Reply briefly and helpfully as Claude. Match the user's language "
        "(reply in Georgian if they write Georgian). This is a conversation — "
        "do NOT use tools or take file/git actions unless explicitly asked. "
        "Output ONLY your reply text, with no name prefix and no header.\n\n"
        "Recent thread:\n" + convo
    )


# ---------- GUI ----------
class ConferenceApp:
    COLORS = {
        "user": "#1565c0",
        "claude": "#7b1fa2",
        "antigravity": "#0277bd",
        "sys": "#888888",
    }

    def __init__(self, root):
        self.root = root
        root.title("🏛️ Conference Room — User · Claude · Antigravity")
        root.geometry("760x620")
        root.minsize(520, 400)

        # ჩატის ხედი
        self.view = scrolledtext.ScrolledText(
            root, wrap="word", state="disabled",
            font=("Segoe UI", 11), padx=10, pady=8, bg="#fafafa",
        )
        self.view.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.view.tag_config("user", foreground=self.COLORS["user"], font=("Segoe UI", 11, "bold"))
        self.view.tag_config("claude", foreground=self.COLORS["claude"], font=("Segoe UI", 11, "bold"))
        self.view.tag_config("antigravity", foreground=self.COLORS["antigravity"], font=("Segoe UI", 11, "bold"))
        self.view.tag_config("sys", foreground=self.COLORS["sys"], font=("Segoe UI", 9, "italic"))
        self.view.tag_config("body", foreground="#222222", font=("Segoe UI", 11), lmargin1=16, lmargin2=16)

        # სტატუსი
        self.status = tk.Label(root, text="მზადაა.", anchor="w", fg="#666", font=("Segoe UI", 9))
        self.status.pack(fill="x", padx=10)

        # შეტანის ზონა
        bottom = tk.Frame(root)
        bottom.pack(fill="x", padx=8, pady=8)
        self.entry = tk.Text(bottom, height=3, font=("Segoe UI", 11), wrap="word")
        self.entry.pack(side="left", fill="both", expand=True)
        self.entry.bind("<Control-Return>", lambda e: self.on_send())
        self.entry.focus_set()

        btns = tk.Frame(bottom)
        btns.pack(side="right", fill="y", padx=(6, 0))
        self.send_btn = tk.Button(btns, text="Send  ▶\n(Ctrl+Enter)", width=14, command=self.on_send)
        self.send_btn.pack(fill="x")
        tk.Button(btns, text="🔵 Antigravity-ს ცნობა", command=self.notify_antigravity).pack(fill="x", pady=(4, 0))

        self._last_mtime = 0
        self.render()
        self.poll()

    # --- რენდერი ---
    def render(self):
        msgs = read_messages()
        self.view.config(state="normal")
        self.view.delete("1.0", "end")
        if not msgs:
            self.view.insert("end", "ჯერ შეტყობინებები არ არის. დაიწყე საუბარი ქვემოთ.\n", "sys")
        for ts, speaker, body in msgs:
            low = speaker.lower()
            tag = "claude" if "claude" in low else "antigravity" if "antigravity" in low else "user" if "user" in low else "sys"
            self.view.insert("end", f"{speaker}", tag)
            self.view.insert("end", f"   ·  {ts}\n", "sys")
            self.view.insert("end", f"{body}\n\n", "body")
        self.view.config(state="disabled")
        self.view.see("end")

    # --- ფაილის ცვლილების მონიტორინგი ---
    def poll(self):
        try:
            mtime = os.path.getmtime(THREAD_FILE) if os.path.exists(THREAD_FILE) else 0
            if mtime != self._last_mtime:
                self._last_mtime = mtime
                self.render()
        except OSError:
            pass
        self.root.after(1500, self.poll)

    def set_status(self, text, busy=False):
        self.status.config(text=text)
        self.send_btn.config(state="disabled" if busy else "normal")

    # --- გაგზავნა ---
    def on_send(self):
        text = self.entry.get("1.0", "end").strip()
        if not text:
            return "break"
        self.entry.delete("1.0", "end")
        append_message(USER_TAG, text)
        self.render()
        self.set_status("🟣 Claude წერს…", busy=True)
        threading.Thread(target=self._claude_worker, daemon=True).start()
        return "break"

    def _claude_worker(self):
        reply = ask_claude(build_prompt(read_messages()))
        append_message(CLAUDE_TAG, reply)
        # UI განახლება მთავარ thread-ში
        self.root.after(0, lambda: (self.render(), self.set_status("მზადაა.", busy=False)))

    def notify_antigravity(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(ANTIGRAVITY_NUDGE)
        self.set_status("📋 დაკოპირდა: ჩასვი Antigravity-ის ჩატში — \"" + ANTIGRAVITY_NUDGE + "\"")


def main():
    if not os.path.exists(THREAD_FILE):
        # მინიმალური thread-ფაილი, თუ არ არსებობს
        with open(THREAD_FILE, "w", encoding="utf-8") as f:
            f.write("# 💬 Conference Room — საერთო სათათბირო\n\n## 🧵 Thread\n")
    root = tk.Tk()
    try:
        ConferenceApp(root)
    except Exception as e:  # noqa
        messagebox.showerror("Conference Room", f"გაშვების შეცდომა:\n{e}")
        return
    root.mainloop()


if __name__ == "__main__":
    main()
