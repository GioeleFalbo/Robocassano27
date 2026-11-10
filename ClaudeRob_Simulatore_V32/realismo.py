"""
[Sim V32] REALISMO: luci, ombre, LED del robot, verdi di tonalità diverse (lucidi o opachi), cono del laser.

Tutto è SPENTO di default: le piste vecchie (gara, rcj2026, lunga, contorto, scuola V31...) danno gli stessi
risultati del simulatore V31. Si accende dal cfg dello scenario (vedi campo.SCENARI["scuola_nuova"]) o a mano:

  "luci": [{"azimut": 200, "elevazione": 60, "forza": 0.30}, ...]
        azimut = da dove arriva la luce (0 = dall'alto della mappa, 90 = da destra, gradi in senso orario),
        elevazione = quanto è alta (90 = sopra la testa), forza = parte della luce che fa ombra (il resto è luce
        diffusa che arriva da tutte le parti). Ogni luce fa le sue ombre (muri, ponte, ostacoli, il robot stesso).
  "luce_gradiente": 0.15     la pista è più chiara dalla parte della finestra (della prima luce)
  "tunnel_buio": 0.35        quanta luce arriva in fondo al tunnel (1 = come fuori)
  "led_forza": 0.45          quanto illuminano le strisce LED del robot (relè GPIO 22/23) davanti al robot
  "verdi_vari": True         ogni quadratino verde ha la sua tonalità (nastri diversi) e può essere lucido
  "verdi_lucidi": 0.4        frazione dei verdi lucidi; un verde lucido sotto una luce può fare un RIFLESSO
                             bianco: se copre più di "riflesso_soglia" del quadratino, YOLO non lo vede
  "tof_cono": 27             apertura del cono del VL53L1X in gradi (0 = raggio sottile, come la V31)
  "tof_rumore_cono": [0.5, 1.6]   rumore = a + b * (d/100)^2 cm: a 1 m circa 2 cm (misurato il 9/11)

I fatti misurati sono nell'issue #17 e in CLAUDE.md; le tonalità dei verdi sono stime dalle foto del 10/11.
"""
import math
import random

import cv2
import numpy as np

# tonalità dei nastri verdi (BGR), stimate dalle foto della pista: scuro, medio, chiaro, verde-azzurro, oliva
TONI_VERDI = [(40, 170, 40), (45, 120, 35), (70, 175, 80), (95, 150, 40), (40, 140, 90)]


def _dir(h):
    r = math.radians(h)
    return math.sin(r), -math.cos(r)


def _dx(h):
    r = math.radians(h)
    return math.cos(r), math.sin(r)


def _vettore_ombra(luce, altezza):
    """Spostamento (cm) dell'ombra di un punto alto 'altezza': dalla parte opposta alla luce."""
    lx, ly = _dir(luce["azimut"])              # direzione VERSO la luce
    L = altezza / math.tan(math.radians(max(5.0, luce["elevazione"])))
    return -lx * L, -ly * L


class Realismo:
    def __init__(self, mondo):
        self.M = mondo
        c = mondo.cfg
        self.luci = list(c.get("luci") or [])
        self.attivo_luci = bool(self.luci)
        self.cono = float(c.get("tof_cono", 0) or 0)
        self.led_forza = float(c.get("led_forza", 0.45))
        self.riflessi = {}                      # id del verde -> quanto è coperto dal riflesso (0..1)
        rng = random.Random(int(c.get("seme_realismo", 7)))
        C = mondo.C
        if c.get("verdi_vari"):
            for v in C["verdi"]:
                v["tono"] = rng.choice(TONI_VERDI)
                v["lucido"] = rng.random() < float(c.get("verdi_lucidi", 0.4))

    # ------------------------------------------------------------------
    #  LUCI E OMBRE FISSE (si calcolano una volta: il campo non si muove)
    # ------------------------------------------------------------------
    def mappa_luce(self, PX, sotto=False):
        """Guadagno della luce su tutto il campo (float32, 1 = luce piena). sotto=True: il livello del tunnel."""
        M, C = self.M, self.M.C
        W, H = int(C["larghezza"] * PX), int(C["altezza"] * PX)
        forza_tot = sum(l["forza"] for l in self.luci)
        g = np.full((H, W), 1.0 - forza_tot, np.float32)
        alti = self._celle_alte()
        for luce in self.luci:
            ombra = np.zeros((H, W), np.uint8)
            for (a, b), h in self._oggetti_alti():
                ox, oy = _vettore_ombra(luce, h)
                poli = np.array([[a[0], a[1]], [b[0], b[1]], [b[0] + ox, b[1] + oy], [a[0] + ox, a[1] + oy]]) * PX
                cv2.fillPoly(ombra, [poli.astype(np.int32)], 255)
            for (x0, y0, x1, y1), h in self._ripiani():
                ox, oy = _vettore_ombra(luce, h)
                poli = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], np.float64)
                tutto = np.vstack([poli, poli + [ox, oy]]) * PX
                cv2.fillPoly(ombra, [cv2.convexHull(tutto.astype(np.int32))], 255)
            if not sotto:
                for (cc, rr) in alti:              # sopra il ponte e sulle rampe l'ombra del ponte non c'è
                    cv2.rectangle(ombra, (int(cc * 30 * PX), int(rr * 30 * PX)),
                                  (int((cc + 1) * 30 * PX), int((rr + 1) * 30 * PX)), 0, -1)
            ombra = cv2.GaussianBlur(ombra, (0, 0), 1.2 * PX)        # penombra
            g += luce["forza"] * (1.0 - ombra.astype(np.float32) / 255.0)
        grad = float(M.cfg.get("luce_gradiente", 0.0))
        if grad and self.luci:
            lx, ly = _dir(self.luci[0]["azimut"])
            xs = (np.arange(W, dtype=np.float32) / PX - C["larghezza"] / 2) / C["larghezza"]
            ys = (np.arange(H, dtype=np.float32) / PX - C["altezza"] / 2) / C["altezza"]
            g *= 1.0 + grad * (lx * xs[None, :] + ly * ys[:, None]) * 2
        if sotto:
            buio = float(M.cfg.get("tunnel_buio", 0.35))
            for t in C.get("tunnel", []):
                x0, y0, x1, y1 = t["rett"]
                m = np.zeros((H, W), np.float32)
                # dentro il tunnel la luce cala dagli imbocchi verso il centro
                if t["asse"] == "EW":
                    xs = np.arange(int(x0 * PX), int(x1 * PX))
                    d = np.minimum(xs / PX - x0, x1 - xs / PX)
                    f = buio + (1 - buio) * np.exp(-d / 8.0)
                    m[int(y0 * PX):int(y1 * PX), int(x0 * PX):int(x1 * PX)] = 1 - f[None, :]
                else:
                    ys = np.arange(int(y0 * PX), int(y1 * PX))
                    d = np.minimum(ys / PX - y0, y1 - ys / PX)
                    f = buio + (1 - buio) * np.exp(-d / 8.0)
                    m[int(y0 * PX):int(y1 * PX), int(x0 * PX):int(x1 * PX)] = 1 - f[:, None]
                g *= 1 - m
        return g

    def _celle_alte(self):
        q = self.M.C.get("quote", {})
        return [c for c, v in q.items() if v["z"] > 0.5 or v["tipo"] == "rampa"]

    def _oggetti_alti(self):
        """Segmenti che fanno ombra, con la loro altezza (cm)."""
        M, c = self.M, self.M.cfg
        out = [(s, c.get("altezza_muri", 11.5)) for s in M._muri]
        out += [(s, 15.0) for s in M._ostacolo]
        for t in M.C.get("tunnel", []):
            out += [(s, t.get("alto", 23.0)) for s in t["pareti"]]
        return out

    def _ripiani(self):
        """Piani sollevati (il ponte): rettangolo e altezza."""
        out = []
        for t in self.M.C.get("tunnel", []):
            out.append((t["rett"], t.get("alto", 23.0)))
        return out

    # ------------------------------------------------------------------
    #  NELL'IMMAGINE DELLA CAMERA: ombra del robot, LED, riflessi dei verdi lucidi
    # ------------------------------------------------------------------
    def guadagno_dinamico(self, pose, proietta, LIN_W, LIN_H, g_fisso, basso=False):
        """Luce finale (LIN_H x LIN_W) nell'immagine della camera della linea: luce fissa del campo x ombra del robot,
        poi le strisce LED RIEMPIONO le zone scure (non sbiancano quelle già chiare: la camera regola l'esposizione)."""
        M, c = self.M, self.M.cfg
        g = np.ones((LIN_H, LIN_W), np.float32)
        x, y, h = pose
        dx, dy = _dir(h)
        rx, ry = _dx(h)
        Lf = c.get("robot_davanti", c["lunghezza_robot"] / 2)
        Lb = c["lunghezza_robot"] - Lf
        W = c["larghezza_robot"] / 2
        corpo = [(x + dx * f + rx * l, y + dy * f + ry * l) for f, l in ((Lf, -W), (Lf, W), (-Lb, W), (-Lb, -W))]
        hr = c.get("altezza_robot", 21.0)
        for luce in ([] if basso else self.luci):          # nel tunnel non c'è luce diretta: niente ombra del robot
            ox, oy = _vettore_ombra(luce, hr * 0.6)          # il corpo pieno è più basso del braccio
            pts = np.array(corpo + [(px + ox, py + oy) for px, py in corpo], np.float64)
            hull = cv2.convexHull(pts.astype(np.float32)).reshape(-1, 2)
            img_pts = [proietta(px, py, pose) for px, py in hull]
            if any(u < -5e3 for u, _ in img_pts):
                continue
            m = np.zeros((LIN_H, LIN_W), np.uint8)
            cv2.fillPoly(m, [np.array(img_pts, np.int32)], 255)
            m = cv2.GaussianBlur(m, (0, 0), 6)
            g -= luce["forza"] * m.astype(np.float32) / 255.0
        # strisce LED: illuminano soprattutto la parte vicina (in basso nell'immagine)
        g = g_fisso * g
        accese = sum(1 for v in M.led.values() if v)
        if accese:
            v = np.linspace(0.0, 1.0, LIN_H, dtype=np.float32)[:, None]
            led = self.led_forza * accese / 2.0 * (0.35 + 0.65 * v)
            g = g + led * np.clip(1.0 - g, 0.0, None)
        return g

    def riflesso_verdi(self, pose, cam, proietta):
        """Per ogni verde LUCIDO in vista: quanto è coperto dal riflesso di una luce (0..1)."""
        out = {}
        if not self.luci:
            return out
        Cx, Cy, Cz = cam
        for v in self.M.C["verdi"]:
            if not v.get("lucido"):
                continue
            px, py = v["x"] + v["w"] / 2, v["y"] + v["h"] / 2
            if abs(px - pose[0]) > 40 or abs(py - pose[1]) > 40:
                continue
            pz = self.M.quota(px, py)[0]
            V = np.array([Cx - px, Cy - py, Cz - pz])
            V /= np.linalg.norm(V) + 1e-9
            best = 0.0
            for luce in self.luci:
                lx, ly = _dir(luce["azimut"])
                e = math.radians(luce["elevazione"])
                Lv = np.array([lx * math.cos(e), ly * math.cos(e), math.sin(e)])
                Hv = V + Lv
                Hv /= np.linalg.norm(Hv) + 1e-9
                spec = max(0.0, Hv[2]) ** 60 * min(1.0, luce["forza"] / 0.25)
                best = max(best, spec)
            if best > 0.02:
                out[v["id"]] = min(1.0, best * 1.6)
        self.riflessi = out
        return out

    # ------------------------------------------------------------------
    #  CONO DEL LASER (VL53L1X)
    # ------------------------------------------------------------------
    def tof_cono(self, ox, oy, h_raggio, solidi, raggio_segmento, centro):
        """Distanza letta dal VL53L1X con un cono di 'tof_cono' gradi.
        centro = distanza del raggio centrale (già con rampe e pavimenti rialzati) o None.
        Il sensore riceve luce da tutto il cono: vince il bersaglio che rimanda più segnale (vicino e grande),
        quindi uno stipite a lato della porta "copre" lo spazio libero in mezzo (come sul robot vero)."""
        c = self.M.cfg
        n = int(c.get("tof_cono_raggi", 9))
        tmax = c["tof_max"]
        colpi = []
        for i in range(n):
            a = h_raggio + self.cono * (i / (n - 1) - 0.5)
            ddx, ddy = _dir(a)
            best = None
            if i == n // 2 and centro is not None:
                best = centro
            else:
                for s in solidi:
                    d = raggio_segmento(ox, oy, ddx, ddy, s[0], s[1])
                    if d is not None and (best is None or d < best):
                        best = d
            if best is not None and best <= tmax:
                peso = 1.0 / max(best, 4.0) ** 2
                colpi.append((best, peso))
        if not colpi:
            return None
        # istogramma a scatti di 3 cm: vince il gruppo con più segnale
        gruppi = {}
        for d, p in colpi:
            k = int(d // 3)
            gruppi.setdefault(k, []).append((d, p))
        migliore = max(gruppi.values(), key=lambda g: sum(p for _, p in g))
        tot = sum(p for _, p in migliore)
        return sum(d * p for d, p in migliore) / tot

    def rumore_tof(self, d):
        a, b = self.M.cfg.get("tof_rumore_cono", (0.5, 1.6))
        return a + b * (d / 100.0) ** 2
