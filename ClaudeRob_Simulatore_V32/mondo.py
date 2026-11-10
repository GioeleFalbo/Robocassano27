"""
MONDO SIMULATO: fisica del robot, sensori e telecamere.

Il robot simulato ha gli stessi componenti di quello vero:
  - 4 servo a rotazione continua (PCA9685 0x41, canali 15/4 sinistra, 0/11 destra) -> trazione skid-steer
  - servo braccio (canale 4) e pinza (canale 11) sulla PCA9685 0x40
  - 3 VL53L0X (sinistra, fronte, destra) e giroscopio (heading, pitch, roll) "letti" dall'Arduino
  - switch di avvio e switch pallina
  - camera della linea (440x260, guarda in basso davanti al robot)
  - camera dell'arena (inclinata in avanti)
  - 2 LED su relè (GPIO 22 e 23)

I numeri in CONFIG sono STIME ragionevoli: misurateli sul robot vero e correggeteli.
"""
import math
import random
import sys
import numpy as np
import cv2

CONFIG = {
    # --- trazione ---
    "vmax": 30.0,            # cm/s di una ruota con servo al massimo (stima: ~100 rpm, ruota 6 cm)
    "neutro": 321,           # tick PCA9685 a cui il servo sta fermo (come motor_range "stop")
    "zona_morta": 9,         # tick attorno al neutro in cui il servo non si muove
    # [V26] MODELLO DEI SERVO. "lineare" = come prima (velocità proporzionale ai tick fino a tick_max).
    # "reale" = curva misurata sulla scatola nera del robot vero (23/10): il servo arriva quasi subito al
    # massimo (sopra ~40 tick la velocità non cresce più), quindi a velocità 47 una correzione di sterzo
    # sotto ~40 non fa girare il robot. Velocità misurata ~10-12 cm/s, rotazione sul posto ~35 gradi/s.
    "servo_modello": "reale",
    "servo_k": 25.0,         # tick: costante della curva 1 - exp(-(tick - zona_morta) / servo_k)
    "vmax_reale": 12.6,      # cm/s al massimo (modello "reale")
    "slittamento_reale": 2.2,  # skid-steer col modello "reale" (rotazione sul posto ~35 gradi/s come il robot vero)
    "imu_ritardo": 0.10,     # [V27] s: il giroscopio del robot vero risponde in ritardo (BNO055 + filtro); con
                             # tau_servo_reale la rotazione si vede 0,2 s dopo il comando, come nelle scatole nere
    "tau_servo_reale": 0.10, # [V27] s: risposta dei servo col modello "reale" (avvio e frenata più lenti)
    "bussola_distorsione": 0.0,  # [V26] gradi: errore del giroscopio che dipende dalla direzione (BNO055 in NDOF)
    "tick_max": 89,          # tick dal neutro per arrivare alla velocità massima (321->410)
    "tau_servo": 0.06,       # s, ritardo di risposta dei servo
    "guadagni": {15: 1.00, 4: 0.98, 0: 1.02, 11: 1.01},   # piccole differenze tra servo (nessuno è identico)
    "carreggiata": 15.0,     # cm tra ruote sinistre e destre
    "slittamento": 1.4,      # skid-steer: in curva le ruote strisciano, la rotazione è più lenta
    "lunghezza_robot": 21.5,  # cm (MISURATA 12/10)
    "larghezza_robot": 15.6,  # cm (MISURATA 12/10: 15; dai file STL 15,6 con le alette di paraurti)
    "robot_davanti": 11.5,    # cm dal centro delle ruote al muso (MISURATA): il retro è a 21,5 - 11,5 = 10 cm
    # --- braccio e pinza ---
    "vel_servo_braccio": 300.0,   # gradi/s
    "zona_presa": (10.0, 21.0, 4.5),  # la pinza abbassata afferra tra 10 e 21 cm davanti al centro, ±4,5 cm di lato
    "rilascio_avanti": 17.0,      # cm davanti al centro dove cade la pallina aprendo la pinza (braccio a 116°)
    # --- camera linea (prospettica: inquadratura a trapezio sul pavimento) ---
    "cam_linea_avanti": 12.0,     # cm davanti al centro del robot (dalle foto: la camera è sul muso)
    "cam_linea_altezza": 8.3,     # cm dal pavimento (MISURATA sul robot: 83 mm)
    "cam_linea_inclinazione": 15.0,  # gradi in avanti rispetto alla verticale (MISURATA dalle foto col righello)
    "cam_linea_hfov": 80.0,       # gradi di campo visivo orizzontale (MISURATO dal marcatore verde 2,5 cm)
    "cam_linea_fps": 10,          # come FrameRate = 10 nel vostro codice
    # --- camera arena ---
    "cam_arena_altezza": 9.8,     # cm dal pavimento (MISURATA sul robot: 98 mm)
    "cam_arena_inclinazione": 26.0,  # gradi verso il basso (MISURATA dalle foto con la pallina a 10/20/40 cm)
    "cam_arena_hfov": 68.0,       # gradi di campo visivo orizzontale (dalla pallina 10 cm a destra)
    "cam_arena_avanti": 10.5,     # cm davanti al centro del robot
    "cam_arena_portata": 160.0,   # cm oltre i quali YOLO non riconosce più gli oggetti
    # --- VL53L0X (avanti, lato, direzione rispetto al robot) ---
    "tof": [(1.5, -7.5, -90.0), (11.5, 0.0, 0.0), (1.5, 7.5, 90.0)],   # MISURATI: frontale al centro del muso,
                                                                       # laterali sui fianchi 10 cm dietro il muso
    "altezza_muri": 11.5,         # cm (MISURATA): i laser (5,8 e 6,4 cm) passano sopra le palline (4,5 cm)
    "tof_max": 120,               # cm, portata del VL53L0X (modo normale)
    "tof_fuori_portata": 0,       # valore inviato quando non c'è niente entro la portata: 0 COME SUL ROBOT VERO
                                  # (prima il simulatore mandava 200 e l'errore dell'uscita non si vedeva)
    "tof_rumore": 0.7,            # cm
    "tof_periodo": 0.033,         # s (circa 30 letture al secondo)
    # --- tempi di calcolo del Raspberry Pi 5 (stime) ---
    "yolo_inferenza": 0.045,      # s per una predizione NCNN 224x224
    "yolo_sbaglia_falsi_verdi": False,
    "yolo_porta_solo_ingresso": False,
    # --- [V29] GUASTI visti sul robot vero (scatola nera 03/11) ---
    "imu_bloccato": False,        # True = il giroscopio manda sempre (-2, -2, 0) (BNO055 bloccato, laser vivi)
    "imu_blocca_da": 0.0,         # s: da quando il giroscopio si blocca
    "tof_fr_spurie": 0.0,         # probabilità che una lettura del laser FRONTALE sia un valore a caso (3-480 cm)
    "tof_lat_spurie": 0.0,        # come sopra per i laser laterali (03/11: frontale 15%, sinistro 10% di salti)
    "arduino_muto_da": -1.0,      # s: da quando l'Arduino smette di mandare dati (-1 = mai; ottobre: 76-156 s)
    "arduino_muto_per": 1e9,      # s: per quanto tempo resta muto
    "yolo_argento_rampa": False,         # [V28] True = all'inizio di ogni rampa (primo secondo) YOLO vede un falso
                                         # ARGENTO, come nella scatola nera del 29/10 (secondo 93,6)
    "yolo_argento_falso": False,         # True = tra 2,5 e 6,3 s YOLO vede un falso ARGENTO in mezzo alla linea (prova FIX 46)
    "yolo_porta_nessuna": False,         # True = TrianFull3 non vede nessuna porta: conta solo la striscia nera   # True = TrianFull3 vede come porta SOLO l'ingresso, l'uscita no
    "yolo_porta_confonde": False,        # True = TrianFull3 vede anche l'ingresso come classe 0 (porta), come nel video dell'8/10   # True = il modello prende i falsi verdi per verdi validi
    "yolo_caricamento": 0.35,     # s per caricare un modello da disco
    "scrittura_foto": 0.010,      # s per salvare un jpg su SD
    # --- campo a piastrelle con rampe (V22) ---
    "tof_altezza": [5.8, 6.4, 5.8],   # cm dal pavimento dei raggi laser (sx, fronte, dx): servono per le rampe
    "scivolo_laterale": 10.0,     # cm/s di scivolamento verso valle per sin(inclinazione laterale), ruote in moto
    "scivolo_fermo": 4.0,         # cm/s di scivolamento laterale a robot fermo (i servo frenano poco)
    "scivolo_pendenza": 4.0,      # cm/s di discesa lungo la rampa per sin(pendenza) a robot fermo
    "altalena_vel": 60.0,         # gradi/s con cui l'altalena bascula
    "gradino_max": 1.5,           # cm: gradino più alto che le ruote riescono a salire
    "lop_fermo_s": 45.0,          # s senza nuove piastrelle dopo i quali il capitano chiama la LoP (sulla linea)
    "caduta_min": 6.0,            # cm: dislivello oltre il quale il robot "cade" da un bordo rialzato
}

PX = 10            # risoluzione del campo disegnato: 10 pixel per cm
LIN_W, LIN_H = 440, 260
CLASSI_CROSS = {"Bi": 0, "Di": 1, "Dx": 2, "Fr": 3, "In": 4, "Ln": 5, "Ro": 6, "Sx": 7}


class FineSimulazione(BaseException):
    """Interrompe il programma del robot quando la simulazione è finita."""


def _dir(h):
    r = math.radians(h)
    return math.sin(r), -math.cos(r)          # avanti


def _dx(h):
    r = math.radians(h)
    return math.cos(r), math.sin(r)           # destra


def _dentro_poli(px, py, poli):
    ins = False
    n = len(poli)
    for i in range(n):
        x1, y1 = poli[i]
        x2, y2 = poli[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            xi = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if px < xi:
                ins = not ins
    return ins


def _dist_punto_segmento(px, py, a, b):
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    L = vx * vx + vy * vy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / L))
    qx, qy = ax + t * vx, ay + t * vy
    return math.hypot(px - qx, py - qy)


def _raggio_segmento(ox, oy, dx, dy, a, b):
    """Distanza lungo il raggio (ox,oy)+t(dx,dy) fino al segmento a-b, oppure None."""
    ax, ay = a
    bx, by = b
    ex, ey = bx - ax, by - ay
    den = dx * ey - dy * ex
    if abs(den) < 1e-9:
        return None
    t = ((ax - ox) * ey - (ay - oy) * ex) / den
    u = ((ax - ox) * dy - (ay - oy) * dx) / den
    if t >= 0 and 0 <= u <= 1:
        return t
    return None


class Mondo:
    def __init__(self, campo, cfg=None, seme=1):
        self.C = campo
        self.cfg = dict(CONFIG)
        if cfg:
            self.cfg.update(cfg)
        random.seed(seme)
        self.t = 0.0
        p = campo["partenza"]
        self.x, self.y, self.h = p["x"], p["y"], p["heading"]
        self.pwm = {}                     # (indirizzo, canale) -> tick "off"
        self.ruote = {15: 0.0, 4: 0.0, 0: 0.0, 11: 0.0}   # velocità reali (frazione)
        self.braccio = 40.0
        self.pinza = 160.0
        self.pinza_prec = 160.0
        self.led = {22: False, 23: False}
        self.switch_avvio = False
        self.palline = [dict(b, stato="libera") for b in campo["palline"]]
        self.tenuta = None
        self.robot = None                 # istanza Robot del vostro codice (si collega da sola)
        self.globali = None               # variabili globali di RwdFoto.py
        self.pitch = 0.0
        self.roll = 0.0
        # tempi
        self.prossimo_frame = 0.0
        self.prossimo_tof = 0.0
        self.prossima_reg = 0.0
        self.tempo_max = 420.0
        self.fine = None
        self.fine_lanciata = False
        self.ultimo_movimento = (0.0, self.x, self.y)
        self.fermo_su_rosso = 0.0
        # dati per il replay
        self.campioni = []
        self.eventi = []
        self.log = []
        self.stati = []                   # tabella stringhe "funzione attiva"
        self._idx_stati = {}
        self.yolo_vista = ""              # ultima classe vista dalla camera linea
        self.tof_val = (200, 200, 200)
        self.frame_pose = (self.x, self.y, self.h)
        self.arena_pose = (self.x, self.y, self.h)
        self.urti = 0
        self._ultimo_urto = -10
        self.traguardi = set()
        self.in_arena_visto = False
        self.ostacolo_visto = False
        self.statistiche = {"predizioni_yolo": 0, "caricamenti_yolo": 0, "cicli_seguilinea": 0}
        self._muri = list(campo["muri"])
        self.nuovo = "percorso" in campo          # campo a piastrelle RCJ 2026 (V22)
        o = campo.get("ostacolo")
        self._rett_ost = [(o["x"], o["y"], o["x"] + o["w"], o["y"] + o["h"])] if o else []
        self._rett_ost += [tuple(r) for r in campo.get("ostacoli", [])]
        self._ostacolo = []
        for x0, y0, x1, y1 in self._rett_ost:
            self._ostacolo += [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
        self._triangoli = []
        for tr in campo["triangoli"]:
            pts = tr["poli"]
            for i in range(3):
                self._triangoli.append((pts[i], pts[(i + 1) % 3]))
        self._solidi = self._muri + self._ostacolo + self._triangoli
        # [Sim V32] tunnel sotto il ponte: le sue pareti valgono solo per chi sta sotto; se il robot è più alto
        # dello spazio libero, gli imbocchi sono un muro (il robot vero sbatterebbe contro il ponte)
        self._sotto = campo.get("sotto", {})
        self._pareti_tunnel = []
        for t in campo.get("tunnel", []):
            self._pareti_tunnel += t["pareti"]
            libero = min(self._sotto[tuple(cc)]["tetto"] - self._sotto[tuple(cc)]["z"] for cc in t["celle"])
            if self.cfg.get("altezza_robot", 21.0) >= libero:
                x0, y0, x1, y1 = t["rett"]
                if t["asse"] == "EW":
                    self._pareti_tunnel += [((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))]
                else:
                    self._pareti_tunnel += [((x0, y0), (x1, y0)), ((x0, y1), (x1, y1))]
        self._solidi_base = self._solidi
        self._basso = False                       # [Sim V32] True = il robot è al livello del tunnel
        self._dossi_alti = list(campo.get("dossi", []))
        self._dossi_bassi = [d for d in self._dossi_alti
                             if (int(((d[0] + d[2]) / 2) // 30), int(((d[1] + d[3]) / 2) // 30)) not in self._sotto]
        self._dossi_bassi += list(campo.get("dossi_sotto", []))
        self._dossi_attivi = self._dossi_alti
        self.z = 0.0
        self.frame_att = (0.0, 0.0, 0.0)
        self.sollevato = False
        self.avviato = False
        if self.nuovo:
            self._init_rcj()
        import realismo                           # [Sim V32] luci, ombre, LED, verdi diversi, cono del laser
        self.real = realismo.Realismo(self)
        self._disegna_campo()

    # ------------------------------------------------------------------
    #  DISEGNO DEL CAMPO (vista dall'alto, per la camera della linea)
    # ------------------------------------------------------------------
    def _disegna_campo(self):
        C = self.C
        W, H = C["larghezza"] * PX, C["altezza"] * PX
        img = np.full((H, W, 3), 245, np.uint8)
        # giunture delle piastrelle (appena visibili)
        for xx in range(0, C["larghezza"] + 1, 30):
            cv2.line(img, (xx * PX, 0), (xx * PX, H), (228, 228, 228), 2)
        for yy in range(0, C["altezza"] + 1, 30):
            cv2.line(img, (0, yy * PX), (W, yy * PX), (228, 228, 228), 2)
        if C.get("rampa"):
            r = C["rampa"]
            cv2.rectangle(img, (r["x"] * PX, r["y"] * PX), ((r["x"] + r["w"]) * PX, (r["y"] + r["h"]) * PX), (232, 236, 240), -1)
        for (cc, rr), q in C.get("quote", {}).items():
            if q["tipo"] != "piana" or q["z"] > 0.5:
                col = {"rampa": (232, 236, 240), "banca": (236, 232, 240), "altalena": (228, 238, 238)}.get(q["tipo"], (240, 242, 245))
                cv2.rectangle(img, (int(cc * 30 * PX) + 2, int(rr * 30 * PX) + 2), (int((cc + 1) * 30 * PX) - 2, int((rr + 1) * 30 * PX) - 2), col, -1)
        for x0, y0, x1, y1 in C.get("dossi", []):
            cv2.rectangle(img, (int(x0 * PX), int(y0 * PX)), (int(x1 * PX), int(y1 * PX)), (236, 236, 236), -1)
        lw = int(round(1.8 * PX))
        for linea in C["linee"]:
            pts = np.array([[int(px * PX), int(py * PX)] for px, py in linea], np.int32)
            cv2.polylines(img, [pts], False, (25, 25, 25), lw, cv2.LINE_AA)
        for a, b in C.get("detriti", []):
            cv2.line(img, (int(a[0] * PX), int(a[1] * PX)), (int(b[0] * PX), int(b[1] * PX)), (120, 170, 210), 3, cv2.LINE_AA)
        def rett(d, col):
            cv2.rectangle(img, (int(d["x"] * PX), int(d["y"] * PX)),
                          (int((d["x"] + d["w"]) * PX), int((d["y"] + d["h"]) * PX)), col, -1)
        for v in C["verdi"]:
            rett(v, v.get("tono", (40, 170, 40)))           # [Sim V32] tonalità diverse (realismo.py)
        rett(C["argento"], (192, 192, 192))
        rett(C["nero_uscita"], (25, 25, 25))
        rett(C["rosso"], (30, 30, 220))
        for x0, y0, x1, y1 in self._rett_ost:
            rett({"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}, (90, 140, 190))
        for tr in C["triangoli"]:
            col = (60, 160, 60) if tr["colore"] == "verde" else (50, 50, 200)
            cv2.fillPoly(img, [np.array([[int(a * PX), int(b * PX)] for a, b in tr["poli"]], np.int32)], col)
        for a, b in C["muri"]:
            cv2.line(img, (int(a[0] * PX), int(a[1] * PX)), (int(b[0] * PX), int(b[1] * PX)), (150, 150, 150), 12)
        self.raster = img
        # [Sim V32] il pavimento del TUNNEL (si vede da sotto il ponte) e le mappe della luce
        self.raster_sotto = None
        if self._sotto:
            sot = img.copy()
            for (cc, rr) in self._sotto:
                cv2.rectangle(sot, (cc * 30 * PX, rr * 30 * PX), ((cc + 1) * 30 * PX, (rr + 1) * 30 * PX), (245, 245, 245), -1)
            for x0, y0, x1, y1 in C.get("dossi_sotto", []):
                cv2.rectangle(sot, (int(x0 * PX), int(y0 * PX)), (int(x1 * PX), int(y1 * PX)), (236, 236, 236), -1)
            for linea in C.get("linee_sotto", []):
                pts = np.array([[int(px * PX), int(py * PX)] for px, py in linea], np.int32)
                cv2.polylines(sot, [pts], False, (25, 25, 25), lw, cv2.LINE_AA)
            for a, b in self._pareti_tunnel:
                cv2.line(sot, (int(a[0] * PX), int(a[1] * PX)), (int(b[0] * PX), int(b[1] * PX)), (225, 225, 225), 12)
            self.raster_sotto = sot
        self.luce = self.luce_sotto = None
        if self.real.attivo_luci:
            self.luce = np.clip(self.real.mappa_luce(PX) * 100, 0, 255).astype(np.uint8)
            if self._sotto:
                self.luce_sotto = np.clip(self.real.mappa_luce(PX, sotto=True) * 100, 0, 255).astype(np.uint8)

    # ------------------------------------------------------------------
    #  HARDWARE: PCA9685 e LED (chiamati dai finti moduli)
    # ------------------------------------------------------------------
    def scrivi_pwm(self, indirizzo, canale, off):
        self.pwm[(indirizzo, canale)] = off

    def spegni_tutto(self, indirizzo):
        for k in list(self.pwm):
            if k[0] == indirizzo:
                self.pwm[k] = 0

    def _frazione_servo(self, tick):
        if not tick:
            return 0.0                    # nessun segnale: servo fermo
        c = self.cfg
        d = tick - c["neutro"]
        if abs(d) <= c["zona_morta"]:
            return 0.0
        if c.get("servo_modello") == "reale":
            f = 1.0 - math.exp(-(abs(d) - c["zona_morta"]) / c["servo_k"])
            return math.copysign(f, d)
        f = (abs(d) - c["zona_morta"]) / (c["tick_max"] - c["zona_morta"])
        return math.copysign(min(1.0, f), d)

    def _angolo_servo(self, tick, attuale):
        if not tick:
            return attuale
        return max(0.0, min(180.0, (530 - tick) * 180.0 / 420.0))

    # ------------------------------------------------------------------
    #  FISICA
    # ------------------------------------------------------------------
    def _rampa(self, x, y, h):
        r = self.C["rampa"]
        if r["x"] <= x <= r["x"] + r["w"] and r["y"] <= y <= r["y"] + r["h"]:
            a = math.radians(h - r["salita_verso"])
            return r["pendenza"] * math.cos(a), r["pendenza"] * math.sin(a)
        return 0.0, 0.0

    def _collide(self, x, y, h=None):
        """Il robot è un rettangolo (lunghezza x larghezza): controlla se tocca muri, ostacolo o triangoli."""
        h = self.h if h is None else h
        Lf = self.cfg.get("robot_davanti", self.cfg["lunghezza_robot"] / 2)   # muso
        Lb = self.cfg["lunghezza_robot"] - Lf                                  # retro
        W = self.cfg["larghezza_robot"] / 2
        dx, dy = _dir(h)
        rx, ry = _dx(h)
        for a, b in self._solidi:
            # estremi del segmento nel sistema del robot (f = avanti, l = destra)
            fa = (a[0] - x) * dx + (a[1] - y) * dy
            la = (a[0] - x) * rx + (a[1] - y) * ry
            fb = (b[0] - x) * dx + (b[1] - y) * dy
            lb = (b[0] - x) * rx + (b[1] - y) * ry
            # ritaglio di Liang-Barsky del segmento sul rettangolo
            t0, t1 = 0.0, 1.0
            ok = True
            for p, q in ((-(fb - fa), fa + Lb), (fb - fa, Lf - fa), (-(lb - la), la + W), (lb - la, W - la)):
                if p == 0:
                    if q < 0:
                        ok = False
                        break
                else:
                    r = q / p
                    if p < 0:
                        t0 = max(t0, r)
                    else:
                        t1 = min(t1, r)
                    if t0 > t1:
                        ok = False
                        break
            if ok:
                return True
        return False

    def passo(self, dt):
        c = self.cfg
        tau = c["tau_servo_reale"] if c.get("servo_modello") == "reale" else c["tau_servo"]
        a = min(1.0, dt / tau)
        for ch in self.ruote:
            obiettivo = self._frazione_servo(self.pwm.get((0x41, ch), 0)) * c["guadagni"][ch]
            self.ruote[ch] += (obiettivo - self.ruote[ch]) * a
        reale = c.get("servo_modello") == "reale"
        vmax = c["vmax_reale"] if reale else c["vmax"]
        slitt = c["slittamento_reale"] if reale else c["slittamento"]
        vl = (self.ruote[15] + self.ruote[4]) / 2 * vmax
        vr = -(self.ruote[0] + self.ruote[11]) / 2 * vmax      # servo destri montati a specchio
        v = (vl + vr) / 2
        w = math.degrees((vl - vr) / (c["carreggiata"] * slitt))   # gradi/s, orario positivo
        if self.nuovo:
            self._muovi_3d(dt, v, w)
        else:
            self.pitch, self.roll = self._rampa(self.x, self.y, self.h)
            if self.pitch:
                v *= 1 - 0.6 * math.sin(math.radians(self.pitch)) * (1 if v > 0 else -1)
            nh = (self.h + w * dt) % 360
            if not self._collide(self.x, self.y, nh) or self._collide(self.x, self.y, self.h):
                self.h = nh                      # la rotazione è bloccata se lo spigolo urta un muro
            dx, dy = _dir(self.h)
            nx, ny = self.x + v * dx * dt, self.y + v * dy * dt
            if self._collide(nx, ny) and not self._collide(self.x, self.y):
                if self.t - self._ultimo_urto > 1.0:
                    self.urti += 1
                    self.evento("urto", "Urto contro muro/ostacolo")
                self._ultimo_urto = self.t
            else:
                self.x, self.y = nx, ny
        # braccio e pinza
        vmax = c["vel_servo_braccio"] * dt
        for nome, ch in (("braccio", 4), ("pinza", 11)):
            att = getattr(self, nome)
            ob = self._angolo_servo(self.pwm.get((0x40, ch), 0), att)
            setattr(self, nome, att + max(-vmax, min(vmax, ob - att)))
        self._gestisci_pinza()
        self.pinza_prec = self.pinza

    def _gestisci_pinza(self):
        dx, dy = _dir(self.h)
        rx, ry = _dx(self.h)
        if self.tenuta is None and self.pinza_prec >= 105 > self.pinza and self.braccio > 160:
            f0, f1, lat = self.cfg["zona_presa"]
            migliore = None
            for b in self.palline:
                if b["stato"] != "libera":
                    continue
                relx, rely = b["x"] - self.x, b["y"] - self.y
                f = relx * dx + rely * dy
                l = relx * rx + rely * ry
                if f0 <= f <= f1 and abs(l) <= lat:
                    if migliore is None or f < migliore[0]:
                        migliore = (f, b)
            if migliore:
                b = migliore[1]
                b["stato"] = "presa"
                self.tenuta = b
                self.evento("presa", f"Pallina {b['tipo']} ({b['id']}) presa con la pinza")
            else:
                self.evento("mancata", "Pinza chiusa a vuoto: nessuna pallina nella zona di presa")
        if self.tenuta is not None and self.pinza_prec <= 140 < self.pinza:
            b = self.tenuta
            self.tenuta = None
            d = self.cfg["rilascio_avanti"]
            b["x"], b["y"] = self.x + dx * d, self.y + dy * d
            for tr in self.C["triangoli"]:
                if _dentro_poli(b["x"], b["y"], tr["poli"]) or self._vicino_triangolo(b, tr):
                    giusto = (tr["colore"] == "verde") == (b["tipo"] == "argento")
                    b["stato"] = "salvata" if giusto else "sbagliata"
                    if self.nuovo:
                        self._salvataggio(b, giusto)
                    txt = f"Pallina {b['tipo']} ({b['id']}) nel triangolo {tr['colore'].upper()}"
                    self.evento("salvata" if giusto else "errore", txt + (" ✓" if giusto else " ✗ triangolo sbagliato"))
                    return
            b["stato"] = "libera"
            distanze = []
            for tr in self.C["triangoli"]:
                pts = tr["poli"]
                d = min(_dist_punto_segmento(b["x"], b["y"], pts[i], pts[(i + 1) % 3]) for i in range(3))
                distanze.append((d, tr["colore"]))
            d, col = min(distanze)
            self.evento("errore", f"Pallina {b['tipo']} ({b['id']}) lasciata FUORI dai triangoli, a {d:.0f} cm dal triangolo {col}")

    def _vicino_triangolo(self, b, tr):
        pts = tr["poli"]
        return min(_dist_punto_segmento(b["x"], b["y"], pts[i], pts[(i + 1) % 3]) for i in range(3)) < 3.0

    # ------------------------------------------------------------------
    #  SENSORI
    # ------------------------------------------------------------------
    def leggi_tof(self):
        dx, dy = _dir(self.h)
        rx, ry = _dx(self.h)
        out = []
        for fwd, lat, ang in self.cfg["tof"]:
            ox = self.x + dx * fwd + rx * lat
            oy = self.y + dy * fwd + ry * lat
            ddx, ddy = _dir(self.h + ang)
            best = None
            for a, b in self._solidi:
                d = _raggio_segmento(ox, oy, ddx, ddy, a, b)
                if d is not None and (best is None or d < best):
                    best = d
            if self.nuovo:
                # [V22] rampe, altalena e bordi rialzati: il raggio (alto qualche cm) può colpire il pavimento
                elev = self.pitch if ang == 0 else (self.roll if ang > 0 else -self.roll)
                hl = self.cfg["tof_altezza"][len(out)]
                d3 = self._raggio_3d(ox, oy, ddx, ddy, hl, elev, min(best if best is not None else 1e9, self.cfg["tof_max"]))
                if d3 is not None:
                    best = d3
            if self.real.cono:
                # [Sim V32] cono vero del VL53L1X (27 gradi): vede anche gli stipiti a lato della porta
                best = self.real.tof_cono(ox, oy, self.h + ang, self._solidi, _raggio_segmento, best)
                if best is None or best > self.cfg["tof_max"]:
                    out.append(self.cfg["tof_fuori_portata"])
                else:
                    out.append(max(1, int(round(best + random.gauss(0, self.real.rumore_tof(best))))))
                continue
            if best is None or best > self.cfg["tof_max"]:
                out.append(self.cfg["tof_fuori_portata"])
            else:
                out.append(max(1, int(round(best + random.gauss(0, self.cfg["tof_rumore"])))))
        return tuple(out)

    def _guasti_laser(self, val):
        # [V29] letture sbagliate a caso, come il laser frontale del robot vero il 03/11 (5, 54, 74, 134 cm...)
        pf, pl = self.cfg.get("tof_fr_spurie", 0.0), self.cfg.get("tof_lat_spurie", 0.0)
        if not pf and not pl:
            return val
        if not hasattr(self, "_rng_guasti"):
            self._rng_guasti = random.Random(4242)
        g = self._rng_guasti
        out = list(val)
        for i, p in ((0, pl), (1, pf), (2, pl)):
            if p and g.random() < p:
                out[i] = g.randint(3, 480)
        return tuple(out)

    def aggiorna_sensori_robot(self):
        r = self.robot
        if r is None:
            return
        # [V29] Arduino muto: niente dati nuovi (il thread di lettura vero dopo 0,3 s mette tutto a 0)
        m0 = self.cfg.get("arduino_muto_da", -1.0)
        if m0 >= 0 and m0 <= self.t < m0 + self.cfg.get("arduino_muto_per", 1e9):
            with r._lock:
                if 1_700_000_000.0 + self.t - r._last_packet_time > 0.3:
                    r._last_distances = (0, 0, 0)
                    r._last_imu = (0, 0, 0)
                    r._last_tilt = (0, 0)
                    r._last_switch = (False, False)
            return
        dist = self.cfg.get("bussola_distorsione", 0.0)
        # [V27] il giroscopio legge la direzione di "imu_ritardo" secondi fa (scatole nere 23 e 26/10: la
        # rotazione si vede 0,2 s dopo il comando e dopo lo stop il robot gira ancora di 5-7 gradi)
        rit = self.cfg.get("imu_ritardo", 0.0) if self.cfg.get("servo_modello") == "reale" else 0.0
        if not hasattr(self, "_storia_h"):
            self._storia_h = []
        self._storia_h.append((self.t, self.h))
        while len(self._storia_h) > 2 and self._storia_h[1][0] <= self.t - rit:
            self._storia_h.pop(0)
        h = self._storia_h[0][1] if rit else self.h
        # [V26] distorsione "magnetica": errore che cambia con la direzione (come un BNO055 vicino ai motori)
        err = dist * math.sin(math.radians(h - 30)) if dist else 0.0
        hd = int(round(h + err + random.gauss(0, 0.3))) % 360
        with r._lock:
            r._last_distances = getattr(self, "tof_robot", self.tof_val)       # [V29] con i guasti dei laser
            if self.cfg.get("imu_bloccato") and self.t >= self.cfg.get("imu_blocca_da", 0.0):
                r._last_imu = (-2, -2, 0)                                       # [V29] giroscopio bloccato (03/11)
            else:
                r._last_imu = (int(round(self.pitch)), int(round(self.roll)), hd)
            r._last_switch = (self.tenuta is not None, self.switch_avvio)
            r._last_tilt = (0, 0)
            r._last_packet_time = 1_700_000_000.0 + self.t     # Arduino "vivo" (come il thread di lettura vero)

    # ------------------------------------------------------------------
    #  CAMERA DELLA LINEA
    # ------------------------------------------------------------------
    def _terreno_da_pixel(self, u, v):
        """Punto del pavimento (avanti, destra) in cm, rispetto al centro del robot, visto dal pixel (u, v)."""
        c = self.cfg
        tau = math.radians(c["cam_linea_inclinazione"])
        f = (LIN_W / 2) / math.tan(math.radians(c["cam_linea_hfov"] / 2))
        xc, yc = (u - LIN_W / 2) / f, (v - LIN_H / 2) / f
        giu = math.cos(tau) + yc * math.sin(tau)          # componente del raggio verso il pavimento
        t = c["cam_linea_altezza"] / giu
        return c["cam_linea_avanti"] + t * (math.sin(tau) - yc * math.cos(tau)), t * xc

    def _impronta_linea(self, pose, att=None):
        """[V22] I 4 punti del campo (cm) inquadrati dagli angoli della camera della linea, in 3D:
        il robot può essere inclinato (rampa, altalena, tratto inclinato) e il pavimento davanti può
        avere un'altra pendenza (inizio e fine rampa): si interseca il raggio di ogni angolo con il
        piano del pavimento nel punto che la camera guarda."""
        c = self.cfg
        x, y, h = pose
        z, pit, rol = att or self.frame_att
        tau = math.radians(c["cam_linea_inclinazione"])
        fz = (LIN_W / 2) / math.tan(math.radians(c["cam_linea_hfov"] / 2))
        d0, d1 = _dir(h)
        r0, r1 = _dx(h)
        p, q = math.radians(pit), math.radians(rol)
        F = (math.cos(p) * d0, math.cos(p) * d1, math.sin(p))
        R = (math.cos(q) * r0, math.cos(q) * r1, math.sin(q))
        U = (F[1] * R[2] - F[2] * R[1], F[2] * R[0] - F[0] * R[2], F[0] * R[1] - F[1] * R[0])
        if U[2] < 0:
            U = (-U[0], -U[1], -U[2])
        av, al = c["cam_linea_avanti"], c["cam_linea_altezza"]
        Cx, Cy, Cz = x + F[0] * av + U[0] * al, y + F[1] * av + U[1] * al, z + F[2] * av + U[2] * al
        Lx, Ly = x + d0 * (av + 4) * math.cos(p), y + d1 * (av + 4) * math.cos(p)
        zP, sx, sy = self.quota(Lx, Ly)
        pts = []
        for u, v in [(0, 0), (LIN_W - 1, 0), (LIN_W - 1, LIN_H - 1), (0, LIN_H - 1)]:
            xc, yc = (u - LIN_W / 2) / fz, (v - LIN_H / 2) / fz
            a, b = math.sin(tau) - yc * math.cos(tau), -(math.cos(tau) + yc * math.sin(tau))
            ray = (F[0] * a + R[0] * xc + U[0] * b, F[1] * a + R[1] * xc + U[1] * b, F[2] * a + R[2] * xc + U[2] * b)
            den = ray[2] - sx * ray[0] - sy * ray[1]
            num = zP + sx * (Cx - Lx) + sy * (Cy - Ly) - Cz
            t = num / den if den < -1e-6 else 80.0
            if t <= 0 or t > 80:
                t = 80.0                      # il raggio non incontra il pavimento (cima della rampa)
            pts.append((Cx + t * ray[0], Cy + t * ray[1]))
        return pts

    def _omografia_linea(self, pose):
        if self.nuovo:
            pts = [(px * PX, py * PX) for px, py in self._impronta_linea(pose)]
            angoli_img = [(0, 0), (LIN_W - 1, 0), (LIN_W - 1, LIN_H - 1), (0, LIN_H - 1)]
            return cv2.getPerspectiveTransform(np.float32(angoli_img), np.float32(pts))
        x, y, h = pose
        dx, dy = _dir(h)
        rx, ry = _dx(h)
        angoli_img = [(0, 0), (LIN_W - 1, 0), (LIN_W - 1, LIN_H - 1), (0, LIN_H - 1)]
        pts = []
        for u, v in angoli_img:
            f, l = self._terreno_da_pixel(u, v)
            pts.append(((x + f * dx + l * rx) * PX, (y + f * dy + l * ry) * PX))
        return cv2.getPerspectiveTransform(np.float32(angoli_img), np.float32(pts))

    def immagine_linea(self, pose=None):
        pose = pose or (self.x, self.y, self.h)
        Hm = self._omografia_linea(pose)
        basso = self._basso and self.raster_sotto is not None          # [Sim V32] nel tunnel
        raster = self.raster_sotto if basso else self.raster
        img = cv2.warpPerspective(raster, Hm, (LIN_W, LIN_H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                  borderMode=cv2.BORDER_CONSTANT, borderValue=(120, 120, 120))
        if self.luce is not None:
            # [Sim V32] luci e ombre fisse del campo, ombra del robot, strisce LED, riflessi dei verdi lucidi
            luce = self.luce_sotto if basso else self.luce
            g = cv2.warpPerspective(luce, Hm, (LIN_W, LIN_H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                                    borderMode=cv2.BORDER_CONSTANT, borderValue=100).astype(np.float32) / 100.0
            g = self.real.guadagno_dinamico(pose, self._proietta_linea, LIN_W, LIN_H, g, basso)
            img = np.clip(img.astype(np.float32) * np.clip(g, 0.05, 2.0)[:, :, None], 0, 255).astype(np.uint8)
            dx, dy = _dir(pose[2])
            cam = (pose[0] + dx * self.cfg["cam_linea_avanti"], pose[1] + dy * self.cfg["cam_linea_avanti"],
                   self.z + self.cfg["cam_linea_altezza"])
            for v in self.C["verdi"]:
                r = self.real.riflesso_verdi(pose, cam, self._proietta_linea).get(v["id"]) if v.get("lucido") else None
                if r:
                    pts = [self._proietta_linea(px, py, pose) for px, py in
                           ((v["x"], v["y"]), (v["x"] + v["w"], v["y"]), (v["x"] + v["w"], v["y"] + v["h"]), (v["x"], v["y"] + v["h"]))]
                    if all(u > -5e3 for u, _ in pts):
                        m = np.zeros((LIN_H, LIN_W), np.uint8)
                        cv2.fillPoly(m, [np.array(pts, np.int32)], 255)
                        a = (m.astype(np.float32) / 255.0 * r)[:, :, None]
                        img = (img * (1 - a) + 250 * a).astype(np.uint8)
        # palline a terra
        Hi = np.linalg.inv(Hm)
        for b in self.palline:
            if b["stato"] == "libera":
                p = Hi @ np.array([b["x"] * PX, b["y"] * PX, 1.0])
                q = Hi @ np.array([(b["x"] + self.C["raggio_pallina"]) * PX, b["y"] * PX, 1.0])
                if p[2] > 0 and q[2] > 0:
                    u, v = p[0] / p[2], p[1] / p[2]
                    r = math.hypot(q[0] / q[2] - u, q[1] / q[2] - v)
                    if -30 < u < LIN_W + 30 and -30 < v < LIN_H + 30:
                        col = (30, 30, 30) if b["tipo"] == "nera" else (200, 200, 200)
                        cv2.circle(img, (int(u), int(v)), max(2, int(r)), col, -1)
        return np.dstack([img, np.full((LIN_H, LIN_W), 255, np.uint8)])

    def _proietta_linea(self, wx, wy, pose):
        Hi = np.linalg.inv(self._omografia_linea(pose))
        p = Hi @ np.array([wx * PX, wy * PX, 1.0])
        if p[2] <= 0:
            return -1e4, -1e4
        return p[0] / p[2], p[1] / p[2]

    def yolo_cross_linea(self, img224):
        """Cosa vedrebbe il modello Cross3 nella camera della linea."""
        pose = self.frame_pose
        trovati = []
        for el in self.C["elementi"]:
            pts = [self._proietta_linea(px, py, pose) for px, py in el["poli"]]
            us = [p[0] * 224 / LIN_W for p in pts]
            vs = [p[1] * 224 / LIN_H for p in pts]
            if el["tipo"] in ("In", "Ro"):
                # strisce lunghe (25 cm) che attraversano tutta l'immagine: un modello vero le
                # riconosce anche se escono dai lati, basta che si vedano tutte in profondità
                box = self._ritaglia(max(min(us), 0.0), min(vs), min(max(us), 223.0), max(vs), 0.6)
            else:
                box = self._ritaglia(min(us), min(vs), max(us), max(vs), 0.6)
            if box:
                trovati.append((el["tipo"], box))
        # --- quadratini verdi: validi solo se il robot li incontra PRIMA dell'incrocio ---
        h = pose[2]
        dx, dy = _dir(h)
        rx, ry = _dx(h)
        gruppi = {}
        for v in self.C["verdi"]:
            angoli = [(v["x"], v["y"]), (v["x"] + v["w"], v["y"]), (v["x"] + v["w"], v["y"] + v["h"]), (v["x"], v["y"] + v["h"])]
            pts = [self._proietta_linea(px, py, pose) for px, py in angoli]
            us = [p[0] * 224 / LIN_W for p in pts]
            vs = [p[1] * 224 / LIN_H for p in pts]
            box = self._ritaglia(min(us), min(vs), max(us), max(vs), 0.6)
            if not box:
                continue
            mx, my = v["x"] + v["w"] / 2, v["y"] + v["h"] / 2
            ix, iy = v["incrocio"]
            avanti = (mx - ix) * dx + (my - iy) * dy      # < 0: il verde è prima dell'incrocio
            lato = (mx - ix) * rx + (my - iy) * ry        # < 0: a sinistra, > 0: a destra
            if avanti >= 0 and not self.cfg["yolo_sbaglia_falsi_verdi"]:
                continue                                  # falso verde: un buon modello lo ignora
            if self.real.riflessi.get(v["id"], 0.0) > self.cfg.get("riflesso_soglia", 0.5):
                continue                                  # [Sim V32] verde lucido con il riflesso: YOLO non lo vede
            gruppi.setdefault(tuple(v["incrocio"]), []).append((lato, box))
        for lista in gruppi.values():
            sinistra = any(l < 0 for l, _ in lista)
            destra = any(l > 0 for l, _ in lista)
            tipo = "Fr" if sinistra and destra else ("Sx" if sinistra else "Dx")
            box = (min(b[0] for _, b in lista), min(b[1] for _, b in lista),
                   max(b[2] for _, b in lista), max(b[3] for _, b in lista))
            trovati.append((tipo, box))
        if self.cfg.get("yolo_argento_rampa"):             # [V28] falso argento all'inizio delle rampe
            if abs(self.pitch) > 8:
                if getattr(self, "_rampa_t0", None) is None:
                    self._rampa_t0 = self.t
                if self.t - self._rampa_t0 < 1.2:
                    # riquadro alto quasi tutta l'immagine, come nella scatola nera: così il controllo "oltre la
                    # striscia la linea continua" (LineaOltreStriscia) non si può fare
                    trovati.append(("In", (0.0, 12.0, 223.0, 210.0)))
            else:
                self._rampa_t0 = None
        if self.cfg.get("yolo_argento_falso") and 2.5 < self.t < 6.3:
            trovati.append(("In", (0.0, 120.0, 223.0, 150.0)))     # riflesso scambiato per la striscia argento
        priorita = ["Ro", "In", "Fr", "Sx", "Dx", "Di"]
        trovati.sort(key=lambda e: priorita.index(e[0]))
        hsv = cv2.cvtColor(img224[:, :, :3], cv2.COLOR_BGR2HSV)
        nero = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 150, 80]))
        ys, xs = np.nonzero(nero)
        if len(xs) > 250:
            trovati.append(("Ln", (float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max()))))
        else:
            trovati.append(("Bi", (0.0, 0.0, 223.0, 223.0)))
        self.yolo_vista = trovati[0][0]
        return [(CLASSI_CROSS[t], 0.9, b) for t, b in trovati]

    @staticmethod
    def _ritaglia(u0, v0, u1, v1, frazione_min, lato=224):
        if u1 <= u0 or v1 <= v0:
            return None
        cu0, cv0 = max(0.0, u0), max(0.0, v0)
        cu1, cv1 = min(lato - 1.0, u1), min(lato - 1.0, v1)
        if cu1 <= cu0 or cv1 <= cv0:
            return None
        if (cu1 - cu0) * (cv1 - cv0) < frazione_min * (u1 - u0) * (v1 - v0):
            return None
        return (cu0, cv0, cu1, cv1)

    # ------------------------------------------------------------------
    #  CAMERA DELL'ARENA (prospettiva semplificata)
    # ------------------------------------------------------------------
    def _proietta_arena(self, wx, wy, wz, pose):
        x, y, h = pose
        c = self.cfg
        dx, dy = _dir(h)
        rx, ry = _dx(h)
        cx, cy = x + dx * c["cam_arena_avanti"], y + dy * c["cam_arena_avanti"]
        relx, rely = wx - cx, wy - cy
        f = relx * dx + rely * dy
        l = relx * rx + rely * ry
        th = math.radians(c["cam_arena_inclinazione"])
        hc = c["cam_arena_altezza"]
        zc = f * math.cos(th) + (hc - wz) * math.sin(th)
        yc = -f * math.sin(th) + (hc - wz) * math.cos(th)
        if zc < 3:
            return None
        th2 = math.tan(math.radians(c["cam_arena_hfov"] / 2))
        fx = 112 / th2
        fy = 112 / (th2 * LIN_H / LIN_W)
        return 112 + fx * l / zc, 112 + fy * yc / zc, zc, fx, fy, math.hypot(relx, rely)

    def _box_punti(self, punti3d, pose, frazione=0.4, tutti=False):
        proj = [self._proietta_arena(px, py, pz, pose) for px, py, pz in punti3d]
        proj = [p for p in proj if p]
        if not proj or len(proj) < (len(punti3d) if tutti else len(punti3d) // 2):
            return None
        if min(p[5] for p in proj) > self.cfg["cam_arena_portata"]:
            return None
        us = [p[0] for p in proj]
        vs = [p[1] for p in proj]
        return self._ritaglia(min(us), min(vs), max(us), max(vs), frazione)

    def oggetti_arena(self, quali):
        """Elenco (classe, conf, box) di ciò che YOLO vedrebbe nella camera dell'arena."""
        pose = self.arena_pose
        out = []
        if quali == "palline":
            r = self.C["raggio_pallina"]
            for b in self.palline:
                if b["stato"] != "libera":
                    continue
                p = self._proietta_arena(b["x"], b["y"], r, pose)
                if not p or p[5] > self.cfg["cam_arena_portata"]:
                    continue
                u, v, zc, fx, fy, _ = p
                box = self._ritaglia(u - fx * r / zc, v - fy * r / zc, u + fx * r / zc, v + fy * r / zc, 0.5)
                if box:
                    out.append((0 if b["tipo"] == "argento" else 1, 0.88, box))
        elif quali == "triangoli":
            for tr in self.C["triangoli"]:
                pts = [(a, b, z) for a, b in tr["poli"] for z in (0, 6)]
                box = self._box_punti(pts, pose)
                if box:
                    out.append((tr["classe"], 0.86, box))
            for cls, box in self._aperture(pose):
                if cls == 1 and (self.cfg.get("yolo_porta_confonde") or self.cfg.get("yolo_porta_solo_ingresso")):
                    cls = 0     # il modello dei triangoli prende anche l'INGRESSO per una porta d'uscita
                if self.cfg.get("yolo_porta_nessuna"):
                    continue    # il modello non vede nessuna porta
                elif cls == 0 and self.cfg.get("yolo_porta_solo_ingresso"):
                    continue    # ...e l'uscita vera non la vede proprio (caso peggiore, video dell'8/10)
                out.append((cls, 0.84, box))
        elif quali == "uscita":
            for cls, box in self._aperture(pose):
                out.append((cls, 0.84, box))
        elif quali == "cross":
            s = self.C["argento"]
            pts = [(s["x"], s["y"], 0), (s["x"] + s["w"], s["y"], 0), (s["x"], s["y"] + s["h"], 0), (s["x"] + s["w"], s["y"] + s["h"], 0)]
            box = self._box_punti(pts, pose, 0.6)
            out.append((CLASSI_CROSS["In"], 0.9, box) if box else (CLASSI_CROSS["Bi"], 0.9, (0, 0, 223, 223)))
        return out

    def _aperture(self, pose):
        A = self.C["arena"]
        x0, x1 = A["uscita"]
        y0, y1 = A["ingresso"]
        out = []
        yb, xa = A["y"] + A["h"], A["x"]
        if A.get("uscita_muro") == "sinistro":
            if self.x > xa + 2:     # uscita sullo stesso muro dell'ingresso (x0..x1 sono quote y)
                box = self._box_punti([(xa, x0, 0), (xa, x1, 0), (xa, x0, self.cfg["altezza_muri"]), (xa, x1, self.cfg["altezza_muri"])], pose, 0.2, tutti=True)
                if box:
                    out.append((0, box))
        elif self.y < yb - 2:     # porta d'uscita vista da dentro
            box = self._box_punti([(x0, yb, 0), (x1, yb, 0), (x0, yb, self.cfg["altezza_muri"]), (x1, yb, self.cfg["altezza_muri"])], pose, 0.2, tutti=True)
            if box:
                out.append((0, box))
        box = self._box_punti([(xa, y0, 0), (xa, y1, 0), (xa, y0, self.cfg["altezza_muri"]), (xa, y1, self.cfg["altezza_muri"])], pose, 0.2, tutti=True)
        if box:
            out.append((1, box))
        return out

    def immagine_arena(self):
        """Disegno schematico di ciò che vede la camera dell'arena (solo per il replay)."""
        img = np.full((224, 224, 3), 240, np.uint8)
        pose = self.arena_pose
        for cls, conf, box in self.oggetti_arena("triangoli"):
            col = {3: (60, 160, 60), 2: (50, 50, 200), 0: (40, 40, 40), 1: (190, 190, 190)}[cls]
            cv2.rectangle(img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), col, -1)
        for cls, conf, box in self.oggetti_arena("palline"):
            col = (200, 200, 200) if cls == 0 else (20, 20, 20)
            c = (int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2))
            cv2.circle(img, c, max(2, int((box[2] - box[0]) / 2)), col, -1)
        out = cv2.resize(img, (LIN_W, LIN_H))
        return np.dstack([out, np.full((LIN_H, LIN_W), 255, np.uint8)])

    # ------------------------------------------------------------------
    #  TEMPO VIRTUALE
    # ------------------------------------------------------------------
    def avanza(self, durata):
        if self.fine_lanciata:
            return
        fine = self.t + max(0.0, durata)
        DT = 0.005
        while self.t < fine - 1e-9:
            h = min(DT, fine - self.t)
            self.passo(h)
            self.t += h
            if self.t >= self.prossimo_tof:
                self.tof_val = self.leggi_tof()
                self.prossimo_tof += self.cfg["tof_periodo"]
                self.tof_robot = self._guasti_laser(self.tof_val)     # [V29] quello che legge il robot
            self.aggiorna_sensori_robot()
            if self.t >= self.prossimo_frame:
                self.prossimo_frame += 1.0 / self.cfg["cam_linea_fps"]
                if self.globali is not None:
                    self.frame_pose = (self.x, self.y, self.h)
                    self.frame_att = (self.z, self.pitch, self.roll)
                    self.globali["Immagine"] = self.immagine_linea(self.frame_pose)
            if self.t >= self.prossima_reg:
                self.prossima_reg += 0.05
                self.registra()
            if self.t > 2.0 and not self.avviato and not self.fine:
                self.avviato = True
                self.switch_avvio = True
                self.evento("avvio", "Switch di avvio acceso: parte la gara")
            self._controlla_traguardi()
            if self.fine:
                self.fine_lanciata = True
                self.registra()
                raise FineSimulazione(self.fine)

    # ------------------------------------------------------------------
    #  TRAGUARDI E FINE
    # ------------------------------------------------------------------
    def _traguardo(self, chiave, tipo, testo):
        if chiave not in self.traguardi:
            self.traguardi.add(chiave)
            self.evento(tipo, testo)

    def _controlla_traguardi(self):
        if self.nuovo:
            self._controlla_percorso()
            return
        x, y = self.x, self.y
        # traguardi del percorso, descritti in campo.py
        for tg in self.C.get("traguardi", []):
            if tg["chiave"] in self.traguardi:
                continue
            x0, y0, x1, y1 = tg["rett"]
            if not (x0 < x < x1 and y0 < y < y1):
                continue
            if any(r not in self.traguardi for r in tg.get("richiede", [])):
                continue
            if any(e in self.traguardi for e in tg.get("esclude", [])):
                continue
            if "heading" in tg and not (tg["heading"][0] <= self.h <= tg["heading"][1]):
                continue
            self._traguardo(tg["chiave"], tg["tipo"], tg["testo"])
        A = self.C["arena"]
        o = self.C["ostacolo"]
        yl = self.C.get("linea_arena_y", 40)
        if self.tof_val[1] < 20 and o["x"] - 40 < x < o["x"] and o["y"] - 10 < y < o["y"] + o["h"] + 10:
            self._traguardo("ostacolo_visto", "info", "Ostacolo rilevato davanti")
        if o["x"] + o["w"] + 8 < x < A["x"] and yl - 12 < y < yl + 12 and "ostacolo_visto" in self.traguardi:
            self._traguardo("ostacolo", "ok", "Ostacolo aggirato, robot di nuovo sulla linea")
        if A["x"] + 3 < x < A["x"] + A["w"] and A["y"] < y < A["y"] + A["h"] - 3:
            self.in_arena_visto = True
            self._traguardo("arena", "ok", "Entrato nell'arena")
        if A.get("uscita_muro") == "sinistro":
            if self.in_arena_visto and x < A["x"] - 6 and A["uscita"][0] - 5 < y < A["uscita"][1] + 5:
                self._traguardo("uscita", "ok", "Uscito dall'arena dalla porta giusta")
            if self.in_arena_visto and x < A["x"] - 6 and A["ingresso"][0] - 5 < y < A["ingresso"][1] + 5 \
                    and "uscita" not in self.traguardi:
                self._traguardo("uscita_ingresso", "errore", "Uscito dall'arena dall'INGRESSO")
        else:
            if self.in_arena_visto and y > A["y"] + A["h"] + 6 and A["uscita"][0] - 5 < x < A["uscita"][1] + 5:
                self._traguardo("uscita", "ok", "Uscito dall'arena dalla porta giusta")
            if self.in_arena_visto and x < A["x"] - 3 and y < A["y"] + A["h"]:
                self._traguardo("uscita_ingresso", "errore", "Uscito dall'arena dall'INGRESSO")
        # fine: arrivo sulla linea rossa
        r = self.C["rosso"]
        vicino = abs(x - (r["x"] + r["w"] / 2)) < 15 and abs(y - (r["y"] + 1)) < 22
        fermo = max(abs(v) for v in self.ruote.values()) < 0.02
        if vicino and fermo and "uscita" in self.traguardi:
            self.fermo_su_rosso += 0.005
            if self.fermo_su_rosso > 15.0:     # 15 s: lascia il tempo per l'eventuale festeggiamento
                self._traguardo("arrivo", "ok", "ARRIVO: fermo sulla linea rossa")
                self.fine = "arrivo"
        else:
            self.fermo_su_rosso = 0.0
        if not (-15 < x < self.C["larghezza"] + 15 and -15 < y < self.C["altezza"] + 15):
            self.evento("errore", "Il robot è uscito dal campo")
            self.fine = "fuori campo"
        if math.hypot(x - self.ultimo_movimento[1], y - self.ultimo_movimento[2]) > 3:
            self.ultimo_movimento = (self.t, x, y)
        elif self.t - self.ultimo_movimento[0] > 60 and self.switch_avvio:
            self.evento("errore", "Robot fermo da 60 secondi: gara interrotta")
            self.fine = "bloccato"
        if self.t > self.tempo_max:
            self.evento("info", f"Tempo massimo di {int(self.tempo_max)} s raggiunto")
            self.fine = "tempo scaduto"

    # ------------------------------------------------------------------
    #  REGISTRAZIONE PER IL REPLAY
    # ------------------------------------------------------------------
    def evento(self, tipo, testo):
        self.eventi.append({"t": round(self.t, 2), "tipo": tipo, "testo": testo})

    def scrivi_log(self, testo):
        if "PAUSA" in testo:
            self._visto_pausa = self.t
        if len(self.log) < 30000:
            self.log.append([round(self.t, 2), testo[:160]])

    def _stato_attuale(self):
        nomi = []
        f = sys._getframe(2)
        while f is not None:
            fn = f.f_code.co_filename
            if fn.endswith(("RwdFoto.py", "ViennaClsRobot.py")) and f.f_code.co_name not in ("<module>", "_set_pwm", "_set_motor", "Sterzo", "GetSensori", "GetGyro", "Distanze", "stop_motors", "stop_tick_from_range", "Stop"):
                nomi.append(f.f_code.co_name)
            f = f.f_back
        s = " › ".join(reversed(nomi)) or "attesa"
        if s not in self._idx_stati:
            self._idx_stati[s] = len(self.stati)
            self.stati.append(s)
        return self._idx_stati[s]

    def registra(self):
        def cmd(ch):
            return round(self._frazione_servo(self.pwm.get((0x41, ch), 0)), 2)
        b = [(p["id"], round(p["x"], 1), round(p["y"], 1), p["stato"]) for p in self.palline]
        self.campioni.append([
            round(self.t, 2), round(self.x, 2), round(self.y, 2), round(self.h, 1),
            cmd(15), cmd(4), cmd(0), cmd(11),
            self.tof_val[0], self.tof_val[1], self.tof_val[2],
            round(self.pitch, 1), int(self.braccio), int(self.pinza),
            1 if self.tenuta else 0, 1 if self.led[22] else 0, 1 if self.led[23] else 0,
            self._stato_attuale(), self.yolo_vista,
            "|".join(f"{i},{x},{y},{s}" for i, x, y, s in b),
        ] + ([round(self.roll, 1), round(self.z, 1),
              [round(v, 1) for p in self._impronta_linea((self.x, self.y, self.h), (self.z, self.pitch, self.roll)) for v in p],
              [round(a["a"], 1) for a in self._alt.values()], round(self.punti_parziali(), 1)] if self.nuovo else []))

    # ==================================================================
    #  [V22] CAMPO A PIASTRELLE: QUOTE, RAMPE, ALTALENA, DOSSI, DETRITI
    # ==================================================================
    def _init_rcj(self):
        C = self.C
        self._alt = {}
        for a in C.get("altalene", []):
            self._alt[tuple(a["cella"])] = {"cella": tuple(a["cella"]), "asse": a["asse"], "A": a["angolo"], "a": -a["angolo"]}
        self._su_dosso = [False, False]
        self._detrito_t = {}
        self._centri_detriti = [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in C.get("detriti", [])]
        self._visto_pausa = -1.0
        P = C["percorso"]
        self.k = 0                          # ultima piastrella del percorso raggiunta (in ordine)
        self.ka = next((i for i, p in enumerate(P) if p["tipo"] == "arena"), None)
        self.ultima = len(P) - 1
        self.cp_corrente = 0
        self.tentativi = {}
        self.punti_cp = 0
        self.punti_ost = 0
        self.ost_fatti = set()
        self.lop = 0
        self.lop_zona = 0
        self.salvataggi = []
        self.uscita_zona = False
        self.arrivato = False
        self.lop_fase = None
        self.perso_da = None
        self.cella_prec = None
        self.t_progresso = 0.0
        self.t_zona = None
        self.fermo_su_arrivo = 0.0
        self.dettaglio = []                 # righe del punteggio

    def quota(self, x, y):
        """Altezza del pavimento (cm) e pendenze dz/dx, dz/dy nel punto (x, y)."""
        c = (int(math.floor(x / 30)), int(math.floor(y / 30)))
        q = self.C["quote"].get(c)
        if q is None:
            return 0.0, 0.0, 0.0
        if c in self._sotto and self.z < self._sotto[c]["tetto"] - 6:
            q = self._sotto[c]                    # [Sim V32] il robot è in basso: per lui conta il pavimento del tunnel
        if q["tipo"] == "altalena":
            st = self._alt[c]
            ax, ay = st["asse"]
            s = (x - q["cx"]) * ax + (y - q["cy"]) * ay
            ta = math.tan(math.radians(st["a"]))
            return q["z"] - s * ta, -ta * ax, -ta * ay
        return q["z"] + q["sx"] * (x - q["cx"]) + q["sy"] * (y - q["cy"]), q["sx"], q["sy"]

    def _aggiorna_altalene(self, dt):
        for c, st in self._alt.items():
            q = self.C["quote"][c]
            dentro = int(self.x // 30) == c[0] and int(self.y // 30) == c[1]
            obiettivo = st["a"]
            if dentro:
                s = (self.x - q["cx"]) * st["asse"][0] + (self.y - q["cy"]) * st["asse"][1]
                if s > 1.5:
                    obiettivo = st["A"]
                elif s < -1.5:
                    obiettivo = -st["A"]
            passo = self.cfg["altalena_vel"] * dt
            prima = st["a"]
            st["a"] += max(-passo, min(passo, obiettivo - st["a"]))
            if prima < st["A"] - 0.01 <= st["a"]:
                self.evento("info", "Altalena: ha basculato in avanti")

    def _dossi_e_detriti(self):
        fatt, extra = 1.0, 0.0
        dx, dy = _dir(self.h)
        rx, ry = _dx(self.h)
        for i, f in enumerate((6.5, -6.5)):
            px, py = self.x + dx * f, self.y + dy * f
            su = any(x0 <= px <= x1 and y0 <= py <= y1 for x0, y0, x1, y1 in self._dossi_attivi)
            if su != self._su_dosso[i]:
                self._su_dosso[i] = su
                self.h = (self.h + random.gauss(0, 1.5)) % 360        # il dosso dà una piccola sterzata
            if su:
                fatt *= 0.65
                extra += 6.0 if i == 0 else -6.0
            for j, (cx, cy) in enumerate(self._centri_detriti):
                if abs(cx - self.x) > 20 or abs(cy - self.y) > 20:
                    continue
                if self.t - self._detrito_t.get((i, j), -9) < 1.0:
                    continue
                a, b = self.C["detriti"][j]
                for l in (-7.0, 7.0):
                    if _dist_punto_segmento(px + rx * l, py + ry * l, a, b) < 0.8:
                        self._detrito_t[(i, j)] = self.t
                        self.h = (self.h + random.gauss(0, 1.2)) % 360
                        fatt *= 0.8
                        break
        return fatt, extra

    def _aggiorna_livello(self):
        """[Sim V32] Sopra il ponte o sotto (nel tunnel): cambia quali pareti e quali tubi contano."""
        basso = bool(self._sotto) and self.z < min(s["tetto"] for s in self._sotto.values()) - 6
        if basso != self._basso or self._solidi is self._solidi_base and basso:
            self._basso = basso
            self._solidi = self._solidi_base + (self._pareti_tunnel if basso else [])
            self._dossi_attivi = self._dossi_bassi if basso else self._dossi_alti

    def _muovi_3d(self, dt, v, w):
        c = self.cfg
        if self.sollevato:
            return
        if self._sotto:
            self._aggiorna_livello()
        self._aggiorna_altalene(dt)
        z, sx, sy = self.quota(self.x, self.y)
        dx, dy = _dir(self.h)
        rx, ry = _dx(self.h)
        # assetto dalle 4 ruote: all'inizio di una rampa salgono prima le ruote davanti (il robot
        # si inclina gradualmente, come quello vero), sul bordo dell'altalena idem
        zf = self.quota(self.x + dx * 6.5, self.y + dy * 6.5)[0]
        zb = self.quota(self.x - dx * 6.5, self.y - dy * 6.5)[0]
        zs = self.quota(self.x - rx * 7.5, self.y - ry * 7.5)[0]
        zd = self.quota(self.x + rx * 7.5, self.y + ry * 7.5)[0]
        if abs(zf - zb) > 6 or abs(zs - zd) > 6:      # bordo rialzato sotto una ruota: conta il centro
            zf, zb = z + (sx * dx + sy * dy) * 6.5, z - (sx * dx + sy * dy) * 6.5
            zs, zd = z - (sx * rx + sy * ry) * 7.5, z + (sx * rx + sy * ry) * 7.5
        self.z = (zf + zb) / 2
        pend = math.atan2(zf - zb, 13.0)
        ban = math.atan2(zd - zs, 15.0)
        fatt, extra = self._dossi_e_detriti()
        self.pitch = math.degrees(pend) + extra
        self.roll = math.degrees(ban)
        fermo = abs(v) < 1.0 and abs(w) < 5
        vs = v * fatt
        if vs:
            vs *= 1 - 0.6 * math.sin(pend) * (1 if vs > 0 else -1)
        if fermo:
            vs -= c["scivolo_pendenza"] * math.sin(pend)
        vlat = -(c["scivolo_fermo"] if fermo else c["scivolo_laterale"]) * math.sin(ban)
        nh = (self.h + w * dt) % 360
        if not self._collide(self.x, self.y, nh) or self._collide(self.x, self.y, self.h):
            self.h = nh
        elif c.get("scivola_sui_muri"):
            # [Sim V32] il robot vero, girando con il fianco contro una parete, scivola un po' di lato (max 10 cm/s)
            for k in (0.05, -0.05):
                px, py = self.x + rx * k, self.y + ry * k
                if not self._collide(px, py, nh):
                    self.x, self.y, self.h = px, py, nh
                    break
        dx, dy = _dir(self.h)
        vo = vs * math.cos(pend)
        nx = self.x + (vo * dx + vlat * rx) * dt
        ny = self.y + (vo * dy + vlat * ry) * dt
        zn = self.quota(nx, ny)[0]
        if self._collide(nx, ny) and not self._collide(self.x, self.y):
            if self.t - self._ultimo_urto > 1.0:
                self.urti += 1
                self.evento("urto", "Urto contro muro/ostacolo")
            self._ultimo_urto = self.t
        elif zn - z > c["gradino_max"]:
            if self.t - self._ultimo_urto > 1.0:
                self.urti += 1
                self.evento("urto", "Gradino troppo alto: le ruote non salgono")
            self._ultimo_urto = self.t
        else:
            self.x, self.y = nx, ny
            if z - zn > c["caduta_min"]:
                self.z = zn
                self.evento("errore", f"CADUTO da un bordo rialzato ({z - zn:.0f} cm)")
                self._richiedi_lop("caduto da un bordo rialzato")

    def _raggio_3d(self, ox, oy, ddx, ddy, hl, elev, limite):
        z0 = self.z + hl
        te = math.tan(math.radians(elev))
        t = 1.0
        while t <= limite:
            if self.quota(ox + ddx * t, oy + ddy * t)[0] >= z0 + te * t:
                return t
            t += 1.0
        return None

    # ==================================================================
    #  [V22] PUNTEGGIO UFFICIALE E MANCANZA DI PROGRESSO (LoP)
    # ==================================================================
    def _salvataggio(self, b, giusto):
        if not giusto:
            return
        vive_prima = sum(1 for s in self.salvataggi if s["tipo"] == "argento")
        valido = b["tipo"] == "argento" or vive_prima >= 2
        self.salvataggi.append({"tipo": b["tipo"], "t": round(self.t, 1), "valido": valido})
        if b["tipo"] == "argento":
            self.evento("punti", f"Vittima viva salvata: moltiplicatore ×1,4")
        elif valido:
            self.evento("punti", f"Vittima morta salvata dopo le due vive: moltiplicatore ×1,4")
        else:
            self.evento("errore", "Vittima morta salvata PRIMA delle due vive: nessun moltiplicatore")
        self.t_zona = self.t

    def _moltiplicatore(self):
        m = 1.0
        for s in self.salvataggi:
            if s["valido"]:
                m *= max(1.25, 1.4 - 0.05 * self.lop_zona)
        return m

    def punti_parziali(self):
        linea = self.punti_cp + self.punti_ost
        bonus = max(0, 60 - 5 * self.lop) if self.arrivato else 0
        return (linea + bonus) * self._moltiplicatore()

    def punteggio(self):
        linea = self.punti_cp + self.punti_ost
        m = self._moltiplicatore()
        b26 = max(0, 60 - 5 * self.lop) if self.arrivato else 0
        b27 = max(10, 60 - 5 * self.lop) if self.arrivato else 0
        P = self.C["percorso"]
        n_tiles = sum(1 for p in P[1:] if p["tipo"] != "arena")
        ost_max = sum(p["punti"] for p in P)
        return {
            "checkpoint": self.punti_cp, "ostacoli": self.punti_ost, "linea": linea,
            "lop": self.lop, "lop_zona": self.lop_zona,
            "salvataggi": self.salvataggi, "moltiplicatore": round(m, 3),
            "uscita_zona": self.uscita_zona, "arrivato": self.arrivato,
            "bonus_2026": b26, "totale_2026": round((linea + b26) * m, 1),
            "bonus_2027": b27, "totale_2027": round((linea + 30 * self.uscita_zona + b27) * m, 1),
            "massimo_2026": round((5 * n_tiles + ost_max + 60) * 1.4 ** 3, 1),
            "massimo_2027": round((5 * n_tiles + ost_max + 30 + 60) * 1.4 ** 3, 1),
            "piastrelle": n_tiles, "ostacoli_max": ost_max, "dettaglio": self.dettaglio,
        }

    def _punti(self, n, testo):
        self.dettaglio.append([round(self.t, 1), n, testo])
        self.evento("punti", f"+{n} punti · {testo}")

    def _raggiunta(self, i):
        P = self.C["percorso"]
        j = i - 1
        while j >= 0 and P[j]["tipo"] == "arena":
            j -= 1
        if j >= 0 and P[j]["punti"] and j not in self.ost_fatti:
            self.ost_fatti.add(j)
            self.punti_ost += P[j]["punti"]
            self._punti(P[j]["punti"], P[j]["nome"])
        if P[i]["cp"] or i == self.ultima:
            n = sum(1 for p in P[self.cp_corrente + 1:i + 1] if p["tipo"] != "arena")
            a = self.tentativi.get(self.cp_corrente, 1)
            pt = [5, 3, 1][a - 1] if a <= 3 else 0
            self.punti_cp += n * pt
            dove = "arrivo" if i == self.ultima else f"checkpoint (piastrella {i})"
            self._punti(n * pt, f"{dove}: {n} piastrelle × {pt} ({a}° tentativo)")
            self.cp_corrente = i

    def _richiedi_lop(self, motivo):
        if self.lop_fase or self.fine or self.arrivato:
            return
        P = self.C["percorso"]
        self.lop += 1
        in_zona = self.ka is not None and self.k == self.ka
        if in_zona:
            self.lop_zona += 1
        a = self.tentativi.get(self.cp_corrente, 1) + 1
        self.tentativi[self.cp_corrente] = a
        cp = self.cp_corrente
        if a > 3:
            succ = [i for i, p in enumerate(P) if p["cp"] and i > cp]
            if succ:
                cp = succ[0]
                self.cp_corrente = cp
                self.evento("info", f"Tre tentativi falliti: il capitano porta il robot al checkpoint successivo (piastrella {cp})")
        self.evento("lop", f"LoP n. {self.lop}{' nella zona' if in_zona else ''}: {motivo}. Si riparte dalla piastrella {cp}")
        if self.tenuta is not None:
            b = self.tenuta
            self.tenuta = None
            A = self.C["arena"]
            if in_zona:
                b["x"] = min(max(self.x, A["x"] + 8), A["x"] + A["w"] - 8)
                b["y"] = min(max(self.y, A["y"] + 8), A["y"] + A["h"] - 8)
            else:
                b["x"], b["y"] = A["x"] + random.uniform(20, 70), A["y"] + random.uniform(20, 70)
            b["stato"] = "libera"
        self.switch_avvio = False
        self.sollevato = True
        self.lop_fase = ("pausa", self.t, cp)

    def _controlla_percorso(self):
        P = self.C["percorso"]
        x, y = self.x, self.y
        if self.t > self.tempo_max:
            self.evento("info", f"Fine degli 8 minuti ({int(self.tempo_max)} s)")
            self.fine = "tempo scaduto"
            return
        if self.lop_fase:
            fase, t0, cp = self.lop_fase
            if fase == "pausa" and (self._visto_pausa > t0 or self.t - t0 > 8.0):
                p = P[cp]
                dx, dy = _dir(p["h"])
                self.x = p["cella"][0] * 30 + 15 - dx * 4
                self.y = p["cella"][1] * 30 + 15 - dy * 4
                self.h = float(p["h"])
                self.z = 0.0 if p.get("sotto") else 999.0          # [Sim V32] si riparte al livello giusto
                self.z = self.quota(self.x, self.y)[0]
                if self._sotto:
                    self._aggiorna_livello()
                for st in self._alt.values():
                    st["a"] = -st["A"]
                self.k = cp
                self.perso_da = None
                self.cella_prec = None
                self.lop_fase = ("riparti", self.t, cp)
            elif fase == "riparti" and self.t - t0 > 3.0:
                self.sollevato = False
                self.switch_avvio = True
                self.t_progresso = self.t
                self.t_zona = self.t if self.k == self.ka else None
                self.lop_fase = None
                self.evento("avvio", "Il capitano riaccende lo switch")
            return
        if not self.switch_avvio:
            return
        if not (-5 < x < self.C["larghezza"] + 5 and -5 < y < self.C["altezza"] + 5):
            self.evento("errore", "Il robot è uscito dal campo")
            self._richiedi_lop("uscito dal campo")
            return
        A = self.C.get("arena")
        cella = (int(x // 30), int(y // 30))
        # ---------------- zona di evacuazione ----------------
        if self.ka is not None:
            dentro = A["x"] + 2 < x < A["x"] + A["w"] and A["y"] < y < A["y"] + A["h"]
            if dentro and self.k < self.ka and self.k >= self.ka - 2:
                for i in range(self.k + 1, self.ka):
                    self._raggiunta(i)
                self.k = self.ka
                self.t_zona = self.t
                self.perso_da = None
                self.evento("ok", "Entrato nella zona di evacuazione")
                return
            if self.k == self.ka:
                x0, x1 = A["uscita"]
                yb = A["y"] + A["h"]
                sx = A.get("uscita_muro") == "sinistro"     # [V26] uscita sullo stesso muro dell'ingresso
                fuori_giusto = (x < A["x"] - 12 and x0 - 4 < y < x1 + 4) if sx else (y > yb + 12 and x0 - 4 < x < x1 + 4)
                if fuori_giusto:
                    self.uscita_zona = True
                    self.evento("ok", "Uscito dalla zona dalla porta giusta")
                    self.evento("punti", "+30 punti · uscita dalla zona (solo bozza regole 2027)")
                    self.k = self.ka + 1
                    self._raggiunta(self.k)
                    self.t_progresso = self.t
                    self.cella_prec = cella
                    self.perso_da = None
                    return
                if x < A["x"] - 8 and (not sx or A["ingresso"][0] - 4 < y < A["ingresso"][1] + 4):
                    self._richiedi_lop("uscito dalla zona dall'INGRESSO")
                    return
                if sx and x < A["x"] - 12:
                    self._richiedi_lop("uscito dalla zona da un punto sbagliato")
                    return
                if not dentro and (y > yb + 12 or x > A["x"] + A["w"] + 5 or y < A["y"] - 5):
                    self._richiedi_lop("uscito dalla zona da un punto sbagliato")
                    return
                if self.t - (self.t_zona or self.t) > 150:
                    self._richiedi_lop("150 s nella zona senza salvare vittime né uscire")
                return
        # ---------------- linea ----------------
        if self.k == self.ultima:
            fermo = max(abs(v) for v in self.ruote.values()) < 0.02
            if cella == P[self.ultima]["cella"] and fermo:
                self.fermo_su_arrivo += 0.005
                if self.fermo_su_arrivo > 5.0 and not self.arrivato:
                    self.arrivato = True
                    b = max(0, 60 - 5 * self.lop)
                    self.evento("ok", "ARRIVO: fermo sulla piastrella d'arrivo per 5 s")
                    self.evento("punti", f"Bonus d'uscita: 60 − 5 × {self.lop} LoP = {b} punti (2026)")
                    self.fine = "arrivo"
            else:
                self.fermo_su_arrivo = 0.0
        if cella != self.cella_prec:
            self.cella_prec = cella
            trovata = None
            for j in range(self.k + 1, min(self.k + 4, len(P))):
                if P[j]["tipo"] == "arena":
                    break
                if P[j]["cella"] == cella and bool(P[j].get("sotto")) == (self._basso and cella in self._sotto):
                    trovata = j                   # [Sim V32] stessa cella, ma ponte e tunnel sono due piastrelle
                    break
            if trovata is not None:
                for i in range(self.k + 1, trovata + 1):
                    self._raggiunta(i)
                self.k = trovata
                self.t_progresso = self.t
                self.perso_da = None
            elif cella == P[self.k]["cella"] or (self.k > 0 and cella == P[self.k - 1]["cella"]):
                self.perso_da = None
            else:
                tipo = self.C["celle_linea"].get(cella)
                vicino = max(abs(cella[0] - P[self.k]["cella"][0]), abs(cella[1] - P[self.k]["cella"][1])) <= 1
                # [V24] mentre gira intorno all'ostacolo il robot può passare sopra le piastrelle vicine anche se
                # hanno una linea: non è "una linea fuori sequenza" finché non la segue fuori da quella zona
                giro_ostacolo = abs(self.C["tolleranza"].get(cella, -99) - self.k) <= 2
                if tipo in ("percorso", "ramo") and not giro_ostacolo:
                    self._richiedi_lop("ha preso una linea fuori sequenza")
                    return
                if not vicino and cella not in self.C["tolleranza"]:
                    self._richiedi_lop("ha perso la linea")
                    return
                if self.perso_da is None:
                    self.perso_da = self.t
        if self.perso_da is not None:
            limite = 20.0 if cella in self.C["tolleranza"] else 6.0
            if self.t - self.perso_da > limite:
                self._richiedi_lop("ha perso la linea")
                return
        if self.t - self.t_progresso > self.cfg["lop_fermo_s"]:
            self._richiedi_lop(f"fermo da {self.cfg['lop_fermo_s']:.0f} s: il capitano chiama la LoP")
