"""
PIASTRELLE DEL RESCUE LINE (regolamento RCJ 2026) e costruttore del campo a piastrelle.

Ogni piastrella è un quadrato di 30 x 30 cm. Qui sono disegnate "in locale": il robot entra
sempre dal lato BASSO (punto 15,30) andando verso l'ALTO (nord). Il costruttore poi le ruota
nella direzione giusta e le mette in fila una dopo l'altra, come si fa montando il campo vero.

Tipi di piastrella (geometria della linea):
  dritto, curva_dx/sx (raggio 15), curva_stretta_dx/sx (raggio 7,5), angolo_dx/sx (90° secco),
  acuto_dx/sx (angolo acuto ~60°), zigzag, onda, interruzione (gap fino a 20 cm), dossi,
  detriti, ostacolo, incrocio (T o +, con tutti i casi di verdi: dx, sx, doppio = vicolo cieco,
  nessuno = dritto, verde DOPO l'incrocio = falso verde), altalena, partenza, arrivo (striscia rossa).
Superficie (si può combinare con quasi tutte): piana, rampa (pendenza in gradi, + sale, - scende),
  inclinata di lato (banca, in gradi), altalena.

Punti del regolamento 2026 per piastrella superata: interruzione 10, dossi 10, incrocio o vicolo
cieco 10, rampa 10, ostacolo 20, altalena 20. Checkpoint: 5/3/1/0 punti per piastrella.
"""
import math
import random

T = 30.0            # lato della piastrella (cm)
LW = 1.8            # larghezza del nastro nero

PUNTI_OSTACOLO = {"interruzione": 10, "dossi": 10, "incrocio": 10, "rampa": 10, "ostacolo": 20, "altalena": 20}


def arco(cx, cy, r, a0, a1, passi=16):
    """Arco (angoli in gradi, convenzione schermo: 0 = destra, 90 = basso)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / passi)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / passi))) for i in range(passi + 1)]


def _specchia(pts):
    return [(T - x, y) for x, y in pts]


# ----------------------------------------------------------------------------------------------
#  GEOMETRIE IN LOCALE  (ritornano un dizionario: linee, verdi, elementi, uscita, ...)
# ----------------------------------------------------------------------------------------------
def g_dritto(o):
    return {"linee": [[(15, 30), (15, 0)]], "uscita": "N"}


def g_curva(o, verso, r=15.0):
    if r >= 15:
        pts = arco(30, 30, 15, 180, 270)
    else:
        pts = [(15, 30), (15, 15 + r)] + arco(15 + r, 15 + r, r, 180, 270)[1:] + [(30, 15)]
    if verso == "sx":
        pts = _specchia(pts)
    return {"linee": [pts], "uscita": "E" if verso == "dx" else "W"}


def g_angolo(o, verso):
    pts = [(15, 30), (15, 15), (30, 15)]
    if verso == "sx":
        pts = _specchia(pts)
    return {"linee": [pts], "uscita": "E" if verso == "dx" else "W"}


def g_acuto(o, verso):
    # sale fin quasi al bordo e torna indietro verso il lato: angolo interno di circa 60°
    pts = [(15, 30), (15, 5), (30, 15)]
    if verso == "sx":
        pts = _specchia(pts)
    return {"linee": [pts], "uscita": "E" if verso == "dx" else "W"}


def g_zigzag(o):
    a = o.get("ampiezza", 5)
    pts = [(15, 30), (15, 26), (15 - a, 21), (15 + a, 15), (15 - a, 9), (15, 4), (15, 0)]
    return {"linee": [pts], "uscita": "N"}


def g_onda(o):
    a = o.get("ampiezza", 5)
    pts = [(15 + a * math.sin(2 * math.pi * (30 - y) / 30), y) for y in [30 - i * 1.5 for i in range(21)]]
    return {"linee": [pts], "uscita": "N"}


def g_interruzione(o):
    L = o.get("lunghezza", 14)         # max 20 cm, con almeno 5 cm di linea dritta prima
    y0, y1 = 15 + L / 2, 15 - L / 2
    return {"linee": [[(15, 30), (15, y0)], [(15, y1), (15, 0)]], "uscita": "N",
            # il modello "Di" riconosce la FINE della linea con il bianco dopo: il riquadro copre
            # l'ultimo centimetro di nastro e i primi 7 cm di vuoto (anche se il gap è più lungo)
            "elementi": [{"tipo": "Di", "poli": [(14, y0 - 7), (16, y0 - 7), (16, y0 + 1), (14, y0 + 1)]}],
            "ostacolo_punti": "interruzione"}


def g_tratteggiata(o):
    # linea tratteggiata: tre pezzi da 5-7 cm e due vuoti da 6 cm (ogni vuoto ha prima almeno 5 cm di linea dritta)
    pezzi = [(30, 23), (17, 11), (5, 0)]
    elementi = []
    for (a, b), (c, _) in zip(pezzi[:-1], pezzi[1:]):
        elementi.append({"tipo": "Di", "poli": [(14, b - 7), (16, b - 7), (16, b + 1), (14, b + 1)]})
    return {"linee": [[(15, a), (15, b)] for a, b in pezzi], "uscita": "N", "elementi": elementi,
            "ostacolo_punti": "interruzione"}


def g_dossi(o):
    n = o.get("quanti", 1)
    ys = [15] if n == 1 else [9, 21]
    return {"linee": [[(15, 30), (15, 0)]], "uscita": "N",
            "dossi": [(1.0, y - 2.0, 29.0, y + 2.0) for y in ys], "ostacolo_punti": "dossi"}


def g_detriti(o):
    base = g_curva(o, o["curva"]) if o.get("curva") else g_dritto(o)
    rnd = random.Random(o.get("seme", 7))
    stecchini = []
    for _ in range(o.get("quanti", 9)):
        cx, cy = rnd.uniform(6, 24), rnd.uniform(4, 26)
        a = rnd.uniform(0, math.pi)
        L = rnd.uniform(4.5, 6.5)                 # stuzzicadenti (alti meno di 3 mm)
        stecchini.append(((cx - L / 2 * math.cos(a), cy - L / 2 * math.sin(a)),
                          (cx + L / 2 * math.cos(a), cy + L / 2 * math.sin(a))))
    base["detriti"] = stecchini
    return base


def g_ostacolo(o):
    w, h = o.get("dim", (10, 10))
    return {"linee": [[(15, 30), (15, 0)]], "uscita": "N",
            "ostacoli": [(15 - w / 2, 15 - h / 2, 15 + w / 2, 15 + h / 2)], "ostacolo_punti": "ostacolo",
            "tolleranza": True}


def g_incrocio(o):
    """o['forma']: 'T' (rami E e W, niente N), '+' (N, E, W), 'Tdx' (N ed E), 'Tsx' (N e W).
       o['verdi']: 'dx', 'sx', 'doppio', '' (nessuno), 'falso_dx', 'falso_sx' (verde DOPO l'incrocio),
       [V28] 'diagonale_dx' / 'diagonale_sx': due verdi in DIAGONALE, uno valido (prima, a destra / a sinistra)
       e uno falso dall'altra parte dopo l'incrocio, come la piastrella della foto del 29/10."""
    forma = o.get("forma", "+")
    rami = {"T": "EW", "+": "NEW", "Tdx": "NE", "Tsx": "NW"}[forma]
    linee = [[(15, 30), (15, 15)]]
    if "N" in rami:
        linee.append([(15, 15), (15, 0)])
    if "E" in rami:
        linee.append([(15, 15), (30, 15)])
    if "W" in rami:
        linee.append([(15, 15), (0, 15)])
    verdi = []
    v = o.get("verdi", "")
    prima_y = 15 + LW / 2 + 0.3                   # subito PRIMA della linea trasversale
    dopo_y = 15 - LW / 2 - 0.3 - 2.5              # subito DOPO: falso verde
    xs = 15 - LW / 2 - 0.4 - 2.5                  # a sinistra della linea
    xd = 15 + LW / 2 + 0.4                        # a destra
    if v in ("sx", "doppio"):
        verdi.append((xs, prima_y))
    if v in ("dx", "doppio"):
        verdi.append((xd, prima_y))
    if v == "falso_sx":
        verdi.append((xs, dopo_y))
    if v == "falso_dx":
        verdi.append((xd, dopo_y))
    if v == "diagonale_dx":                       # [V28] valido a destra, falso a sinistra dopo l'incrocio
        verdi += [(xd, prima_y), (xs, dopo_y)]
    if v == "diagonale_sx":                       # [V28] valido a sinistra, falso a destra dopo l'incrocio
        verdi += [(xs, prima_y), (xd, dopo_y)]
    if v in ("dx", "diagonale_dx"):
        uscita = "E"
    elif v in ("sx", "diagonale_sx"):
        uscita = "W"
    elif v == "doppio":
        uscita = "S"                              # vicolo cieco: dietrofront
    else:
        uscita = "N"
    assert uscita in rami or uscita == "S", f"incrocio {forma} senza ramo {uscita}"
    return {"linee": linee, "uscita": uscita, "verdi": verdi, "rami": [r for r in rami if r != uscita],
            "ostacolo_punti": "incrocio"}


def g_partenza(o):
    return {"linee": [[(15, 30), (15, 0)]], "uscita": "N"}


def g_arrivo(o):
    return {"linee": [[(15, 30), (15, 15)]], "uscita": None,
            "rosso": (0.0, 13.75, 30.0, 16.25),
            "elementi": [{"tipo": "Ro", "poli": [(2.5, 13.75), (27.5, 13.75), (27.5, 16.25), (2.5, 16.25)]}]}


GEOMETRIE = {
    "dritto": g_dritto, "partenza": g_partenza, "arrivo": g_arrivo,
    "curva_dx": lambda o: g_curva(o, "dx"), "curva_sx": lambda o: g_curva(o, "sx"),
    "curva_stretta_dx": lambda o: g_curva(o, "dx", 7.5), "curva_stretta_sx": lambda o: g_curva(o, "sx", 7.5),
    "angolo_dx": lambda o: g_angolo(o, "dx"), "angolo_sx": lambda o: g_angolo(o, "sx"),
    "acuto_dx": lambda o: g_acuto(o, "dx"), "acuto_sx": lambda o: g_acuto(o, "sx"),
    "zigzag": g_zigzag, "onda": g_onda, "interruzione": g_interruzione, "dossi": g_dossi,
    "detriti": g_detriti, "ostacolo": g_ostacolo, "tratteggiata": g_tratteggiata, "incrocio": g_incrocio, "altalena": g_dritto,
}

NOMI = {
    "dritto": "rettilineo", "partenza": "partenza", "arrivo": "arrivo (striscia rossa)",
    "curva_dx": "curva a destra", "curva_sx": "curva a sinistra",
    "curva_stretta_dx": "curva stretta a destra", "curva_stretta_sx": "curva stretta a sinistra",
    "angolo_dx": "angolo retto a destra", "angolo_sx": "angolo retto a sinistra",
    "acuto_dx": "angolo acuto a destra", "acuto_sx": "angolo acuto a sinistra",
    "zigzag": "zig-zag", "onda": "onda", "interruzione": "interruzione (gap)", "dossi": "dossi",
    "tratteggiata": "linea tratteggiata (2 interruzioni)",
    "detriti": "detriti (stuzzicadenti)", "ostacolo": "ostacolo", "incrocio": "incrocio", "altalena": "altalena",
}

# ----------------------------------------------------------------------------------------------
#  ROTAZIONI
# ----------------------------------------------------------------------------------------------
LATI = {"N": 0, "E": 90, "S": 180, "W": 270}
PASSO = {0: (0, -1), 90: (1, 0), 180: (0, 1), 270: (-1, 0)}


def ruota(p, h, cella):
    """Punto locale (entrata in basso, verso nord) -> punto del campo per una piastrella percorsa con direzione h."""
    x, y = p[0] - 15, p[1] - 15
    for _ in range((h // 90) % 4):
        x, y = -y, x                      # rotazione oraria di 90° (asse y verso il basso)
    return (cella[0] * T + 15 + x, cella[1] * T + 15 + y)


def ruota_rett(r, h, cella):
    pts = [ruota((r[0], r[1]), h, cella), ruota((r[2], r[3]), h, cella)]
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


# ----------------------------------------------------------------------------------------------
#  COSTRUTTORE
# ----------------------------------------------------------------------------------------------
class Costruttore:
    def __init__(self, colonne, righe):
        self.nc, self.nr = colonne, righe
        self.C = {"larghezza": int(colonne * T), "altezza": int(righe * T), "piastrella": T,
                  "linee": [], "verdi": [], "elementi": [], "dossi": [], "detriti": [], "ostacoli": [],
                  "quote": {}, "percorso": [], "etichette": [], "altalene": [], "celle_linea": {},
                  "tolleranza": {}}
        self.cella = None
        self.h = 0
        self.z = 0.0
        self.occupate = {}
        self.rami_in_sospeso = []

    def inizia(self, c, r, h):
        self.cella, self.h = (c, r), h

    def _quota(self, cella, sup):
        cx, cy = cella[0] * T + 15, cella[1] * T + 15
        dx, dy = PASSO[self.h]
        tipo = sup.get("tipo", "piana")
        if tipo == "rampa":
            dz = T * math.tan(math.radians(sup["pendenza"]))
            s = dz / T
            q = {"z": self.z + dz / 2, "sx": dx * s, "sy": dy * s, "tipo": "rampa", "pendenza": sup["pendenza"]}
            self.z += dz
        elif tipo == "banca":
            s = math.tan(math.radians(sup["banca"]))
            rx, ry = -dy, dx                  # destra della direzione di marcia
            q = {"z": self.z, "sx": rx * s, "sy": ry * s, "tipo": "banca", "banca": sup["banca"]}
        elif tipo == "altalena":
            A = sup.get("angolo", 15)
            hc = 15 * math.tan(math.radians(A))
            q = {"z": self.z + hc, "sx": 0.0, "sy": 0.0, "tipo": "altalena", "angolo": A,
                 "asse": (dx, dy), "base": self.z}
        else:
            q = {"z": self.z, "sx": 0.0, "sy": 0.0, "tipo": "piana"}
        q["cx"], q["cy"] = cx, cy
        return q

    def metti(self, tipo, **o):
        """Mette una piastrella nella cella corrente e passa alla cella successiva."""
        c = self.cella
        assert 0 <= c[0] < self.nc and 0 <= c[1] < self.nr, f"{tipo}: cella {c} fuori dal campo"
        ripasso = c in self.occupate
        g = GEOMETRIE[tipo](o)
        h = self.h
        C = self.C
        sup = {"tipo": "piana"}
        if "pendenza" in o:
            sup = {"tipo": "rampa", "pendenza": o["pendenza"]}
        elif "banca" in o:
            sup = {"tipo": "banca", "banca": o["banca"]}
        elif tipo == "altalena":
            sup = {"tipo": "altalena", "angolo": o.get("angolo", 15)}
        z_in = self.z
        if not ripasso:
            q = self._quota(c, sup)
            C["quote"][c] = q
            if sup["tipo"] == "altalena":
                C["altalene"].append({"cella": c, "asse": q["asse"], "angolo": q["angolo"], "base": q["base"]})
            for L in g["linee"]:
                C["linee"].append([ruota(p, h, c) for p in L])
            for (vx, vy) in g.get("verdi", []):
                a = ruota((vx, vy), h, c)
                b = ruota((vx + 2.5, vy + 2.5), h, c)
                C["verdi"].append({"x": min(a[0], b[0]), "y": min(a[1], b[1]), "w": 2.5, "h": 2.5,
                                   "id": f"V{len(C['verdi'])}", "incrocio": ruota((15, 15), h, c)})
            for el in g.get("elementi", []):
                C["elementi"].append({"tipo": el["tipo"], "poli": [ruota(p, h, c) for p in el["poli"]]})
            for r in g.get("dossi", []):
                C["dossi"].append(ruota_rett(r, h, c))
            for a, b in g.get("detriti", []):
                C["detriti"].append((ruota(a, h, c), ruota(b, h, c)))
            for r in g.get("ostacoli", []):
                C["ostacoli"].append(ruota_rett(r, h, c))
            if "rosso" in g:
                x0, y0, x1, y1 = ruota_rett(g["rosso"], h, c)
                C["rosso"] = {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}
            C["celle_linea"][c] = "percorso"
            for ramo in g.get("rami", []):
                hr = (h + LATI[ramo]) % 360
                self._ramo((c[0] + PASSO[hr][0], c[1] + PASSO[hr][1]), hr)
            if g.get("tolleranza"):
                dx, dy = PASSO[h]
                for k in (-1, 1):
                    for f in (-1, 0, 1):
                        C["tolleranza"][(c[0] - dy * k + dx * f, c[1] + dx * k + dy * f)] = len(C["percorso"])
        else:
            q = C["quote"][c]
            self.z = z_in
        punti = PUNTI_OSTACOLO.get(g.get("ostacolo_punti"), 0)
        if sup["tipo"] in ("rampa", "banca") and not punti:
            punti = PUNTI_OSTACOLO["rampa"]
        if sup["tipo"] == "altalena":
            punti = PUNTI_OSTACOLO["altalena"]
        nome = NOMI.get(tipo, tipo)
        if tipo == "incrocio":
            v = o.get("verdi", "")
            nome = {"dx": "incrocio: verde a destra", "sx": "incrocio: verde a sinistra",
                    "doppio": "vicolo cieco (doppio verde)", "": "incrocio senza verde: dritto",
                    "falso_dx": "incrocio con FALSO verde (dopo): dritto",
                    "falso_sx": "incrocio con FALSO verde (dopo): dritto",
                    "diagonale_dx": "incrocio con verdi in diagonale: a destra",
                    "diagonale_sx": "incrocio con verdi in diagonale: a sinistra"}[v]
        if sup["tipo"] == "rampa":
            nome += f" su rampa {'in salita' if sup['pendenza'] > 0 else 'in discesa'} {abs(sup['pendenza'])}°"
        if sup["tipo"] == "banca":
            nome += f" inclinato di lato {sup['banca']}°"
        C["percorso"].append({"cella": c, "h": h, "tipo": tipo, "nome": nome, "punti": punti,
                              "cp": bool(o.get("cp")), "z": round(z_in, 1)})
        self.occupate.setdefault(c, []).append(len(C["percorso"]) - 1)
        if o.get("etichetta"):
            C["etichette"].append([o["etichetta"], c[0] * T + 15, c[1] * T + 4, "center"])
        u = g["uscita"]
        if u is None:
            return
        self.h = (h + LATI[u]) % 360
        if u == "S":
            self.h = (h + 180) % 360
        dx, dy = PASSO[self.h]
        self.cella = (c[0] + dx, c[1] + dy)

    def _ramo(self, cella, h):
        """Ramo sbagliato di un incrocio: la linea prosegue nella piastrella vicina (se è vuota)."""
        # si disegna alla fine (in fine()), solo se nel frattempo la cella non è diventata percorso
        self.rami_in_sospeso.append((cella, h))

    def arena(self, sopra=1, uscita_col=1, palline=None, righe=3, uscita_lato="basso", uscita_riga=None):
        """Zona di evacuazione 4 x 'righe' piastrelle. Il robot arriva andando verso EST: l'ingresso è sul
        muro sinistro, all'altezza della linea; 'sopra' = righe dell'arena sopra quella dell'ingresso.
        uscita_lato="basso": l'uscita è sul muro BASSO, nella colonna 'uscita_col' (0..3) dell'arena.
        [V26] uscita_lato="sinistro": l'uscita è sullo STESSO muro dell'ingresso (come nell'arena della
        scuola), nella riga 'uscita_riga' (0 = la più alta) dell'arena; il robot esce verso OVEST."""
        assert self.h == 90, "l'arena si entra andando verso est"
        c, r = self.cella
        AX, AY = c * T, (r - sopra) * T
        YL = r * T + 15
        X2, Y2 = AX + 120, AY + righe * T
        C = self.C
        if uscita_lato == "sinistro":
            assert uscita_riga is not None and uscita_riga != sopra, "l'uscita deve essere su un'altra riga"
            yu = AY + uscita_riga * T + 15
            C["arena"] = {"x": AX, "y": AY, "w": 120, "h": righe * T, "ingresso": (YL - 13.5, YL + 13.5),
                          "uscita": (yu - 13.5, yu + 13.5), "uscita_muro": "sinistro"}
            aperture = sorted([C["arena"]["ingresso"], C["arena"]["uscita"]])
            C["muri"] = [((AX, AY), (X2, AY)), ((X2, AY), (X2, Y2)), ((AX, Y2), (X2, Y2)),
                         ((AX, AY), (AX, aperture[0][0])), ((AX, aperture[0][1]), (AX, aperture[1][0])),
                         ((AX, aperture[1][1]), (AX, Y2))]
        else:
            xu = AX + uscita_col * T + 15
            C["arena"] = {"x": AX, "y": AY, "w": 120, "h": righe * T, "ingresso": (YL - 13.5, YL + 13.5),
                          "uscita": (xu - 13.5, xu + 13.5)}
            yi0, yi1 = C["arena"]["ingresso"]
            xu0, xu1 = C["arena"]["uscita"]
            C["muri"] = [((AX, AY), (X2, AY)), ((X2, AY), (X2, Y2)),
                         ((AX, AY), (AX, yi0)), ((AX, yi1), (AX, Y2)),
                         ((AX, Y2), (xu0, Y2)), ((xu1, Y2), (X2, Y2))]
        C["triangoli"] = [
            {"colore": "verde", "classe": 3, "poli": [(X2, AY), (X2 - 30, AY), (X2, AY + 30)]},
            {"colore": "rosso", "classe": 2, "poli": [(X2, Y2), (X2 - 30, Y2), (X2, Y2 - 30)]},
        ]
        C["palline"] = palline or [
            {"id": "A1", "tipo": "argento", "x": AX + 55.0, "y": AY + 22.0},
            {"id": "A2", "tipo": "argento", "x": AX + 85.0, "y": AY + 60.0},
            {"id": "N1", "tipo": "nera", "x": AX + 30.0, "y": AY + 70.0},
        ] if righe == 3 else [
            {"id": "A1", "tipo": "argento", "x": AX + 60.0, "y": AY + 25.0},
            {"id": "A2", "tipo": "argento", "x": AX + 85.0, "y": AY + 80.0},
            {"id": "N1", "tipo": "nera", "x": AX + 40.0, "y": AY + 95.0},
        ]
        C["raggio_pallina"] = 2.25
        C["argento"] = {"x": AX, "y": YL - 12.5, "w": 2.5, "h": 25.0}
        C["elementi"].append({"tipo": "In", "poli": [(AX, YL - 12.5), (AX + 2.5, YL - 12.5), (AX + 2.5, YL + 12.5), (AX, YL + 12.5)]})
        if uscita_lato == "sinistro":
            C["nero_uscita"] = {"x": AX, "y": yu - 12.5, "w": 2.5, "h": 25.0}
        else:
            C["nero_uscita"] = {"x": xu - 12.5, "y": Y2 - 2.5, "w": 25.0, "h": 2.5}
        C["linea_arena_y"] = YL
        for i in range(4):
            for j in range(righe):
                cella = (c + i, r - sopra + j)
                assert cella not in self.occupate, f"l'arena copre la cella {cella} già usata"
                self.C["celle_linea"][cella] = "arena"
                self.C["quote"][cella] = {"z": self.z, "sx": 0.0, "sy": 0.0, "tipo": "piana",
                                          "cx": cella[0] * T + 15, "cy": cella[1] * T + 15}
                self.occupate[cella] = []
        C["percorso"].append({"cella": (c, r), "h": 90, "tipo": "arena", "nome": "zona di evacuazione",
                              "punti": 0, "cp": False, "z": round(self.z, 1)})
        C["etichette"].append(["ZONA DI EVACUAZIONE", AX + 60, AY + 45, "center"])
        if uscita_lato == "sinistro":
            # [V26] si riparte a sinistra della porta d'uscita, verso ovest
            self.cella = (c - 1, r - sopra + uscita_riga)
            self.h = 270
        else:
            # si riparte sotto la porta d'uscita, verso sud
            self.cella = (c + uscita_col, r - sopra + righe)
            self.h = 180
        return C["arena"]

    def fine(self, partenza_cella, partenza_h):
        C = self.C
        for cella, h in self.rami_in_sospeso:
            if cella in self.occupate or cella in C["celle_linea"] or not (0 <= cella[0] < self.nc and 0 <= cella[1] < self.nr):
                continue
            C["linee"].append([ruota((15, 30), h, cella), ruota((15, 8), h, cella)])
            C["celle_linea"][cella] = "ramo"
        # le celle senza piastrella di percorso sono piane alla quota del pavimento
        for i in range(self.nc):
            for j in range(self.nr):
                if (i, j) not in C["quote"]:
                    C["quote"][(i, j)] = {"z": 0.0, "sx": 0.0, "sy": 0.0, "tipo": "piana", "cx": i * T + 15, "cy": j * T + 15}
        c = partenza_cella
        dx, dy = PASSO[partenza_h]
        C["partenza"] = {"x": c[0] * T + 15 - dx * 4.0, "y": c[1] * T + 15 - dy * 4.0, "heading": float(partenza_h)}
        return C


def catalogo():
    """Tutte le piastrelle, in locale, per la pagina del simulatore."""
    voci = [
        ("partenza", {}, "Partenza (checkpoint)"), ("dritto", {}, "Rettilineo"),
        ("curva_dx", {}, "Curva (raggio 15 cm)"), ("curva_stretta_dx", {}, "Curva stretta (7,5 cm)"),
        ("angolo_dx", {}, "Angolo retto"), ("acuto_dx", {}, "Angolo acuto"),
        ("zigzag", {}, "Zig-zag"), ("onda", {}, "Onda"),
        ("interruzione", {"lunghezza": 14}, "Interruzione 14 cm"), ("interruzione", {"lunghezza": 20}, "Interruzione 20 cm (max)"),
        ("tratteggiata", {}, "Linea tratteggiata"),
        ("dossi", {"quanti": 1}, "Dosso (alto ≤ 1 cm)"), ("dossi", {"quanti": 2}, "Due dossi"),
        ("detriti", {}, "Detriti (≤ 3 mm)"), ("detriti", {"curva": "dx", "seme": 3}, "Detriti in curva"),
        ("ostacolo", {}, "Ostacolo (alto ≥ 15 cm)"),
        ("incrocio", {"forma": "T", "verdi": "sx"}, "Incrocio a T: verde a sinistra"),
        ("incrocio", {"forma": "+", "verdi": "dx"}, "Incrocio +: verde a destra"),
        ("incrocio", {"forma": "+", "verdi": ""}, "Incrocio senza verde: dritto"),
        ("incrocio", {"forma": "T", "verdi": "doppio"}, "Vicolo cieco: dietrofront"),
        ("incrocio", {"forma": "+", "verdi": "falso_dx"}, "Falso verde (dopo l'incrocio)"),
        ("incrocio", {"forma": "Tdx", "verdi": ""}, "Ramo laterale senza verde"),
        ("dritto", {"pendenza": 20}, "Rampa in salita (≤ 25°)"), ("dritto", {"pendenza": -20}, "Rampa in discesa"),
        ("onda", {"pendenza": 20}, "Onda su rampa"), ("dritto", {"banca": 10}, "Inclinata di lato"),
        ("altalena", {}, "Altalena (< 20°)"), ("arrivo", {}, "Arrivo (striscia rossa)"),
    ]
    out = []
    for tipo, o, nome in voci:
        g = GEOMETRIE[tipo](o)
        sup = "rampa" if "pendenza" in o else ("banca" if "banca" in o else ("altalena" if tipo == "altalena" else "piana"))
        punti = PUNTI_OSTACOLO.get(g.get("ostacolo_punti"), 0)
        if sup in ("rampa", "banca") and not punti:
            punti = 10
        if sup == "altalena":
            punti = 20
        out.append({"nome": nome, "linee": g["linee"], "verdi": g.get("verdi", []), "dossi": g.get("dossi", []),
                    "detriti": g.get("detriti", []), "ostacoli": g.get("ostacoli", []), "rosso": g.get("rosso"),
                    "superficie": sup, "pendenza": o.get("pendenza", 0), "punti": punti})
    return out
