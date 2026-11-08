"""
[V29] LA PISTA DELLA SCUOLA (foto del 03/11/2026, due punti di vista della stessa pista).

Come è stata ricostruita
- Le piastrelle sono da 30 cm: la pista è 4 colonne x 7 righe (120 x 210 cm), più una colonna a destra
  (accanto all'arena) di cui le foto mostrano solo 3 piastrelle.
- L'ARENA è oltre il bordo alto della pista (nelle foto). Sul muro in comune ci sono:
    * l'INGRESSO (striscia ARGENTO) nella 3a colonna: ci arriva la linea verticale della colonna 3;
    * l'USCITA (striscia NERA) nella 1a colonna, all'angolo: da lì la linea scende, attraversa la linea
      lunga (verde DOPO l'incrocio = falso verde) e arriva alla LINEA ROSSA (arrivo).
    * tra le due porte c'è un pezzo di muro di circa 33 cm.
- Il percorso "di gara" che si legge dai verdi: si parte sulla linea lunga in alto verso destra, falso
  verde, dosso (tubo), al 2° incrocio verde a destra -> giù, zig-zag, quadrato arrotondato (verde a
  sinistra), su per lo stelo, alla T verde a sinistra -> linea lunga verso sinistra, all'incrocio con i
  due verdi verde a destra -> INGRESSO. Arena, USCITA, giù fino alla linea ROSSA.
- La parte bassa (piattaforma, rampa con i tubi, curve a S, incroci, zig-zag con T a doppio verde) è
  un insieme di esercizi con diversi vicoli ciechi: è disegnata com'è nelle foto.

COSA NON SI VEDE DALLE FOTO (valori messi a stima, da correggere):
- dimensioni dell'arena (messa 120 x 120 cm, come "arena_parete");
  [Sim V30] dalla terza foto (03/11, robot vicino alla parete): triangolo VERDE nell'angolo in fondo a
  sinistra, triangolo ROSSO nell'angolo vicino a destra (dietro il muro dopo l'ingresso), palline in fondo;
- [Sim V30] lungo il bordo DESTRO della pista (sotto la colonna accanto all'arena) c'è una PARETE: sul robot vero
  il robot la tocca sul semicerchio (scatola nera 03/11 V30, secondo 81);
- altezza della piattaforma e pendenza della rampa (messa 12 gradi sulle 2 piastrelle con i tubi;
  la piattaforma è disegnata in piano: il simulatore a linee libere ha una sola rampa);
- cosa c'è a destra della colonna accanto all'arena e sopra di essa (le linee finiscono al bordo).

[Sim V31] ARENA RIFATTA DALLA FOTO DALL'ALTO DEL 05/11/2026 (arena_dall_alto_2026-11-05.jpg):
- misure interne circa 120 x 90 cm: il lato lungo (120) è il muro in comune con la pista, profonda 90 cm;
- INGRESSO (argento) sul lato lungo, nella 3a colonna: confermato dalla foto (da 59 a 88 cm dall'angolo);
- USCITA (striscia NERA) NON più sul muro in comune: è sul lato CORTO verso la colonna accanto all'arena,
  da circa 29 a 56 cm dal muro in comune, accanto al triangolo ROSSO;
- triangolo ROSSO nell'angolo tra muro in comune e lato corto dell'uscita, VERDE nell'angolo opposto (lati 30 cm);
- dall'uscita la linea scende nella colonna accanto all'arena; la LINEA ROSSA d'arrivo l'ho messa lì, circa 30 cm
  dopo l'uscita (NON si vede nella foto: da verificare). La vecchia uscita della 1a colonna ora è muro.

Coordinate: le scrivo come nella FOTO (u verso destra, v verso il basso, v = 0 sul muro dell'arena,
la pista va da v = 0 a v = 210) e poi giro tutto di 90 gradi, perché il simulatore vuole l'arena a
destra della pista con l'ingresso sul suo muro SINISTRO (il robot entra andando verso est).
"""
import math

L_PISTA = 210.0            # cm: profondità della pista (7 righe)
A_PROF = 90.0              # cm: profondità dell'arena ([Sim V31] foto dall'alto del 05/11: 120 x 90)
A_LUNGO = 120.0            # cm: lato lungo dell'arena = muro in comune con la pista


def _arco(cx, cy, r, a0, a1, passi=16):
    """Arco in coordinate FOTO (0 gradi = destra, 90 = basso)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / passi)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / passi))) for i in range(passi + 1)]


def _quadrato_arrotondato(u0, v0, u1, v1, r=3.0):
    p = []
    p += _arco(u1 - r, v0 + r, r, -90, 0, 4)
    p += _arco(u1 - r, v1 - r, r, 0, 90, 4)
    p += _arco(u0 + r, v1 - r, r, 90, 180, 4)
    p += _arco(u0 + r, v0 + r, r, 180, 270, 4)
    return p + [p[0]]


# ------------------------------------------------------------------------------------------------
#  LINEE NERE (coordinate FOTO, cm)
# ------------------------------------------------------------------------------------------------
LINEE_FOTO = [
    # riga 1: linea lunga (dal bordo sinistro fino alla colonna accanto all'arena)
    [(0.0, 15.0), (150.0, 15.0)],
    # colonna 1: dall'USCITA giù fino alla linea ROSSA
    [(15.0, 0.0), (15.0, 39.0)],
    # colonna 2: dal muro giù, zig-zag, fino al quadrato arrotondato
    [(45.0, 0.0), (45.0, 43.0), (51.0, 43.0), (51.0, 46.0), (64.0, 46.0), (68.0, 36.0), (74.0, 50.0),
     (81.0, 36.0), (85.0, 45.0), (97.0, 45.0)],
    # colonna 3: dall'INGRESSO giù (finisce a metà della riga: vicolo cieco)
    [(75.0, 0.0), (75.0, 28.5)],
    # colonna 4: stelo dalla linea lunga al quadrato arrotondato
    [(104.5, 15.0), (104.5, 37.0)],
    # quadrato arrotondato (15 x 15 cm)
    _quadrato_arrotondato(97.0, 37.0, 112.0, 52.0),
    # colonna accanto all'arena: [Sim V31] parte dall'USCITA (lato corto dell'arena, a 43 cm di profondità),
    # gira verso la pista e scende; poi gira a destra (fino al bordo della foto)
    [(120.0, -43.0), (128.0, -43.0), (135.0, -36.0), (135.0, 40.0), (150.0, 40.0)],
    # riga 2, colonna 1: pezzo sotto la linea rossa (va fino al bordo della piattaforma)
    [(8.0, 42.0), (8.0, 49.0), (20.5, 49.0), (20.5, 60.0)],
    # PIATTAFORMA (riga 3, colonne 1-3): cerchio a sinistra, scalini, linea della rampa
    _arco(15.0, 75.0, 6.5, 0, 360, 24),
    [(21.5, 75.0), (34.5, 75.0), (34.5, 79.5), (44.5, 79.5), (44.5, 70.0), (54.0, 70.0), (54.0, 74.5),
     (64.0, 74.5), (64.0, 76.5), (74.5, 76.5)],
    # linea della RAMPA: dal bordo della piattaforma giù fino alla riga 6
    [(74.5, 60.0), (75.0, 120.0), (75.5, 162.0), (75.5, 180.0)],
    # dal fondo del cerchio: giù, curve a S, giù fino all'angolo in basso a sinistra, linea in fondo
    [(15.0, 81.5), (15.0, 95.0)] + _arco(24.0, 96.0, 9.0, 180, 90, 6)[1:] + [(37.5, 105.0)]
    + _arco(37.5, 112.5, 7.5, -90, 0, 6)[1:] + [(45.0, 127.0)] + _arco(37.0, 127.0, 8.0, 0, 90, 6)[1:]
    + [(26.0, 135.0)] + _arco(26.0, 143.0, 8.0, 270, 180, 6)[1:] + [(18.0, 162.0), (18.0, 189.0)]
    + _arco(24.0, 189.0, 6.0, 180, 90, 6)[1:]
    + [(43.0, 195.0), (57.5, 195.0), (67.5, 200.0), (80.0, 192.5), (89.5, 195.0), (110.0, 195.0)],
    # T in fondo a destra (barra con doppio verde: vicolo cieco)
    [(110.0, 187.0), (110.0, 205.5)],
    # seconda S (colonna 2): dal fianco della rampa giù fino alla linea in fondo
    [(59.5, 134.0), (52.0, 134.5), (48.0, 137.0), (46.0, 141.5), (46.0, 180.0), (43.0, 195.0)],
    # incrocio a sinistra (riga 6): tra le due verticali
    [(18.0, 162.0), (46.0, 162.0)],
    # diagonale sotto la piattaforma (colonna 2, riga 4): vicolo cieco alle due estremità
    [(42.0, 90.0), (42.5, 91.5), (51.0, 100.0), (56.0, 105.0), (59.5, 105.3)],
    # semicerchio sul bordo sinistro (colonna 1, righe 4-5: la foto lo taglia)
    [(0.0, 113.0), (8.6, 113.0)] + _arco(8.6, 122.0, 9.0, -90, 90, 10)[1:] + [(0.0, 131.0)],
    # colonna 4, riga 3: barra con doppio verde (vicolo cieco), diagonale verso il bordo destro
    [(95.0, 61.0), (113.0, 61.0)],
    [(104.5, 61.0), (104.5, 65.0), (114.0, 74.5), (120.0, 74.5)],
    # colonna 4: scalini dal fianco della piattaforma, INTERRUZIONE, semicerchio, giù fino alla riga 6
    [(90.5, 75.0), (97.0, 75.0), (97.0, 81.5), (105.0, 81.5), (105.0, 97.0)],
    [(105.0, 113.0), (105.0, 126.0)] + _arco(105.0, 135.5, 9.5, -90, 90, 12)[1:] + [(105.0, 181.0)],
    # riga 6: linea orizzontale con due incroci (dal fianco della rampa al bordo destro)
    [(61.5, 162.0), (120.0, 162.0)],
]


def _verde_q(uc, vc, quad):
    """Quadratino verde 2,5 cm nell'angolo 'quad' (NE, NW, SE, SW) dell'incrocio (uc, vc), coordinate FOTO."""
    du = 1.2 if "E" in quad else -3.7
    dv = -3.7 if "N" in quad else 1.2
    return (uc + du, vc + dv, (uc, vc))


VERDI_FOTO = [
    _verde_q(15.0, 15.0, "SE"),     # falso verde (dopo l'incrocio, andando a destra)
    _verde_q(45.0, 15.0, "SW"),     # andando a destra: verde a destra -> giù
    _verde_q(75.0, 15.0, "NW"),     # incrocio dell'INGRESSO: due verdi sopra la linea
    _verde_q(75.0, 15.0, "NE"),
    _verde_q(104.5, 15.0, "SW"),    # salendo dallo stelo: verde a sinistra -> linea lunga verso sinistra
    _verde_q(135.0, 15.0, "NW"),
    _verde_q(104.5, 37.0, "NW"),    # quadrato arrotondato: in alto
    _verde_q(97.0, 45.0, "NW"),     # quadrato arrotondato: a sinistra
    _verde_q(21.5, 75.0, "SE"),     # piattaforma: cerchio, uscita a destra
    _verde_q(15.0, 81.5, "SE"),     # piattaforma: cerchio, uscita in basso
    _verde_q(74.5, 76.5, "SW"),     # piattaforma: incrocio con la linea della rampa
    _verde_q(104.5, 61.0, "SW"),    # barra con doppio verde
    _verde_q(104.5, 61.0, "SE"),
    _verde_q(75.5, 162.0, "NE"),    # riga 6, incrocio della rampa
    _verde_q(75.5, 162.0, "SW"),
    _verde_q(105.0, 162.0, "NW"),   # riga 6, incrocio a destra
    _verde_q(105.0, 162.0, "SE"),
    _verde_q(18.0, 162.0, "NE"),    # riga 6, incrocio a sinistra
    _verde_q(46.0, 162.0, "NW"),
    _verde_q(110.0, 195.0, "NW"),   # T in fondo: doppio verde prima della barra
    _verde_q(110.0, 195.0, "SW"),
]

# tubi bianchi sulla pista (dossi), rettangoli FOTO (u0, v0, u1, v1)
DOSSI_FOTO = [
    (29.0, 1.0, 31.0, 29.0),        # riga 1: tubo sul bordo tra colonna 1 e 2
    (38.0, 66.0, 40.0, 88.0),       # piattaforma: tubo sulla linea a scalini
    (66.0, 99.0, 84.0, 101.0),      # rampa: 4 tubi di traverso
    (66.0, 105.0, 84.0, 107.0),
    (66.0, 110.0, 84.0, 112.0),
    (66.0, 134.5, 84.0, 136.5),
    (27.0, 131.0, 29.0, 138.0),     # curve a S: due tubi
    (33.0, 131.0, 35.0, 138.0),
    (68.0, 190.0, 72.0, 203.0),     # zig-zag in fondo: tubo di traverso
]

PARETE_DESTRA_FOTO = (123.5, 55.0)                 # [Sim V30] parete a u = 123,5 cm, da v = 55 fino in fondo
ROSSO_FOTO = (124.0, -14.0, 146.0, -11.5)            # [Sim V31] linea rossa d'arrivo: dopo l'uscita, colonna accanto all'arena (STIMA)
RAMPA_FOTO = (60.0, 90.0, 90.0, 150.0)               # le 2 piastrelle con i tubi, in salita verso la piattaforma
INTERRUZIONE_FOTO = (104.0, 97.0, 106.0, 113.0)      # interruzione della linea (colonna 4, riga 4)

# porte (coordinate FOTO)
INGRESSO_U = (61.5, 88.5)    # striscia ARGENTO sul muro in comune, colonna 3 (u da..a)
USCITA_PROF = (29.5, 56.5)   # [Sim V31] striscia NERA sul lato corto dell'arena: profondità dal muro in comune (da..a)

PARTENZE = {
    # sulla linea lunga in alto a sinistra, verso destra (percorso fino all'arena e alla linea rossa)
    "scuola": (6.0, 15.0, 90.0),
    # in fondo alla linea della rampa, verso l'alto (rampa con i tubi, piattaforma, cerchio, curve a S...)
    "scuola_rampa": (75.5, 176.0, 0.0),
    # sulla verticale di sinistra in basso, verso il basso (angolo, zig-zag, T con doppio verde)
    "scuola_basso": (18.0, 172.0, 180.0),
    # [Sim V30] dopo l'interruzione della colonna 4, verso il basso: semicerchio accanto alla parete destra
    "scuola_parete": (105.0, 116.0, 180.0),
}


# ------------------------------------------------------------------------------------------------
#  DA FOTO A SIMULATORE (giro di 90 gradi in senso orario: l'alto della foto diventa la destra)
# ------------------------------------------------------------------------------------------------
def _p(u, v):
    return (L_PISTA - v, u)


def _rett(u0, v0, u1, v1):
    x0, y0 = _p(u0, v1)
    x1, y1 = _p(u1, v0)
    return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


def crea_campo_scuola(partenza="scuola"):
    AX = L_PISTA                        # muro sinistro dell'arena (il muro in comune)
    X2 = AX + A_PROF
    LARG = 150                          # 4 colonne + la colonna accanto all'arena
    C = {"larghezza": int(X2), "altezza": LARG, "piastrella": 30}
    C["linee"] = [[_p(u, v) for (u, v) in L] for L in LINEE_FOTO]
    C["verdi"] = []
    for i, (u, v, inc) in enumerate(VERDI_FOTO):
        r = _rett(u, v, u + 2.5, v + 2.5)
        r.update(id=f"V{i}", incrocio=_p(*inc))
        C["verdi"].append(r)
    C["dossi"] = []
    for (u0, v0, u1, v1) in DOSSI_FOTO:
        r = _rett(u0, v0, u1, v1)
        C["dossi"].append((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))
    C["detriti"] = []
    C["rosso"] = _rett(*ROSSO_FOTO)
    r = C["rosso"]
    gi = _rett(*INTERRUZIONE_FOTO)
    yi0, yi1 = INGRESSO_U
    H = A_LUNGO
    xu0, xu1 = AX + USCITA_PROF[0], AX + USCITA_PROF[1]      # [Sim V31] uscita sul muro BASSO del simulatore
    C["argento"] = {"x": AX, "y": yi0 + 1.0, "w": 2.5, "h": yi1 - yi0 - 2.0}
    C["nero_uscita"] = {"x": xu0 + 1.0, "y": H - 2.5, "w": xu1 - xu0 - 2.0, "h": 2.5}
    a = C["argento"]
    C["elementi"] = [
        {"tipo": "In", "poli": [(a["x"], a["y"]), (a["x"] + a["w"], a["y"]), (a["x"] + a["w"], a["y"] + a["h"]), (a["x"], a["y"] + a["h"])]},
        {"tipo": "Ro", "poli": [(r["x"], r["y"]), (r["x"] + r["w"], r["y"]), (r["x"] + r["w"], r["y"] + r["h"]), (r["x"], r["y"] + r["h"])]},
        {"tipo": "Di", "poli": [(gi["x"], gi["y"]), (gi["x"] + gi["w"], gi["y"]), (gi["x"] + gi["w"], gi["y"] + gi["h"]), (gi["x"], gi["y"] + gi["h"])]},
    ]
    # rampa (il simulatore a linee libere ne ha una): sale verso la piattaforma = verso est nel simulatore
    rp = _rett(*RAMPA_FOTO)
    C["rampa"] = {"x": int(rp["x"]), "y": int(rp["y"]), "w": int(rp["w"]), "h": int(rp["h"]), "pendenza": 12, "salita_verso": 90}
    C["ostacolo"] = {"x": -500, "y": -500, "w": 1, "h": 1}     # nessun ostacolo di legno su questa pista
    # [Sim V31] arena: ingresso sul muro SINISTRO (in comune con la pista), uscita sul muro BASSO (lato corto)
    C["arena"] = {"x": AX, "y": 0, "w": A_PROF, "h": H, "ingresso": (yi0, yi1), "uscita": (xu0, xu1)}
    C["muri"] = [((AX, 0), (X2, 0)), ((X2, 0), (X2, H)),
                 ((AX, H), (xu0, H)), ((xu1, H), (X2, H)),
                 ((AX, 0), (AX, yi0)), ((AX, yi1), (AX, H))]
    # [Sim V30] parete lungo il bordo destro della pista (foto: dopo il bordo in legno c'è il muro bianco)
    a0, _ = _p(0, PARETE_DESTRA_FOTO[1])
    C["muri"].append(((0.0, PARETE_DESTRA_FOTO[0]), (a0, PARETE_DESTRA_FOTO[0])))
    C["triangoli"] = [
        # [Sim V31] foto dall'alto del 05/11: ROSSO tra muro in comune e lato dell'uscita, VERDE nell'angolo opposto
        {"colore": "verde", "classe": 3, "poli": [(X2, 0), (X2 - 30, 0), (X2, 30)]},
        {"colore": "rosso", "classe": 2, "poli": [(AX, H), (AX + 30, H), (AX, H - 30)]},
    ]
    C["palline"] = [
        {"id": "N1", "tipo": "nera", "x": AX + 20.0, "y": 55.0},        # [Sim V31] posizioni di prova (nella foto
        {"id": "A1", "tipo": "argento", "x": AX + 35.0, "y": 30.0},     # le palline erano già negli angoli)
        {"id": "A2", "tipo": "argento", "x": AX + 65.0, "y": 75.0},
    ]
    C["raggio_pallina"] = 2.25
    C["linea_arena_y"] = (yi0 + yi1) / 2
    C["traguardi"] = []          # pista con tanti esercizi: niente traguardi automatici (si guarda il replay)
    C["etichette"] = [
        ["INGRESSO", AX - 3, yi0 - 3, "right"], ["USCITA", (xu0 + xu1) / 2, H + 8, "center"],
        ["ARRIVO", r["x"] - 2, r["y"] + r["h"] / 2 + 3, "right"], ["RAMPA (stima 12°)", rp["x"] + rp["w"] / 2, rp["y"] + 4, "center"],
        ["PIATTAFORMA", _p(45, 75)[0], 4, "center"], ["ZONA DI EVACUAZIONE 120 x 90 (foto 05/11)", AX + 45, 60, "center"],
        ["INTERRUZIONE", gi["x"], gi["y"] - 3, "center"],
    ]
    u, v, h = PARTENZE.get(partenza, PARTENZE["scuola"])
    x, y = _p(u, v)
    C["partenza"] = {"x": x, "y": y, "heading": float((h + 90) % 360)}
    return C
