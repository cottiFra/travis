import tkinter as tk
import customtkinter as ctk
import threading
import math
import time
import queue
from travis_core import TravisCore

ctk.set_appearance_mode("dark")

BG          = "#04080f"
PANEL       = "#080e1c"
PANEL2      = "#0c1628"
ACCENT      = "#00cfff"
ACCENT2     = "#0055ff"
ACCENT3     = "#7b2fff"
TEXT        = "#e8f4ff"
SUBTEXT     = "#3d5a7a"
GREEN       = "#00ff88"
RED         = "#ff2255"
BORDER      = "#0d2040"

class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, storico_log):
        super().__init__(parent)
        self.title("Storico Comandi")
        self.geometry("480x520")
        self.configure(fg_color=PANEL)
        self.resizable(False, False)
        self.lift()
        self.attributes("-topmost", True)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(header, text="◈  STORICO COMANDI",
                     font=("Consolas", 13, "bold"), text_color=ACCENT).pack(side="left")

        ctk.CTkButton(header, text="✕", width=28, height=28, corner_radius=14,
                      font=("Segoe UI", 12, "bold"),
                      fg_color=BORDER, hover_color=RED,
                      text_color=TEXT, command=self.destroy).pack(side="right")

        ctk.CTkFrame(self, fg_color=ACCENT2, height=1).pack(fill="x", padx=20, pady=(5, 10))

        self.text = ctk.CTkTextbox(self, fg_color="#060c17", text_color=TEXT,
                                   font=("Consolas", 11), corner_radius=10,
                                   border_width=1, border_color=BORDER,
                                   wrap="word")
        self.text.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.text._textbox.tag_config("cmd_tag", foreground="#94b8cc")
        self.text._textbox.tag_config("travis_tag", foreground=ACCENT)
        self.text._textbox.tag_config("err_tag", foreground=RED)
        self.text._textbox.tag_config("ts_tag", foreground=SUBTEXT)

        self.text.configure(state="normal")
        if not storico_log:
            self.text.insert("end", "Nessun comando ancora.\n", "ts_tag")
        else:
            for entry in storico_log:
                ts = entry.get("time", "")
                tipo = entry.get("tipo", "cmd")
                testo = entry.get("testo", "")
                if tipo == "cmd":
                    self.text.insert("end", f"{ts}  ", "ts_tag")
                    self.text.insert("end", f"▶  {testo}\n\n", "cmd_tag")
                elif tipo == "travis":
                    self.text.insert("end", f"{ts}  ", "ts_tag")
                    self.text.insert("end", f"◀  {testo}\n\n", "travis_tag")
                elif tipo == "err":
                    self.text.insert("end", f"{ts}  ", "ts_tag")
                    self.text.insert("end", f"⚠  {testo}\n\n", "err_tag")
        self.text.configure(state="disabled")
        self.text.see("end")


class TravisUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TRAVIS")
        self.root.geometry("440x620")
        self.root.configure(fg_color=BG)
        self.root.resizable(False, False)

        self.attivo = False
        self.parlando = False
        self.registrando = False
        self.elaborando = False
        self.onda_angolo = 0.0
        self.amp_target = 0.0
        self.amp_corrente = 0.0

        self.stop_event = threading.Event()
        self.conferma_event = threading.Event()
        self.conferma_valore = False
        self.storico_log = []

        self.core = TravisCore()

        self._build_ui()
        self._avvia_travis()
        self._anima_onda()

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_ui(self):
        header = ctk.CTkFrame(self.root, fg_color="transparent", height=46)
        header.pack(fill="x", padx=24, pady=(16, 0))

        ctk.CTkLabel(header, text="T R A V I S",
                     font=("Courier New", 22, "bold"),
                     text_color=ACCENT).pack(side="left")

        self.stato_lbl = ctk.CTkLabel(header, text="● INIZIALIZZAZIONE",
                                      font=("Consolas", 10, "bold"),
                                      text_color=SUBTEXT)
        self.stato_lbl.pack(side="right", pady=10)

        ctk.CTkFrame(self.root, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=(8, 0))

        canvas_holder = ctk.CTkFrame(self.root, fg_color=PANEL, corner_radius=18,
                                     border_width=1, border_color=BORDER, height=280)
        canvas_holder.pack(fill="x", padx=24, pady=16)
        canvas_holder.pack_propagate(False)

        self.canvas = tk.Canvas(canvas_holder, width=392, height=260,
                                bg=PANEL,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        sub_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=88)
        sub_frame.pack(fill="x", padx=30, pady=(0, 8))
        sub_frame.pack_propagate(False)

        self.user_lbl = ctk.CTkLabel(sub_frame, text="",
                                     font=("Segoe UI", 11, "italic"),
                                     text_color=SUBTEXT, wraplength=370,
                                     anchor="center", justify="center")
        self.user_lbl.pack(fill="x")

        self.travis_lbl = ctk.CTkLabel(sub_frame, text="Sistema in avvio...",
                                       font=("Segoe UI", 14, "bold"),
                                       text_color=TEXT, wraplength=370,
                                       anchor="center", justify="center")
        self.travis_lbl.pack(fill="x", pady=(6, 0))

        self.conferma_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=44)
        self.btn_esegui = ctk.CTkButton(self.conferma_frame, text="✔  ESEGUI",
                                        font=("Segoe UI", 11, "bold"),
                                        fg_color=GREEN, hover_color="#00cc66",
                                        text_color=BG, width=130, height=34,
                                        corner_radius=17, command=self._click_esegui)
        self.btn_esegui.pack(side="left", padx=8)
        self.btn_annulla = ctk.CTkButton(self.conferma_frame, text="✘  ANNULLA",
                                         font=("Segoe UI", 11, "bold"),
                                         fg_color=RED, hover_color="#cc1a44",
                                         text_color=TEXT, width=130, height=34,
                                         corner_radius=17, command=self._click_annulla)
        self.btn_annulla.pack(side="right", padx=8)

        bottom = ctk.CTkFrame(self.root, fg_color=PANEL2, corner_radius=16,
                              border_width=1, border_color=BORDER, height=56)
        bottom.pack(fill="x", side="bottom", padx=24, pady=20)
        bottom.pack_propagate(False)

        self.btn_toggle = ctk.CTkButton(bottom, text="⏸",
                                        font=("Segoe UI", 16),
                                        fg_color="transparent",
                                        hover_color=BORDER,
                                        text_color=SUBTEXT,
                                        width=42, height=42,
                                        corner_radius=12,
                                        command=self._toggle)
        self.btn_toggle.pack(side="left", padx=(8, 0), pady=7)

        self.input_var = ctk.StringVar()
        self.input_box = ctk.CTkEntry(bottom, textvariable=self.input_var,
                                      font=("Segoe UI", 12),
                                      placeholder_text="Digita un comando...",
                                      fg_color="transparent",
                                      text_color=TEXT,
                                      border_width=0,
                                      height=42)
        self.input_box.pack(side="left", fill="x", expand=True, pady=7)
        self.input_box.bind("<Return>", self._invia_testo)

        self.chiedi_conferma = ctk.BooleanVar(value=True)
        self.sw_conf = ctk.CTkSwitch(bottom, text="",
                                     variable=self.chiedi_conferma,
                                     width=36, progress_color=ACCENT2,
                                     switch_height=18, switch_width=36)
        self.sw_conf.pack(side="right", padx=(0, 6), pady=7)
        ctk.CTkLabel(bottom, text="✓", font=("Segoe UI", 11),
                     text_color=SUBTEXT).pack(side="right", pady=7)

        self.btn_history = ctk.CTkButton(bottom, text="☰",
                                         font=("Segoe UI", 16),
                                         fg_color="transparent",
                                         hover_color=BORDER,
                                         text_color=SUBTEXT,
                                         width=42, height=42,
                                         corner_radius=12,
                                         command=self._apri_storico)
        self.btn_history.pack(side="right", padx=(0, 4), pady=7)

        self.btn_invia = ctk.CTkButton(bottom, text="▶",
                                       font=("Segoe UI", 14, "bold"),
                                       fg_color=ACCENT2,
                                       hover_color=ACCENT,
                                       text_color=TEXT,
                                       width=42, height=42,
                                       corner_radius=12,
                                       command=self._invia_testo)
        self.btn_invia.pack(side="right", padx=(0, 6), pady=7)

    def _anima_onda(self):
        c = self.canvas
        c.delete("all")
        W, H = 392, 260
        cx, cy = W // 2, H // 2

        c.create_rectangle(0, 0, W, H, fill=PANEL, outline="")

        if self.parlando or self.registrando:
            self.amp_target = 28.0
        elif self.elaborando:
            self.amp_target = 10.0
        else:
            self.amp_target = 0.0
        self.amp_corrente += (self.amp_target - self.amp_corrente) * 0.12

        amp = self.amp_corrente
        ang = self.onda_angolo

        if self.registrando:
            col_main, col_ring, col_spike = GREEN, GREEN, GREEN
            vel = 0.10
        elif self.parlando:
            col_main, col_ring, col_spike = ACCENT, ACCENT2, ACCENT3
            vel = 0.07
        elif self.elaborando:
            col_main, col_ring, col_spike = ACCENT3, ACCENT2, ACCENT3
            vel = 0.09
        elif self.attivo:
            col_main, col_ring, col_spike = ACCENT2, BORDER, ACCENT2
            vel = 0.018
        else:
            col_main, col_ring, col_spike = SUBTEXT, BORDER, SUBTEXT
            vel = 0.006

        R_CORE  = 34
        R_RING1 = 55
        R_RING2 = 76
        R_RING3 = 94

        if amp > 1:
            N = 36
            for i in range(N):
                th = i * (2 * math.pi / N) + ang * 0.35
                variation = abs(math.sin(th * 3 + ang * 9)) * 0.6 + 0.4
                spk_len = amp * variation
                r0 = R_RING2 + 6
                r1 = r0 + spk_len
                x1 = cx + r0 * math.cos(th)
                y1 = cy + r0 * math.sin(th)
                x2 = cx + r1 * math.cos(th)
                y2 = cy + r1 * math.sin(th)
                w = 2 if variation > 0.7 else 1
                c.create_line(x1, y1, x2, y2, fill=col_spike, width=w)

        delta = amp * 0.12 * math.sin(ang * 8)

        r3 = R_RING3 + delta * 0.5
        c.create_arc(cx-r3, cy-r3, cx+r3, cy+r3,
                     start=math.degrees(ang * 0.8), extent=130,
                     style="arc", outline=BORDER, width=1, dash=(4, 8))
        c.create_arc(cx-r3, cy-r3, cx+r3, cy+r3,
                     start=math.degrees(ang * 0.8) + 200, extent=100,
                     style="arc", outline=BORDER, width=1, dash=(4, 8))

        r2 = R_RING2 + delta * 0.7
        c.create_arc(cx-r2, cy-r2, cx+r2, cy+r2,
                     start=math.degrees(-ang * 1.1), extent=150,
                     style="arc", outline=col_ring, width=1, dash=(6, 6))
        c.create_arc(cx-r2, cy-r2, cx+r2, cy+r2,
                     start=math.degrees(-ang * 1.1) + 220, extent=100,
                     style="arc", outline=col_ring, width=1, dash=(3, 9))

        r1 = R_RING1 + delta
        c.create_arc(cx-r1, cy-r1, cx+r1, cy+r1,
                     start=math.degrees(ang * 1.4), extent=110,
                     style="arc", outline=col_main, width=2)
        c.create_arc(cx-r1, cy-r1, cx+r1, cy+r1,
                     start=math.degrees(ang * 1.4) + 175, extent=110,
                     style="arc", outline=col_main, width=2)

        for tick_ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
            xt = cx + (R_RING2 + 14) * math.cos(tick_ang)
            yt = cy + (R_RING2 + 14) * math.sin(tick_ang)
            xe = cx + (R_RING2 + 22) * math.cos(tick_ang)
            ye = cy + (R_RING2 + 22) * math.sin(tick_ang)
            c.create_line(xt, yt, xe, ye, fill=col_ring, width=2)

        glow = R_CORE
        if self.attivo and not self.parlando and not self.registrando and not self.elaborando:
            glow += 1.5 * math.sin(ang * 2.8)
        c.create_oval(cx-glow, cy-glow, cx+glow, cy+glow,
                      outline=col_main, width=2)

        c.create_oval(cx-5, cy-5, cx+5, cy+5, fill=col_main, outline="")

        self.onda_angolo += vel
        self.root.after(30, self._anima_onda)

    def _log(self, testo, tipo="cmd"):
        timestamp = time.strftime("%H:%M:%S")
        self.storico_log.append({"time": timestamp, "tipo": tipo, "testo": testo})

    def _set_subtitles(self, user_txt=None, travis_txt=None, travis_color=TEXT):
        def _do():
            if user_txt is not None:
                self.user_lbl.configure(text=f"> {user_txt}")
            if travis_txt is not None:
                self.travis_lbl.configure(text=travis_txt, text_color=travis_color)
        self.root.after(0, _do)

    def _set_stato(self, testo, colore=ACCENT):
        self.stato_lbl.configure(text=f"● {testo.upper()}", text_color=colore)

    def safe_stato(self, testo, colore=ACCENT):
        self.root.after(0, lambda: self._set_stato(testo, colore))

    def safe_set_parlando(self, v):
        self.root.after(0, lambda: setattr(self, "parlando", v))

    def safe_set_registrando(self, v):
        self.root.after(0, lambda: setattr(self, "registrando", v))

    def safe_set_elaborando(self, v):
        self.root.after(0, lambda: setattr(self, "elaborando", v))

    def is_attivo(self):
        return self.attivo

    def _toggle(self):
        self.attivo = not self.attivo
        if self.attivo:
            self.btn_toggle.configure(text="⏸", text_color=ACCENT)
            self._set_stato("Attivo", ACCENT)
            self._set_subtitles(travis_txt="Dimmi 'Travis' per attivarmi.")
        else:
            self.btn_toggle.configure(text="▶", text_color=SUBTEXT)
            self._set_stato("Standby", SUBTEXT)
            self._set_subtitles(travis_txt="Sistema in pausa.", travis_color=SUBTEXT)
            self.conferma_valore = False
            self.conferma_event.set()

    def _apri_storico(self):
        win = HistoryWindow(self.root, self.storico_log)
        win.grab_set()

    def _invia_testo(self, event=None):
        comando = self.input_var.get().strip()
        if not comando:
            return
        self.input_var.set("")
        self._set_subtitles(user_txt=comando)
        self._log(comando, "cmd")
        threading.Thread(target=self._esegui_comando, args=(comando,), daemon=True).start()

    def _avvia_travis(self):
        threading.Thread(target=self._carica_modelli, daemon=True).start()

    def _carica_modelli(self):
        def cb(msg):
            self.safe_stato(msg, SUBTEXT)
            self._set_subtitles(travis_txt=msg, travis_color=SUBTEXT)
        try:
            self.core.init_models(status_callback=cb)
            self.root.after(0, self._on_pronti)
        except Exception as e:
            self.safe_stato("Errore", RED)
            self._set_subtitles(travis_txt=f"Errore: {e}", travis_color=RED)

    def _on_pronti(self):
        self.attivo = True
        self._set_stato("Pronto", ACCENT)
        self.btn_toggle.configure(text="⏸", text_color=ACCENT)
        threading.Thread(target=self._loop_wake_word, daemon=True).start()
        threading.Thread(target=self._parla, args=("Sistema pronto.",), daemon=True).start()

    def _parla(self, testo, wait=False):
        def on_start():
            self.safe_set_parlando(True)
            self._set_subtitles(travis_txt=testo)
            self._log(testo, "travis")
        def on_end():
            self.safe_set_parlando(False)
        self.core.parla(testo, on_start=on_start, on_end=on_end, wait=wait)

    def _loop_wake_word(self):
        while not self.stop_event.is_set():
            try:
                def on_detect():
                    self.safe_stato("In ascolto...", GREEN)
                    threading.Thread(target=self._parla, args=("Dimmi pure.",), daemon=True).start()
                    threading.Thread(target=self._ascolta_ed_esegui, daemon=True).start()

                self.core.aspetta_wake_word(
                    active_check_callback=self.is_attivo,
                    on_detect_callback=on_detect,
                    stop_event=self.stop_event
                )
                while (self.parlando or self.registrando) and not self.stop_event.is_set():
                    time.sleep(0.4)
            except Exception as e:
                print(f"[wake word error] {e}")
                time.sleep(1)

    def _ascolta_ed_esegui(self):
        self.safe_set_registrando(True)
        try:
            def cb(msg):
                self.safe_stato(msg, GREEN)
            comando = self.core.ascolta_con_silenzio(status_callback=cb)
            if comando:
                self._set_subtitles(user_txt=comando)
                self._log(comando, "cmd")
                self._esegui_comando(comando)
            else:
                self.safe_stato("Pronto", ACCENT)
        except Exception as e:
            print(f"[ascolto error] {e}")
        finally:
            self.safe_set_registrando(False)
            if self.attivo:
                self.safe_stato("Pronto", ACCENT)

    def _click_esegui(self):
        self.conferma_valore = True
        self.conferma_event.set()

    def _click_annulla(self):
        self.conferma_valore = False
        self.conferma_event.set()

    def _mostra_conferma(self):
        self.conferma_frame.pack(pady=6)

    def _nascondi_conferma(self):
        self.conferma_frame.pack_forget()

    def _esegui_comando(self, comando):
        if not comando:
            return

        if "spegniti" in comando.lower() or "esci" in comando.lower():
            self._parla("Arrivederci.")
            self.root.after(1200, self._on_closing)
            return

        risultato = self.core.gestisci_spotify(comando)
        if risultato:
            self._parla(risultato)
            return

        self.safe_stato("Elaboro...", ACCENT2)
        self.safe_set_elaborando(True)
        risposta = self.core.chiedi_ai(comando)
        codice = self.core.pulisci_codice(risposta)
        self.safe_set_elaborando(False)
        print(f"[codice generato]\n{codice}")

        if not codice:
            self._parla("Non ho capito cosa fare.")
            return

        confermato = True
        if self.chiedi_conferma.get():
            self.safe_stato("Attesa conferma", RED)
            self._set_subtitles(travis_txt=f"Codice pronto. Eseguo?", travis_color=ACCENT)
            self._log(f"[CODICE]\n{codice}", "cmd")
            self.root.after(0, self._mostra_conferma)
            self._parla("Eseguo il codice generato?", wait=True)
            self.conferma_event.clear()
            self.conferma_event.wait()
            confermato = self.conferma_valore
            self.root.after(0, self._nascondi_conferma)

        if confermato:
            self.safe_stato("Eseguito", GREEN)
            try:
                self.core.esegui_codice_sicuro(codice)
                self._parla("Fatto.")
            except Exception as e:
                self.safe_stato("Errore", RED)
                self._set_subtitles(travis_txt=f"Errore: {e}", travis_color=RED)
                self._log(f"Errore: {e}", "err")
                self._parla("Errore durante l'esecuzione.")
        else:
            self.safe_stato("Annullato", SUBTEXT)
            self._parla("Annullato.")

    def _on_closing(self):
        self.attivo = False
        self.stop_event.set()
        self.conferma_valore = False
        self.conferma_event.set()
        self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = TravisUI(root)
    root.mainloop()
