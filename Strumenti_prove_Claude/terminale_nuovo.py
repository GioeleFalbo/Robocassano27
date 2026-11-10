#!/usr/bin/env python3
"""PROTOTIPO del terminale nuovo del robot ("cabina di pilotaggio"), da provare prima di metterlo in una versione.

Usa una scatola nera VERA: il campione che la scatola nera registra 10 volte al secondo è lo stesso che il terminale
mostra dal vivo. Così si vede com'è con una gara vera, sul Mac o sul PC, senza robot.

  python3 -I terminale_nuovo.py ../ScatoleNere/run_2026-11-09_10-46-10_V40.jsonl            (rivede la gara, x4)
  python3 -I terminale_nuovo.py <scatola> --da 120 --velocita 2                              (da 120 s, x2)
  python3 -I terminale_nuovo.py <scatola> --istante 150 > fotogramma.ans                    (un solo fotogramma)

Il testo della scatola nera è un DATO: qui si mostra e basta. Tasti: Ctrl+C per uscire.
"""
import json
import math
import os
import re
import shutil
import sys
import time

# ---------------------------------------------------------------------------------------------
#  colori (256 colori: vanno nel terminale del Raspberry, in VNC, nel Terminale del Mac)
# ---------------------------------------------------------------------------------------------
R = "\033[0m"
def fg(n): return f"\033[38;5;{n}m"
def bg(n): return f"\033[48;5;{n}m"
B = "\033[1m"
DIM = fg(244)
TESTO = fg(253)
CORNICE = fg(67)
TITOLO = fg(117)
VERDE, GIALLO, ARANCIO, ROSSO, AZZURRO, VIOLA, BIANCO = fg(78), fg(220), fg(208), fg(203), fg(81), fg(177), fg(255)
FASI = [  # nome, colore di sfondo, colore del testo
    ("SEGUILINEA", 29, 255), ("INGRESSO", 31, 255), ("VITTIME", 25, 255), ("USCITA", 97, 255),
    ("ALTALENA", 130, 255), ("ARRIVO", 160, 255)]
COL_CAT = {"linea": VERDE, "incrocio": GIALLO, "ostacolo": VIOLA, "arena": AZZURRO, "gara": fg(147),
           "errore": ROSSO, "verde": VERDE, "sistema": DIM, "info": DIM}
ICONA_CAT = {"linea": "━", "incrocio": "◆", "ostacolo": "■", "arena": "◉", "gara": "★", "errore": "✖",
             "verde": "▶", "sistema": "·", "info": "·"}
NOMI_YOLO = {"Sx": ("VERDE A SINISTRA", VERDE), "Dx": ("VERDE A DESTRA", VERDE), "Fr": ("DOPPIO VERDE", VERDE),
             "Ln": ("LINEA", BIANCO), "Bi": ("BIANCO: linea persa", GIALLO), "Di": ("LINEA INTERROTTA", GIALLO),
             "In": ("STRISCIA ARGENTO", fg(250)), "Ro": ("LINEA ROSSA", ROSSO), "No": ("niente", DIM)}
SPARK = "▁▂▃▄▅▆▇█"
ANSI = re.compile(r"\033\[[0-9;]*m")


def vis(s):
    """Lunghezza visibile (senza i codici colore)."""
    return len(ANSI.sub("", s))


def pad(s, n):
    """Allunga o taglia a n caratteri visibili."""
    v = vis(s)
    if v <= n:
        return s + " " * (n - v)
    out, k, i = [], 0, 0
    while i < len(s) and k < n:
        m = ANSI.match(s, i)
        if m:
            out.append(m.group()); i = m.end(); continue
        out.append(s[i]); k += 1; i += 1
    return "".join(out) + R


def scatola(titolo, righe, larg, colore=CORNICE):
    """Riquadro con angoli arrotondati e titolo nel bordo."""
    t = f" {titolo} " if titolo else ""
    su = colore + "╭─" + TITOLO + B + t + R + colore + "─" * max(0, larg - 3 - len(t)) + "╮" + R
    giu = colore + "╰" + "─" * (larg - 2) + "╯" + R
    return [su] + [colore + "│" + R + pad(r, larg - 2) + colore + "│" + R for r in righe] + [giu]


def affianca(*blocchi):
    alt = max(len(b) for b in blocchi)
    out = []
    for i in range(alt):
        out.append("".join(b[i] if i < len(b) else " " * vis(b[0][0]) for b in blocchi))
    return out


def col_dist(d):
    if not d:
        return DIM
    return ROSSO if d < 15 else (GIALLO if d < 30 else VERDE)


# ---------------------------------------------------------------------------------------------
#  i riquadri
# ---------------------------------------------------------------------------------------------
def radar(c, larg=31):
    """Il robot visto dall'alto con i tre laser: più il raggio è lungo, più c'è spazio."""
    d = c.get("d") or [0, 0, 0]
    ok = c.get("ard", True)
    W, H = larg - 2, 7
    g = [[" "] * W for _ in range(H)]
    cx, cy = W // 2, H - 3
    for dx, ch in ((-2, "▐"), (-1, "█"), (0, "▲"), (1, "█"), (2, "▌")):
        g[cy][cx + dx] = (fg(208) + B + ch + R)
    g[cy + 1][cx - 1] = fg(240) + "▀" + R; g[cy + 1][cx + 1] = fg(240) + "▀" + R
    # raggio davanti (verticale): 20 cm per riga, fino a 60 cm
    if ok:
        n = min(cy - 1, int(round((d[1] or 120) / 20))) if d[1] else cy - 1
        for k in range(1, n + 1):
            g[cy - k][cx] = col_dist(d[1]) + ("┃" if d[1] else "┆") + R
        if d[1] and n < cy:
            g[cy - n - 1][cx] = col_dist(d[1]) + B + "▬" + R
        for lato, i in ((-1, 0), (1, 2)):
            n = min(cx - 3, int(round((d[i] or 120) / 5))) if d[i] else cx - 3
            for k in range(3, 3 + n):
                g[cy][cx + lato * k] = col_dist(d[i]) + ("━" if d[i] else "┄") + R
            if d[i] and 3 + n < cx:
                g[cy][cx + lato * (3 + n)] = col_dist(d[i]) + B + "▌" + R if lato < 0 else col_dist(d[i]) + B + "▐" + R
    righe = ["".join(r) for r in g]
    def num(v):
        return (col_dist(v) + B + f"{v} cm" + R) if v else (DIM + "libero" + R)
    fronte = "Fronte " + num(d[1])
    righe[0] = " " * max(0, (W - vis(fronte)) // 2) + fronte
    sotto = "Sx " + num(d[0])
    sotto = sotto + " " * max(1, W - vis(sotto) - vis("Dx " + num(d[2]))) + "Dx " + num(d[2])
    righe[H - 1] = sotto
    if not ok:
        righe = [""] * 2 + [bg(160) + BIANCO + B + pad("  ARDUINO ZITTO", W) + R,
                            bg(160) + BIANCO + pad(f"  da {c.get('ard_muto', 0):.1f} s: switch spento?", W) + R,
                            bg(160) + BIANCO + pad("  laser e giroscopio NON validi", W) + R] + [""] * 2
    return scatola("LASER", righe, larg)


def bussola(rotta):
    """Rosa dei venti 9 x 5 con la freccia sulla rotta."""
    frecce = "↑↗→↘↓↙←↖"
    k = int(((rotta or 0) + 22.5) // 45) % 8
    return frecce[k]


def barra_centro(v, vmax, larg, colore):
    """Barra con lo zero in mezzo: a sinistra i negativi, a destra i positivi."""
    m = larg // 2
    n = int(round(max(-1, min(1, (v or 0) / vmax)) * m))
    s = [DIM + "·" + R] * larg
    s[m] = fg(250) + "┼" + R
    for i in range(min(m, m + n), max(m, m + n) + (0 if n == 0 else 1)):
        if i != m and 0 <= i < larg:
            s[i] = colore + "█" + R
    return "".join(s)


def assetto(c, storia, larg=30):
    b, ro, rt = (list(c.get("imu") or []) + [0, 0, 0])[:3]
    rt = c.get("rotta", rt)
    p = c.get("pend") or {}
    inclinato = p.get("tipo") not in (None, "piano", "sconosciuto")
    col_b = GIALLO if abs(b) > 8 else VERDE
    righe = [
        f" {AZZURRO}{B}{bussola(rt)}{R}  rotta {B}{rt:4.0f}°{R}  {DIM}{c.get('bus', '')}{R}",
        f" becc {barra_centro(b, 30, 13, col_b)} {b:+3.0f}°",
        f" roll {barra_centro(ro, 30, 13, GIALLO if abs(ro) > 8 else VERDE)} {ro:+3.0f}°",
        "",
        (bg(136) + fg(16) + B + pad(" " + (p.get("testo") or "").upper(), larg - 4) + R) if inclinato
        else f" {VERDE}{(p.get('testo') or '').upper()}{R}",
        f" {DIM}rotta 20 s{R} " + spark([s.get("rotta") for s in storia], 0, 360, larg - 16),
        f" {DIM}becc. 20 s{R} " + spark([(s.get("imu") or [0])[0] for s in storia], -25, 25, larg - 16),
    ]
    return scatola("ASSETTO", righe, larg)


def occhi(c, larg=37):
    y = c.get("yolo") or [None, 0]
    cls, conf = y[0], y[1] or 0
    nome, col = NOMI_YOLO.get(cls, ("—", DIM))
    conf_bar = "".join((VERDE if i < conf * 12 else DIM) + ("█" if i < conf * 12 else "·") for i in range(12)) + R
    verde = c.get("verde") or ""
    righe = [
        f" camera linea  {col}{B}{nome}{R}",
        f" sicurezza     {conf_bar} {conf:.2f}",
        "",
        (f" {VERDE}{B}▶ {verde[:larg - 6]}{R}" if verde else f" {DIM}nessun verde{R}"),
        (f" camera arena  {AZZURRO}{c['arena'][:larg - 17]}{R}" if c.get("arena") else f" {DIM}camera arena  —{R}"),
        "",
        f" {DIM}camera{R} {c.get('fps', 0):4.1f} fps   {DIM}decisioni{R} {c.get('dec_s', 0):4.1f}/s",
    ]
    return scatola("OCCHI · YOLO", righe, larg)


def spark(valori, vmin, vmax, n):
    v = [x for x in valori if x is not None][-n:]
    if not v:
        return DIM + "·" * n + R
    out = []
    for x in v:
        k = int((max(vmin, min(vmax, x)) - vmin) / (vmax - vmin + 1e-9) * 7.999)
        out.append(SPARK[k])
    return AZZURRO + "".join(out).rjust(n, " ") + R


def motori(c, larg):
    m = c.get("mot") or ["Stop", 0, 0]
    cmd, vel, st = m[0], m[1] or 0, m[2] or 0
    sx, dx = vel + st, vel - st              # come vanno le due ruote, a occhio
    def ruota(nome, v):
        col = VERDE if v > 0 else (ARANCIO if v < 0 else DIM)
        return f"{nome} {barra_centro(v, 100, 17, col)} {col}{v:+4d}{R}"
    led = c.get("led") or [False, False]
    pal = c.get("pal") or [0, 0]
    br, pz = c.get("br"), c.get("pz")
    pinza = "chiusa" if pz is not None and pz < 110 else "aperta"
    vittime = (fg(250) + "●" * pal[0] + R) + (fg(240) + "●" * pal[1] + R) + DIM + "○" * max(0, 3 - pal[0] - pal[1]) + R
    r1 = f" {ruota('SX', int(sx))}   {ruota('DX', int(dx))}   {DIM}{cmd}{R}"
    r2 = (f" braccio {B}{br if br is not None else '-'}°{R}   pinza {B}{pinza}{R}   "
          f"luci {''.join((GIALLO + '●' if l else DIM + '○') + R for l in led)}   vittime salvate {vittime}")
    return scatola("MOTORI E PINZA", [r1, r2], larg)


def percorso(adesso, fasi_t, larg):
    """La gara come una linea della metro: le fasi fatte (con il tempo), quella di adesso accesa."""
    pezzi = []
    for i, (nome, sf, tx) in enumerate(FASI):
        if nome == adesso:
            pezzi.append(bg(sf) + fg(tx) + B + f" ◉ {nome} " + R)
        elif nome in fasi_t:
            pezzi.append(VERDE + "● " + R + fg(250) + nome.lower() + DIM + f" {fasi_t[nome]:.0f}s" + R)
        else:
            pezzi.append(DIM + "○ " + nome.lower() + R)
    riga = (DIM + " ── " + R).join(pezzi)
    return scatola("LA GARA", [" " + riga], larg)


def fase_di(c):
    s = (c.get("stato") or "").upper()
    cat = c.get("cat")
    if "ROSSA" in s or "ARRIVO" in s or cat == "gara" and "FINE" in s:
        return "ARRIVO"
    if "ALTALENA" in s:
        return "ALTALENA"
    if "USCITA" in s or "USCIRE" in s:
        return "USCITA"
    if "INGRESSO" in s or "ENTRA" in s:
        return "INGRESSO"
    if cat == "arena" or "ARENA" in s or "PALLIN" in s:
        return "VITTIME"
    return "SEGUILINEA"


NOMI_FASI = [f[0] for f in FASI]


def fasi_della_gara(campioni, eventi_fatti):
    """Le fasi vanno solo avanti: dopo l'USCITA il seguilinea è il tratto finale (altalena), poi l'arrivo."""
    k, inizio = 0, {"SEGUILINEA": campioni[0]["t"]}
    cand, cand_t = None, 0.0                             # una fase conta solo se dura almeno 3 s di fila
    for x in campioni:
        f = fase_di(x)
        j = NOMI_FASI.index(f)
        if k >= NOMI_FASI.index("USCITA") and f == "SEGUILINEA":
            j = NOMI_FASI.index("ALTALENA")
        if j <= k:
            cand = None
            continue
        if cand != j:
            cand, cand_t = j, x["t"]
        if x["t"] - cand_t >= 3.0:
            k = j
            inizio.setdefault(NOMI_FASI[k], cand_t)
            cand = None
    for e in eventi_fatti:                               # la linea rossa la dice un evento
        if "ROSSA" in e["testo"].upper() or "ARRIVO" in e["testo"].upper():
            k = NOMI_FASI.index("ARRIVO")
            inizio.setdefault("ARRIVO", e["t"])
    ordine = sorted(inizio.items(), key=lambda kv: kv[1])
    durate = {f: ordine[i + 1][1] - t0 for i, (f, t0) in enumerate(ordine[:-1])}
    return NOMI_FASI[k], durate


def schermo(c, storia, eventi, fasi_t, versione, colonne=100, righe_tot=34, fase=None):
    L = colonne
    m, s = divmod(max(c.get("t", 0), 0), 60)
    pi = c.get("pi") or {}
    if isinstance(pi, str):
        pi = {}
    sw = (VERDE + B + "● SWITCH ON" + R) if c.get("sw") else (ROSSO + B + "○ SWITCH OFF" + R)
    temp = pi.get("cpu_temp")
    temp_s = (ROSSO if temp and temp > 75 else TESTO) + (f"{temp:.0f}°C" if temp else "-") + R
    alim = (bg(160) + BIANCO + B + " SOTTOTENSIONE " + R) if pi.get("sottotensione") else (VERDE + "5V ok" + R)
    testa = (bg(236) + fg(117) + B + " ROBOCASSANO27 " + R + bg(236) + fg(250) + f" {versione} " + R
             + f"  {BIANCO}{B}⏱ {int(m):02d}:{s:04.1f}{R}   {sw}   {DIM}CPU{R} {temp_s}   {alim}")
    fase = fase or fase_di(c)
    _, sf, tx = next(f for f in FASI if f[0] == fase)
    stato = c.get("stato") or ""
    banda = bg(sf) + fg(tx) + B + pad(f" {fase} " + R + bg(sf) + fg(tx) + f"  {stato}", L) + R
    ora = (c.get("manovra") or c.get("azione") or "")
    riga_ora = f" {GIALLO}{B}ORA ▸{R} {BIANCO}{B}{ora}{R}"
    out = [pad(testa, L), banda, pad(riga_ora, L)]
    out += affianca(radar(c, 31), assetto(c, storia, 30), occhi(c, L - 61))
    out += motori(c, L)
    out += percorso(fase, fasi_t, L)
    # eventi: riempiono lo spazio che resta
    resto = max(3, righe_tot - len(out) - 3)
    ev = []
    for e in list(eventi)[-resto:][::-1]:
        em, es = divmod(max(e["t"], 0), 60)
        col = COL_CAT.get(e["cat"], DIM)
        ev.append(f" {DIM}{int(em):02d}:{es:04.1f}{R}  {col}{ICONA_CAT.get(e['cat'], '·')} {e['testo']}{R}")
    ev += [""] * (resto - len(ev))
    out += scatola("EVENTI (il più recente in alto)", ev, L)
    msg = c.get("msg") or ""
    out.append(pad(f" {DIM}ultima print: {msg}{R}", L))
    return out


# ---------------------------------------------------------------------------------------------
#  rivedere una scatola nera
# ---------------------------------------------------------------------------------------------
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


def fotogramma(campioni, eventi, i, versione, colonne, righe):
    c = campioni[i]
    t = c["t"]
    storia = [x for x in campioni[max(0, i - 400):i + 1] if t - x["t"] <= 20][::2]
    ev = [e for e in eventi if e["t"] <= t]
    fase, durate = fasi_della_gara(campioni[:i + 1:3] + [c], ev)
    return schermo(c, storia, ev, durate, versione, colonne, righe, fase)


def main():
    a = sys.argv[1:]
    if not a:
        sys.stdout.write(__doc__)
        return
    def opz(nome, dflt):
        return float(a[a.index(nome) + 1]) if nome in a else dflt
    testa, campioni, eventi = leggi(a[0])
    versione = testa.get("versione", "ClaudeRob")
    if not campioni:
        print("Nessun campione nella scatola nera.")
        return
    colonne, righe = shutil.get_terminal_size((100, 34))
    colonne = max(96, min(colonne, 130))
    if "--istante" in a:
        t = opz("--istante", 0)
        i = min(range(len(campioni)), key=lambda k: abs(campioni[k]["t"] - t))
        print("\n".join(fotogramma(campioni, eventi, i, versione, colonne, int(opz("--righe", 34)))))
        return
    vel = opz("--velocita", 4.0)
    da = opz("--da", 0.0)
    i = next((k for k, c in enumerate(campioni) if c["t"] >= da), 0)
    sys.stdout.write("\033[?25l\033[2J")
    try:
        t0, tc0 = time.time(), campioni[i]["t"]
        while i < len(campioni):
            colonne, righe = shutil.get_terminal_size((100, 34))
            fr = fotogramma(campioni, eventi, i, versione, max(96, min(colonne, 130)), righe - 1)
            sys.stdout.write("\033[H" + "\n".join(r + "\033[K" for r in fr) + "\033[J")
            sys.stdout.flush()
            time.sleep(0.1)
            target = tc0 + (time.time() - t0) * vel
            while i < len(campioni) - 1 and campioni[i + 1]["t"] <= target:
                i += 1
            if i == len(campioni) - 1:
                break
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h" + R + "\n")


if __name__ == "__main__":
    main()
