import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from datetime import datetime

# ── สีหลัก ──────────────────────────────────────────────────
BG_ROOT   = "#0d0d1a"
BG_CARD   = "#1e272e"
BG_HEADER = "#16213e"
BG_STATUS = "#0f3460"
BG_GRID   = "#0d0d1a"

# ── Font: ใช้ Courier New เป็น pixel-style arcade font ──────
FONT_TITLE   = ("Courier New", 18, "bold")
FONT_SUB     = ("Courier New", 10)
FONT_STATUS  = ("Courier New",  9, "bold")
FONT_SECTION = ("Courier New", 13, "bold")
FONT_BTN     = ("Courier New", 11, "bold")
FONT_DESC    = ("Courier New",  9)
FONT_LAUNCH  = ("Courier New", 10, "bold")
FONT_CARD_LB = ("Courier New",  9, "bold")
FONT_CARD_VL = ("Courier New",  8)
FONT_FOOTER  = ("Courier New",  8)
FONT_ICON    = ("Segoe UI Emoji", 22, "bold")
FONT_ICON_SM = ("Segoe UI Emoji", 15)


class HoneypotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.animation_running = True
        self.blink_state = True

        # เก็บสถานะ hover ของแต่ละ card ด้วย key (widget id)
        # เพื่อไม่ต้อง loop children ซ้ำทุกครั้ง
        self._card_widgets: dict[int, dict] = {}

        self.setup_window()
        self.create_widgets()
        self.animate_glow()
        self.update_time()

    # ──────────────────────────────────────────
    # Window Setup
    # ──────────────────────────────────────────
    def setup_window(self):
        self.root.title("🍯 ระบบป้องกันไซเบอร์")
        self.root.geometry("980x720")
        self.root.configure(bg=BG_ROOT)
        self.root.resizable(True, True)
        self.root.minsize(860, 620)
        self.root.attributes("-alpha", 0.98)
        self.center_window()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ──────────────────────────────────────────
    # Main Layout
    # ──────────────────────────────────────────
    def create_widgets(self):
        outer = tk.Frame(self.root, bg=BG_ROOT)
        outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(outer, bg=BG_ROOT, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical",
                                  command=self._canvas.yview)

        self.scrollable_frame = tk.Frame(self._canvas, bg=BG_ROOT)
        self._win_id = self._canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        self._canvas.configure(yscrollcommand=scrollbar.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ── resize scrollable_frame ให้เต็มความกว้าง canvas เสมอ ──
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            )
        )

        # ── scroll ด้วย mouse wheel (Windows + Linux) ──
        self._canvas.bind_all("<MouseWheel>",   self._on_mousewheel)
        self._canvas.bind_all("<Button-4>",     self._on_mousewheel)
        self._canvas.bind_all("<Button-5>",     self._on_mousewheel)

        content = tk.Frame(self.scrollable_frame, bg=BG_ROOT)
        content.pack(fill="both", expand=True, padx=24, pady=18)

        self.create_header(content)
        self.create_status_panel(content)
        self.create_button_grid(content)
        self.create_footer(content)

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._win_id, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ──────────────────────────────────────────
    # Header
    # ──────────────────────────────────────────
    def create_header(self, parent):
        outer = tk.Frame(parent, bg="#ff6b35", relief="ridge", bd=3)
        outer.pack(fill="x", pady=(0, 20))

        inner = tk.Frame(outer, bg=BG_HEADER, relief="ridge", bd=2)
        inner.pack(fill="both", expand=True, padx=2, pady=2)

        # pixel accent line
        tk.Frame(inner, bg="#ff6b35", height=3).pack(fill="x")

        body = tk.Frame(inner, bg=BG_HEADER)
        body.pack(fill="x", padx=20, pady=14)

        # icon + title row
        title_row = tk.Frame(body, bg=BG_HEADER)
        title_row.pack()

        self.main_icon = tk.Label(
            title_row, text="🍯⚔️🛡️",
            font=FONT_ICON,
            bg=BG_HEADER, fg="#ff6b35"
        )
        self.main_icon.pack(side="left", padx=(0, 14))

        tk.Label(
            title_row, text="ระบบป้องกันไซเบอร์",
            font=("Leelawadee UI", 22, "bold"),
            bg=BG_HEADER, fg="#4ecdc4"
        ).pack(side="left")

        tk.Label(
            body, text="[ CYBER DEFENSE & HONEYPOT CONTROL CENTER ]",
            font=FONT_SUB,
            bg=BG_HEADER, fg="#ffa726"
        ).pack(pady=(8, 0))

        self.status_info = tk.Label(
            body,
            text=self._status_text(),
            font=FONT_STATUS,
            bg=BG_HEADER, fg="#45b7d1"
        )
        self.status_info.pack(pady=(6, 0))

    def _status_text(self):
        return (f">> TIME: {datetime.now().strftime('%H:%M:%S')}   "
                f"USER: EXPERT   STATUS: [ONLINE]")

    # ──────────────────────────────────────────
    # Status Panel
    # ──────────────────────────────────────────
    def create_status_panel(self, parent):
        outer = tk.Frame(parent, bg=BG_STATUS, relief="ridge", bd=2)
        outer.pack(fill="x", pady=(0, 20), padx=4)

        tk.Label(
            outer, text="[ สถานะระบบปัจจุบัน / SYSTEM STATUS ]",
            font=FONT_SECTION,
            bg=BG_STATUS, fg="#ffeaa7"
        ).pack(pady=(10, 10))

        grid = tk.Frame(outer, bg=BG_STATUS)
        grid.pack(fill="x", padx=16, pady=(0, 14))

        status_items = [
            ("🟢", "CONNECTION",  "CONNECTED",       "#00b894"),
            ("🟡", "SCANNING",    "RUNNING",          "#fdcb6e"),
            ("🔴", "DEFENSE",     "ENABLED",          "#e84393"),
            ("🔵", "UPTIME",      datetime.now().strftime('%H:%M'), "#74b9ff"),
        ]

        for col_idx in range(4):
            grid.columnconfigure(col_idx, weight=1)

        for i, (icon, name, val, color) in enumerate(status_items):
            card = tk.Frame(grid, bg=BG_CARD, relief="raised", bd=2)
            card.grid(row=0, column=i, padx=6, pady=4,
                      sticky="nsew", ipadx=4, ipady=4)

            tk.Label(card, text=icon, font=FONT_ICON_SM,
                     bg=BG_CARD, fg=color).pack(pady=(6, 0))
            tk.Label(card, text=name, font=FONT_CARD_LB,
                     bg=BG_CARD, fg="#dfe6e9").pack()
            tk.Label(card, text=val, font=FONT_CARD_VL,
                     bg=BG_CARD, fg=color).pack(pady=(0, 6))

    # ──────────────────────────────────────────
    # Button Grid
    # ──────────────────────────────────────────
    def create_button_grid(self, parent):
        header = tk.Frame(parent, bg="#6c5ce7", relief="ridge", bd=2)
        header.pack(fill="x", padx=4, pady=(0, 16))

        tk.Label(
            header, text="[ SELECT TOOL / เลือกเครื่องมือ ]",
            font=FONT_SECTION,
            bg="#6c5ce7", fg="#ffffff"
        ).pack(pady=8)

        buttons = [
            {
                "text":    "DASHBOARD SUMMARY",
                "desc":    "เปิดหน้าจอสรุปผลการวิเคราะห์ข้อมูลทั้งหมด",
                "command": self.run_streamlit_summary,
                "color":   "#00b894",
                "icon":    "📊",
            },
            {
                "text":    "ALERT CHECKER",
                "desc":    "วิเคราะห์และแจ้งเตือนความปลอดภัยแบบ real-time",
                "command": self.run_alert_checker,
                "color":   "#e84393",
                "icon":    "🔥",
            },
            {
                "text":    "RECEIVER",
                "desc":    "เปิดตัวรับข้อมูลจาก honeypot และ sensors",
                "command": self.run_receiver,
                "color":   "#0984e3",
                "icon":    "📡",
            },
            {
                "text":    "FILTER IP LOG",
                "desc":    "วิเคราะห์และกรองข้อมูล IP จาก log ทั้งหมด",
                "command": self.filter_ip_log,
                "color":   "#fdcb6e",
                "icon":    "🔍",
            },
            {
                "text":    "MAIN DASHBOARD",
                "desc":    "เปิดแดชบอร์ดหลักของระบบ honeypot",
                "command": self.run_streamlit_dashboard,
                "color":   "#a29bfe",
                "icon":    "🖥️",
            },
            {
                "text":    "EXIT SYSTEM",
                "desc":    "ปิดโปรแกรมและหยุดการทำงานทั้งหมด",
                "command": self.quit_app,
                "color":   "#636e72",
                "icon":    "❌",
            },
        ]

        grid_frame = tk.Frame(parent, bg=BG_GRID)
        grid_frame.pack(fill="both", expand=True, padx=4)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        for idx, cfg in enumerate(buttons):
            row = idx // 2
            col = idx % 2
            self._make_button_card(grid_frame, cfg, row, col)

    def _make_button_card(self, grid, cfg, row, col):
        cell = tk.Frame(grid, bg=BG_GRID)
        cell.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        grid.rowconfigure(row, weight=1)

        # ── card frame ── highlightthickness=2 เผื่อไว้สำหรับ glow hover
        card = tk.Frame(cell, bg=BG_CARD, relief="raised", bd=2, cursor="hand2",
                        highlightthickness=2, highlightbackground=BG_GRID)
        card.pack(fill="both", expand=True)

        # left accent bar (สีคงที่ ไม่เปลี่ยนตอน hover)
        accent = tk.Frame(card, bg=cfg["color"], width=8)
        accent.pack(side="left", fill="y")
        accent.pack_propagate(False)

        # content area
        body = tk.Frame(card, bg=BG_CARD)
        body.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        top = tk.Frame(body, bg=BG_CARD)
        top.pack(fill="x")

        icon_lbl = tk.Label(
            top, text=cfg["icon"],
            font=FONT_ICON_SM,
            bg=BG_CARD, fg=cfg["color"], cursor="hand2"
        )
        icon_lbl.pack(side="left", padx=(0, 10))

        title_lbl = tk.Label(
            top, text=cfg["text"],
            font=FONT_BTN,
            bg=BG_CARD, fg="#ffffff", cursor="hand2",
            anchor="w"
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        desc_lbl = tk.Label(
            body, text=cfg["desc"],
            font=FONT_DESC,
            bg=BG_CARD, fg="#b2bec3", cursor="hand2",
            wraplength=340, justify="left", anchor="w"
        )
        desc_lbl.pack(fill="x", pady=(5, 0))

        # launch button (right)
        launch = tk.Label(
            card, text="▶ RUN",
            font=FONT_LAUNCH,
            bg=cfg["color"], fg="#000000",
            cursor="hand2", relief="raised", bd=2,
            padx=12, pady=5
        )
        launch.pack(side="right", padx=12, pady=12)

        # ── รวบ widgets ทั้งหมดของ card นี้ เพื่อ hover แบบ O(1) ──
        # แยก accent ออกไม่ต้องเปลี่ยนสี
        bg_widgets   = [card, body, top, icon_lbl, title_lbl, desc_lbl]
        card_id      = id(card)
        self._card_widgets[card_id] = {
            "bg_widgets": bg_widgets,
            "color":      cfg["color"],
            "launch":     launch,
            "card":       card,
            "icon_lbl":   icon_lbl,
        }

        clickable = [card, body, top, icon_lbl, title_lbl, desc_lbl, launch, accent]
        for w in clickable:
            w.bind("<Button-1>", lambda e, cmd=cfg["command"]: cmd())
            w.bind("<Enter>",    lambda e, cid=card_id: self._hover_on(cid))
            w.bind("<Leave>",    lambda e, cid=card_id: self._hover_off(cid))

    # ──────────────────────────────────────────
    # Hover  (ไม่กระตุก: อัปเดตเฉพาะ widget ที่เก็บไว้)
    # ──────────────────────────────────────────
    def _hover_on(self, card_id: int):
        info = self._card_widgets.get(card_id)
        if not info:
            return
        color = info["color"]
        # ใช้ highlightbackground เป็น glow — ไม่เปลี่ยน bd เลยไม่ขยับ
        info["card"].configure(highlightbackground=color)
        for w in info["bg_widgets"]:
            try:
                w.configure(bg=color)
            except Exception:
                pass
        try:
            info["icon_lbl"].configure(fg="#000000")
        except Exception:
            pass

    def _hover_off(self, card_id: int):
        info = self._card_widgets.get(card_id)
        if not info:
            return
        color = info["color"]
        info["card"].configure(highlightbackground=BG_GRID)
        for w in info["bg_widgets"]:
            try:
                w.configure(bg=BG_CARD)
            except Exception:
                pass
        try:
            info["icon_lbl"].configure(fg=color)
        except Exception:
            pass

    # ──────────────────────────────────────────
    # Footer
    # ──────────────────────────────────────────
    def create_footer(self, parent):
        footer = tk.Frame(parent, bg=BG_HEADER, relief="ridge", bd=1)
        footer.pack(fill="x", pady=(20, 4))

        tk.Frame(footer, bg="#ff6b35", height=2).pack(fill="x")

        tk.Label(
            footer,
            text="[ HONEYPOT CYBER DEFENSE ]  Pling site/49  "
                 "|  นายพุฒิเมธ บุตรเงิน  |  นายพชร เสืออ่ำ  |  นายเฉลิมพร บุญชู",
            font=FONT_FOOTER,
            bg=BG_HEADER, fg="#636e72"
        ).pack(pady=6)

    # ──────────────────────────────────────────
    # Animations  (ลด rate ป้องกัน UI กระตุก)
    # ──────────────────────────────────────────
    def animate_glow(self):
        if not self.animation_running:
            return
        self.blink_state = not self.blink_state
        try:
            self.main_icon.configure(
                fg="#ff6b35" if self.blink_state else "#ffa726"
            )
        except Exception:
            pass
        # 1200 ms — ช้าลงเพื่อไม่ให้ดูกระตุก
        self.root.after(1200, self.animate_glow)

    def update_time(self):
        if not self.animation_running:
            return
        try:
            self.status_info.configure(text=self._status_text())
        except Exception:
            pass
        # 5000 ms — อัปเดตทุก 5 วิ ลด overhead
        self.root.after(5000, self.update_time)

    # ──────────────────────────────────────────
    # Tool launchers
    # ──────────────────────────────────────────
    def run_streamlit_dashboard(self):
        self._launch_cmd("streamlit run dashboard.py",
                         "LOADING: Dashboard Main")

    def run_streamlit_summary(self):
        self._launch_cmd("streamlit run dashboard_summary.py",
                         "LOADING: Dashboard Summary")

    def run_receiver(self):
        self._launch_cmd("python receiver.py",
                         "LOADING: Receiver")

    def run_alert_checker(self):
        self._launch_cmd("python alert_checker.py",
                         "LOADING: Alert Checker")

    def filter_ip_log(self):
        self._launch_cmd("python filter_ip_log.py",
                         "LOADING: IP Log Filter")

    def quit_app(self):
        if messagebox.askyesno("EXIT", "ต้องการออกจากระบบหรือไม่?"):
            self.animation_running = False
            self.root.destroy()

    def _launch_cmd(self, script_cmd: str, echo_msg: str):
        full_cmd = f'echo {echo_msg} && {script_cmd}'
        subprocess.Popen(
            ["start", "cmd", "/k", full_cmd],
            shell=True
        )

    # ──────────────────────────────────────────
    # Run
    # ──────────────────────────────────────────
    def run(self):
        print("=" * 50)
        print("  HONEYPOT CYBER DEFENSE SYSTEM  ")
        print("=" * 50)
        try:
            self.root.mainloop()
        finally:
            self.animation_running = False


if __name__ == "__main__":
    print(">> BOOTING CYBER DEFENSE SYSTEM...")
    app = HoneypotGUI()
    app.run()
