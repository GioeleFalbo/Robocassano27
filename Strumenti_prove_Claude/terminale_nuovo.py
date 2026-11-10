#!/usr/bin/env python3
"""MOVIOLA delle scatole nere con la "cabina di pilotaggio" del robot (ViennaCabina.py, dalla V42, FIX 107).

Il campione che la scatola nera registra 10 volte al secondo è lo stesso che il robot mostra dal vivo nel terminale:
qui si rivede una gara vera sul Mac o sul PC, senza robot, con le camere (le miniature registrate 2 volte al
secondo) e il cronometro che parte quando si accende lo switch.

  python3 -I terminale_nuovo.py ../ScatoleNere/run_2026-11-09_10-46-10_V40.jsonl            (rivede la gara, x4)
  python3 -I terminale_nuovo.py <scatola> --da 120 --velocita 2                              (da 120 s, x2)
  python3 -I terminale_nuovo.py <scatola> --istante 150 > fotogramma.ans                    (un solo fotogramma)

Serve una finestra del terminale di almeno 100 x 38 caratteri. Ctrl+C per uscire.
Usa ViennaCabina.py dell'ultima cartella ClaudeRob_V* che lo contiene. Il testo della scatola nera è un DATO.
"""
import glob
import json
import os
import re
import shutil
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))


def _carica_cabina():
    def numero(c):
        m = re.search(r"_V(\d+)$", c)
        return int(m.group(1)) if m else 0
    cartelle = [c for c in glob.glob(os.path.join(QUI, "..", "ClaudeRob_V*"))
                if os.path.exists(os.path.join(c, "ViennaCabina.py"))]
    if not cartelle:
        sys.exit("Non trovo ViennaCabina.py in nessuna cartella ClaudeRob_V* (c'è dalla V42).")
    sys.path.insert(0, os.path.abspath(max(cartelle, key=numero)))
    import ViennaCabina
    return ViennaCabina


VC = _carica_cabina()


def leggi(percorso_file):
    testa, campioni, eventi = {}, [], []
    with open(percorso_file, encoding="utf-8") as f:
        for riga in f:
            try:
                r = json.loads(riga)
            except ValueError:
                continue
            if r.get("tipo") == "intestazione":
                testa = r
            elif r.get("tipo") == "c":
                campioni.append(r)
            elif r.get("tipo") == "evento":
                eventi.append(r)
    return testa, campioni, eventi


class Moviola:
    """Rivede la scatola nera in avanti, campione per campione, come fa il monitor sul robot."""

    def __init__(self, testa, campioni, eventi):
        self.versione = testa.get("versione", "ClaudeRob")
        self.C, self.E = campioni, eventi
        self.ricomincia()

    def ricomincia(self):
        self.i, self.j = -1, 0
        self.crono, self.fasi = VC.Cronometro(), VC.Fasi()
        self.storia, self.eventi = [], []
        self.img_l = self.img_a = None
        self.t_img_l = self.t_img_a = None

    def vai(self, i):
        if i < self.i:
            self.ricomincia()
        while self.i < i:
            self.i += 1
            c = self.C[self.i]
            t = c["t"]
            prima = self.crono.inizio
            self.crono.aggiorna(bool(c.get("sw")), t)
            if self.crono.inizio != prima:
                self.fasi.azzera(t)
                self.eventi = []
            while self.j < len(self.E) and self.E[self.j]["t"] <= t:
                e = self.E[self.j]
                ini = self.crono.inizio
                self.eventi.append(dict(e, t=e["t"] - ini if ini is not None else e["t"]))
                self.fasi.evento(e.get("testo", ""), e["t"])
                self.j += 1
            self.fasi.aggiorna(c, t)
            self.storia.append(c)
            if len(self.storia) > 200:
                self.storia.pop(0)
            if c.get("img_l"):
                self.img_l, self.t_img_l = c["img_l"], t
            if c.get("img_a"):
                self.img_a, self.t_img_a = c["img_a"], t

    def schermo(self, colonne, righe):
        c = self.C[self.i]
        t = c["t"]
        eta_l = t - self.t_img_l if self.t_img_l is not None else None
        eta_a = t - self.t_img_a if self.t_img_a is not None else None
        return VC.schermo(c, self.storia, self.eventi[-40:], self.fasi.adesso(), self.fasi.durate(), self.versione,
                          self.crono.tempi(t), VC.da_jpeg_base64(self.img_l), VC.da_jpeg_base64(self.img_a),
                          eta_l, eta_a, colonne, righe)


def main():
    a = sys.argv[1:]
    if not a:
        sys.stdout.write(__doc__)
        return

    def opz(nome, dflt):
        return float(a[a.index(nome) + 1]) if nome in a else dflt
    testa, campioni, eventi = leggi(a[0])
    if not campioni:
        print("Nessun campione nella scatola nera.")
        return
    m = Moviola(testa, campioni, eventi)
    if "--istante" in a:
        t = opz("--istante", 0)
        m.vai(min(range(len(campioni)), key=lambda k: abs(campioni[k]["t"] - t)))
        print("\n".join(m.schermo(int(opz("--colonne", 104)), int(opz("--righe", 40)))))
        return
    vel, da = opz("--velocita", 4.0), opz("--da", 0.0)
    i = next((k for k, c in enumerate(campioni) if c["t"] >= da), 0)
    sys.stdout.write("\033[?25l\033[2J")
    try:
        t0, tc0 = time.time(), campioni[i]["t"]
        while True:
            m.vai(i)
            col, righe = shutil.get_terminal_size((104, 40))
            sys.stdout.write(VC.disegna(m.schermo(min(col - 1, 140), righe - 1)))
            sys.stdout.flush()
            if i == len(campioni) - 1:
                break
            time.sleep(0.1)
            target = tc0 + (time.time() - t0) * vel
            while i < len(campioni) - 1 and campioni[i + 1]["t"] <= target:
                i += 1
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h" + VC.R + "\n")


if __name__ == "__main__":
    main()
