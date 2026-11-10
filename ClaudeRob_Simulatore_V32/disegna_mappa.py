"""
[Sim V32] Disegna la mappa a piastrelle della pista della scuola (o di un altro campo a piastrelle).

Uso:   python3 disegna_mappa.py                 -> mappa_scuola.png
       python3 disegna_mappa.py rcj2026 x.png   -> un altro campo
Serve matplotlib (pip3 install matplotlib). La mappa serve alla squadra per controllare la pista:
colonne A, B, C... da sinistra, righe 1, 2, 3... dall'alto, come nella battaglia navale.
"""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrow

import piastrelle as P

LETTERE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def campo(nome):
    if nome == "scuola_nuova":
        import pista_scuola_piastrelle as S
        return S.crea_campo_scuola_piastrelle()
    import campo as CP
    return CP.crea_campo(nome)


def disegna(C, uscita, titolo):
    T = P.T
    W, H = C["larghezza"], C["altezza"]
    nc, nr = int(W // T), int(H // T)
    fig, ax = plt.subplots(figsize=(W / 22, H / 22 + 1.2), dpi=110)
    ax.set_xlim(-14, W + 4)
    ax.set_ylim(H + 4, -14)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), W, H, color="#f4f4f2", zorder=0))
    # piastrelle: colore secondo la superficie
    celle_percorso = {p["cella"] for p in C["percorso"]}
    for (c, r), q in C["quote"].items():
        col = None
        if q["tipo"] == "rampa":
            col = "#f3d9a4" if q.get("pendenza", 0) > 0 else "#d9e7f3"
        elif q["tipo"] == "altalena":
            col = "#e6d4f2"
        elif q["tipo"] == "banca":
            col = "#f2e0d4"
        elif q["z"] > 0.5:
            col = "#f7c9a8"                                   # in alto: il ponte
        elif (c, r) in celle_percorso or C["celle_linea"].get((c, r)) == "ramo":
            col = "#ffffff"
        if col:
            ax.add_patch(Rectangle((c * T, r * T), T, T, color=col, zorder=1))
    for i in range(nc + 1):
        ax.plot([i * T, i * T], [0, H], color="#c9c9c4", lw=0.8, zorder=2)
    for j in range(nr + 1):
        ax.plot([0, W], [j * T, j * T], color="#c9c9c4", lw=0.8, zorder=2)
    for i in range(nc):
        ax.text(i * T + 15, -6, LETTERE[i], ha="center", va="center", fontsize=11, weight="bold", color="#555")
    for j in range(nr):
        ax.text(-7, j * T + 15, str(j + 1), ha="center", va="center", fontsize=11, weight="bold", color="#555")
    # arena
    if C.get("arena"):
        a = C["arena"]
        ax.add_patch(Rectangle((a["x"], a["y"]), a["w"], a["h"], color="#e9eef2", zorder=1))
        for tr in C.get("triangoli", []):
            ax.add_patch(Polygon(tr["poli"], color="#2f9e44" if tr["colore"] == "verde" else "#d63333", zorder=3))
        for b in C.get("palline", []):
            ax.add_patch(plt.Circle((b["x"], b["y"]), 2.25, color="#222" if b["tipo"] == "nera" else "#b8b8b8",
                                    ec="#555", zorder=5))
    # tunnel: tetto tratteggiato e pareti
    for t in C.get("tunnel", []):
        x0, y0, x1, y1 = t["rett"]
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ls="--", lw=1.5, ec="#8a5a2b", zorder=6))
        for a, b in t["pareti"]:
            ax.plot([a[0], b[0]], [a[1], b[1]], color="#8a5a2b", lw=2.2, zorder=6)
        ax.text((x0 + x1) / 2, y1 + 3.5, "sotto: TUNNEL 91 x 30 cm, alto 22,3 cm", ha="center", fontsize=7,
                color="#8a5a2b", zorder=9)
    # linee nere
    for L in C["linee"]:
        xs, ys = zip(*L)
        ax.plot(xs, ys, color="#111", lw=2.4, solid_capstyle="butt", zorder=4)
    for L in C.get("linee_sotto", []):
        xs, ys = zip(*L)
        ax.plot(xs, ys, color="#2b6cb0", lw=2.0, ls=(0, (3, 2)), zorder=4)
    for x0, y0, x1, y1 in C.get("dossi", []) + C.get("dossi_sotto", []):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, color="#9aa5b1", alpha=0.8, zorder=5))
    for v in C["verdi"]:
        ax.add_patch(Rectangle((v["x"], v["y"]), v["w"], v["h"], color="#1f9d3a", zorder=6))
    for k, col in (("argento", "#a9a9a9"), ("nero_uscita", "#111"), ("rosso", "#d62020")):
        d = C.get(k)
        if d:
            ax.add_patch(Rectangle((d["x"], d["y"]), d["w"], d["h"], color=col, zorder=7))
    for a, b in C.get("muri", []):
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#6b6b6b", lw=3.2, zorder=8)
    # partenza
    p = C["partenza"]
    import math
    hx, hy = math.sin(math.radians(p["heading"])), -math.cos(math.radians(p["heading"]))
    ax.add_patch(FancyArrow(p["x"] - hx * 6, p["y"] - hy * 6, hx * 12, hy * 12, width=2.5, color="#e8590c", zorder=9))
    # numeri del percorso (ordine delle piastrelle) e checkpoint
    for n, pz in enumerate(C["percorso"], 1):
        c, r = pz["cella"]
        dy = 25 if pz.get("sotto") else 6
        ax.text(c * T + 3, r * T + dy, str(n), fontsize=6, color="#2b6cb0" if pz.get("sotto") else "#777", zorder=9)
        if pz.get("cp"):
            ax.add_patch(plt.Circle((c * T + 26, r * T + 4), 2.2, color="#f2c200", zorder=9))
    for testo, x, y, _ in C.get("etichette", []):
        ax.text(x, y, testo, ha="center", va="center", fontsize=6.5, weight="bold", color="#7a1f5c", zorder=10,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))
    leg = ("Legenda:  arancio = ponte (23 cm)   giallo = rampa in salita   azzurro = rampa in discesa   "
           "lilla = altalena\n          blu tratteggiato = linea nel tunnel   grigio = tubi   pallino giallo = checkpoint   "
           "numeri = ordine delle piastrelle")
    ax.text(0, H + 4, leg, fontsize=7, va="top", color="#333")
    ax.set_title(titolo, fontsize=12, weight="bold")
    fig.savefig(uscita, bbox_inches="tight")
    print("scritto", uscita)


if __name__ == "__main__":
    nome = sys.argv[1] if len(sys.argv) > 1 else "scuola_nuova"
    out = sys.argv[2] if len(sys.argv) > 2 else ("mappa_scuola.png" if nome == "scuola_nuova" else f"mappa_{nome}.png")
    titolo = "Pista della scuola a piastrelle (bozza dalle foto del 10/11) - da correggere" if nome == "scuola_nuova" else nome
    disegna(campo(nome), out, titolo)
