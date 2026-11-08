"""
CAMPO DI GARA SIMULATO - RoboCup Junior Rescue Line
Unità: centimetri. Origine in alto a sinistra, x verso destra, y verso il basso.
Direzione (heading) come una bussola: 0 = verso l'alto, 90 = verso destra (senso orario).
Piastrelle da 30 cm: campo 15 x 9 piastrelle.

Percorso:
  partenza -> INCROCIO 0 con FALSO VERDE -> RAMPA -> curva -> INCROCIO 1 con FALSO VERDE (dopo l'incrocio: si va dritti)
  -> INCROCIO 2 con DOPPIO VERDE (dietrofront) -> di nuovo all'INCROCIO 1, dove ora lo stesso
  verde è PRIMA dell'incrocio, a destra -> svolta a destra -> INTERRUZIONE -> curva
  -> CURVE A ONDA -> OSTACOLO -> ARENA (2 argento + 1 nera) -> USCITA
  -> INCROCIO 3 con verde a sinistra -> LINEA ROSSA

Regola dei verdi (regolamento RCJ): un verde conta solo se il robot lo incontra PRIMA
dell'incrocio. Un verde dopo l'incrocio è un "falso verde" e va ignorato.
"""
import math

LARGHEZZA_LINEA = 1.8       # nastro nero (1-2 cm da regolamento)


def arco(cx, cy, r, a0, a1, passi=24):
    """Punti di un arco (angoli in gradi, convenzione schermo: 0 = destra, 90 = basso)."""
    pts = []
    for i in range(passi + 1):
        a = math.radians(a0 + (a1 - a0) * i / passi)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def onda(x0, x1, y, ampiezza, periodo, passi=40):
    return [(x0 + (x1 - x0) * i / passi,
             y - ampiezza * math.sin(2 * math.pi * ((x1 - x0) * i / passi) / periodo)) for i in range(passi + 1)]


def verde(x, y):
    return {"x": x, "y": y, "w": 2.5, "h": 2.5}


def crea_campo_rcj2026():
    """Campo grande montato con le piastrelle del regolamento 2026 (vedi piastrelle.py):
    20 x 12 piastrelle (6 x 3,6 m), rampe su e giù con altopiano, interruzioni, dossi, detriti,
    tratto inclinato di lato, vicolo cieco, falsi verdi, incrocio attraversato due volte,
    angolo acuto, ostacolo, altalena, zona di evacuazione 4 x 3 e arrivo."""
    import piastrelle as P
    K = P.Costruttore(20, 12)
    K.inizia(1, 11, 0)
    m = K.metti
    m("partenza", cp=True, etichetta="PARTENZA")
    m("dritto")
    m("curva_dx")
    m("zigzag", etichetta="ZIG-ZAG")
    m("incrocio", forma="T", verdi="sx", etichetta="T verde sx")
    m("dritto", cp=True)
    m("curva_stretta_sx")
    m("curva_dx")
    m("interruzione", lunghezza=14, etichetta="GAP")
    m("dritto", pendenza=20, etichetta="RAMPA 20°")
    m("dritto", pendenza=20)
    m("dritto", cp=True, etichetta="ALTOPIANO")
    m("curva_dx")
    m("interruzione", lunghezza=18, etichetta="GAP 18")
    m("dritto", banca=10, etichetta="INCLINATO 10°")
    m("onda")
    m("curva_dx")
    m("onda", pendenza=-20, etichetta="DISCESA 20°")
    m("dritto", pendenza=-20)
    m("dossi", quanti=2, etichetta="DOSSI")
    m("dritto", cp=True)
    m("incrocio", forma="+", verdi="falso_sx", etichetta="FALSO VERDE")
    m("dritto")
    m("incrocio", forma="T", verdi="doppio", etichetta="VICOLO CIECO")
    m("dritto")                                   # ritorno
    m("incrocio", forma="+", verdi="dx")          # stesso incrocio: ora il verde è prima, a destra
    m("detriti", etichetta="DETRITI")
    m("incrocio", forma="+", verdi="", etichetta="INCROCIO x2")
    m("curva_dx")
    m("curva_dx")
    m("curva_dx")
    m("incrocio", forma="+", verdi="")            # ripasso: dritto anche questa volta
    m("curva_dx")
    m("dritto", cp=True)
    m("acuto_dx", etichetta="ANGOLO ACUTO")
    m("curva_stretta_sx")
    m("ostacolo", etichetta="OSTACOLO")
    m("dritto", cp=True)
    m("altalena", etichetta="ALTALENA")
    m("dritto")
    m("angolo_sx")
    m("zigzag")
    m("curva_sx")
    m("curva_dx")
    m("dritto", cp=True)
    m("curva_dx")
    m("dritto")
    K.arena(sopra=1, uscita_col=1)
    m("dritto")
    m("incrocio", forma="+", verdi="falso_dx", etichetta="FALSO VERDE")
    m("curva_sx")
    m("curva_dx")
    m("incrocio", forma="T", verdi="dx", etichetta="T verde dx")
    m("dritto")
    m("curva_sx")
    m("dritto", cp=True)
    m("arrivo", etichetta="ARRIVO")
    C = K.fine((1, 11), 0)
    C["traguardi"] = []
    C["ostacolo"] = None
    return C


def crea_campo_lunga():
    """[V26] Pista LUNGA (26 x 14 piastrelle, 7,8 x 4,2 m) con tutto quello del campo 2026 e una zona di
    evacuazione 4 x 4 con INGRESSO E USCITA SULLO STESSO MURO, come l'arena della scuola."""
    import piastrelle as P
    K = P.Costruttore(26, 14)
    K.inizia(1, 13, 0)
    m = K.metti
    m("partenza", cp=True, etichetta="PARTENZA")
    m("dritto")
    m("zigzag", etichetta="ZIG-ZAG")
    m("dritto", cp=True)
    m("interruzione", lunghezza=14, etichetta="GAP")
    m("curva_dx")
    m("dritto")
    m("incrocio", forma="+", verdi="", etichetta="INCROCIO")
    m("onda", etichetta="ONDA")
    m("curva_sx")
    m("dritto", pendenza=20, etichetta="RAMPA 20°")
    m("dritto", pendenza=20)
    m("dritto", cp=True, etichetta="ALTOPIANO")
    m("interruzione", lunghezza=18, etichetta="GAP 18")
    m("curva_dx")
    m("dritto", banca=10, etichetta="INCLINATO 10°")
    m("onda", pendenza=-20, etichetta="DISCESA 20°")
    m("dritto", pendenza=-20)
    m("dossi", quanti=2, etichetta="DOSSI")
    m("dritto", cp=True)
    m("incrocio", forma="+", verdi="falso_sx", etichetta="FALSO VERDE")
    m("dritto")
    m("incrocio", forma="T", verdi="doppio", etichetta="VICOLO CIECO")
    m("dritto")                                   # ritorno
    m("incrocio", forma="+", verdi="dx")          # stesso incrocio: ora il verde è a destra
    m("detriti", etichetta="DETRITI")
    m("curva_dx")
    m("dritto")
    m("tratteggiata", etichetta="TRATTEGGIATA")
    m("curva_stretta_dx", etichetta="CURVA STRETTA")
    m("dritto")
    m("dritto", cp=True)
    m("curva_sx")
    m("dritto")
    m("ostacolo", etichetta="OSTACOLO")
    m("dritto")
    m("dritto")
    m("curva_sx")
    m("dritto")
    m("curva_dx")
    m("onda")
    m("dritto", cp=True)
    m("curva_dx")
    m("altalena", etichetta="ALTALENA")
    m("dritto")
    m("curva_dx")
    m("zigzag")
    m("curva_sx")
    m("dritto", cp=True)
    m("curva_sx")
    m("curva_dx")
    # [V27] come a scuola (scatola nera del 26/10): un incrocio con verde subito prima dell'ingresso. Il robot
    # vede la striscia argento mentre sta ancora girando.
    # [V28] verdi in DIAGONALE (foto del 29/10): uno valido a sinistra e uno falso a destra dopo l'incrocio
    m("incrocio", forma="T", verdi="diagonale_sx", etichetta="T verdi diagonale sx")
    K.arena(sopra=1, righe=4, uscita_lato="sinistro", uscita_riga=3)
    m("dritto")
    m("incrocio", forma="+", verdi="falso_dx", etichetta="FALSO VERDE")
    m("curva_sx")
    m("curva_dx")
    m("dritto")
    m("interruzione", lunghezza=20, etichetta="GAP 20")
    m("dritto", cp=True)
    m("incrocio", forma="+", verdi="diagonale_dx", etichetta="VERDI DIAGONALE dx")   # [V28] come la foto del 29/10
    m("dritto")
    m("curva_sx")
    m("onda")
    m("curva_sx")
    m("dritto")
    m("curva_dx")
    m("dritto", cp=True)
    m("zigzag")
    m("dritto")
    m("tratteggiata")
    m("curva_sx")
    m("curva_dx")
    m("dritto")
    m("curva_dx")
    m("dritto", cp=True)
    m("curva_sx")
    m("dritto")
    m("zigzag")
    m("curva_sx")
    m("dritto", cp=True)
    m("curva_sx")
    m("dritto")
    m("arrivo", etichetta="ARRIVO")
    C = K.fine((1, 13), 0)
    C["traguardi"] = []
    C["ostacolo"] = None
    return C


def crea_campo_contorto():
    """Campo 'contorto' (14 x 12 piastrelle): un serpentone di 6 file a 30 cm l'una dall'altra, così se il
    robot perde la linea accanto trova sempre un'altra linea (curva, zig-zag, onda) e prende una linea fuori
    sequenza. 15 piastrelle con interruzioni (da 14 a 20 cm, anche subito dopo una curva, sull'altopiano e
    tratteggiate), rampa con altopiano stretto tra due file, vicolo cieco, falso verde, ramo senza verde,
    angolo acuto, due ostacoli, altalena, dossi, detriti, zona di evacuazione e arrivo."""
    import piastrelle as P
    K = P.Costruttore(14, 12)
    K.inizia(1, 11, 90)
    m = K.metti
    # fila 11 verso est
    m("partenza", cp=True, etichetta="PARTENZA")
    m("dritto")
    m("interruzione", lunghezza=14, etichetta="GAP")
    m("zigzag")
    m("tratteggiata", etichetta="TRATTEGGIATA")
    m("onda")
    m("curva_sx")
    # fila 10 verso ovest
    m("curva_sx")
    m("interruzione", lunghezza=18, etichetta="GAP DOPO CURVA")
    m("zigzag")
    m("incrocio", forma="Tdx", verdi="", etichetta="RAMO SENZA VERDE")
    m("dritto", cp=True)
    m("onda")
    m("interruzione", lunghezza=20, etichetta="GAP 20")
    m("curva_dx")
    # fila 9 verso est
    m("curva_dx")
    m("dritto")
    m("altalena", etichetta="ALTALENA")
    m("dritto")
    m("zigzag")
    m("interruzione", lunghezza=14)
    m("dossi", quanti=2, etichetta="DOSSI")
    m("curva_sx")
    # fila 8 verso ovest
    m("curva_sx")
    m("tratteggiata")
    m("dritto", cp=True)
    m("zigzag")
    m("interruzione", lunghezza=16)
    m("onda")
    m("detriti", etichetta="DETRITI")
    m("curva_dx")
    # fila 7 verso est: rampa e altopiano stretto tra due file di linea
    m("curva_dx")
    m("dritto")
    m("dritto", pendenza=20, etichetta="RAMPA")
    m("interruzione", lunghezza=14, etichetta="GAP ALTO")
    m("dritto", banca=10)
    m("dritto", pendenza=-20)
    m("dritto", cp=True)
    m("curva_sx")
    # fila 6 verso ovest
    m("curva_sx")
    m("zigzag")
    m("interruzione", lunghezza=20)
    m("onda")
    m("dritto", cp=True)
    m("zigzag")
    m("interruzione", lunghezza=14)
    m("curva_dx")
    # su per la colonna 0, angolo acuto
    m("dritto")
    m("acuto_dx", etichetta="ANGOLO ACUTO")
    m("curva_sx")
    m("interruzione", lunghezza=16)
    m("curva_sx")
    m("curva_dx")
    m("curva_dx")
    # fila 1 verso est: ostacolo, falso verde, vicolo cieco
    m("dritto", cp=True)
    m("ostacolo", etichetta="OSTACOLO")
    m("dritto")
    m("incrocio", forma="+", verdi="falso_dx", etichetta="FALSO VERDE")
    m("incrocio", forma="T", verdi="doppio", etichetta="VICOLO CIECO")
    m("incrocio", forma="+", verdi="sx")
    m("curva_sx")
    m("zigzag")
    m("curva_sx")
    m("curva_dx")
    m("interruzione", lunghezza=20)
    m("onda")
    m("dritto", cp=True)
    K.arena(sopra=1, uscita_col=1)
    # discesa verso l'arrivo
    m("dritto")
    m("zigzag")
    m("incrocio", forma="T", verdi="dx", etichetta="T verde dx")
    m("curva_sx")
    m("dritto", cp=True)
    m("ostacolo", dim=(8, 14), etichetta="OSTACOLO")
    m("dritto")
    m("interruzione", lunghezza=18)
    m("curva_sx")
    m("curva_dx")
    m("arrivo", etichetta="ARRIVO")
    C = K.fine((1, 11), 90)
    C["traguardi"] = []
    C["ostacolo"] = None
    return C


def crea_campo(variante="normale"):
    if variante == "rcj2026":
        return crea_campo_rcj2026()
    if variante == "contorto":
        return crea_campo_contorto()
    if variante == "lunga":
        return crea_campo_lunga()
    if variante.startswith("scuola"):                 # [V29] la pista della scuola (foto del 03/11)
        import pista_scuola
        return pista_scuola.crea_campo_scuola(variante)
    C = {"larghezza": 450, "altezza": 270, "piastrella": 30}
    AX = 330          # bordo sinistro dell'arena
    YL = 50           # quota della linea che entra nell'arena

    # ---- LINEE NERE (polilinee) ----
    C["linee"] = [
        # partenza, rampa, curva, verso est fino all'incrocio 2 e un pezzetto oltre (ramo morto)
        [(15, 258), (15, 150)] + arco(35, 150, 20, 180, 270)[1:] + [(190, 130)],
        [(15, 235), (45, 235)],                 # incrocio 0: ramo est (vicolo cieco)
        [(90, 130), (90, 160)],                 # incrocio 1: ramo sud (morto)
        [(165, 105), (165, 155)],               # incrocio 2: rami nord e sud (morti)
        [(90, 130), (90, 100)],                 # incrocio 1: ramo nord fino all'interruzione
        # dopo l'interruzione: curva, onde, rettilineo con ostacolo fino all'arena
        [(90, 88), (90, 70)] + arco(110, 70, 20, 180, 270)[1:] + [(125, YL)]
        + onda(125, 185, YL, 7, 60)[1:] + [(AX, YL)],
        # uscita dall'arena: giù fino all'incrocio 3, verde a sinistra, curva, linea rossa
        [(AX + 55, 90), (AX + 55, 170)],
        [(AX + 55, 140), (AX + 65, 140)] + arco(AX + 65, 160, 20, 270, 360)[1:] + [(AX + 85, 215)],
    ]

    # ---- QUADRATINI VERDI, con l'incrocio a cui si riferiscono ----
    C["verdi"] = [
        # incrocio 0 (15,235): verde a est DOPO l'incrocio (falso verde). Se il modello lo prende
        # per buono il robot gira a destra e finisce nel vicolo cieco.
        dict(verde(16.2, 231.4), id="V0", incrocio=(15, 235)),
        # incrocio 1 (90,130): verde a NORD-EST. Andando verso est è DOPO l'incrocio (falso verde);
        # tornando verso ovest dopo il dietrofront è PRIMA dell'incrocio, a destra -> svolta a destra.
        dict(verde(91.2, 126.4), id="V1", incrocio=(90, 130)),
        # incrocio 2 (165,130): doppio verde prima dell'incrocio -> dietrofront
        dict(verde(160.0, 126.4), id="V2a", incrocio=(165, 130)),
        dict(verde(160.0, 131.1), id="V2b", incrocio=(165, 130)),
        # incrocio 3 (385,140): scendendo da nord il verde è a EST = a sinistra -> svolta a sinistra
        dict(verde(AX + 56.2, 136.4), id="V3", incrocio=(AX + 55, 140)),
    ]
    # ---- ALTRI ELEMENTI RICONOSCIUTI DA YOLO (classe del modello Cross3) ----
    C["elementi"] = [
        {"tipo": "Di", "poli": [(89.0, 88.0), (91.0, 88.0), (91.0, 100.0), (89.0, 100.0)]},
        {"tipo": "In", "poli": [(AX, YL - 12.5), (AX + 2.5, YL - 12.5), (AX + 2.5, YL + 12.5), (AX, YL + 12.5)]},
        {"tipo": "Ro", "poli": [(AX + 72.5, 215.0), (AX + 97.5, 215.0), (AX + 97.5, 217.5), (AX + 72.5, 217.5)]},
    ]
    C["argento"] = {"x": AX, "y": YL - 12.5, "w": 2.5, "h": 25.0}      # striscia argento all'ingresso
    C["nero_uscita"] = {"x": AX + 42.5, "y": 87.5, "w": 25.0, "h": 2.5}  # striscia nera all'uscita
    C["rosso"] = {"x": AX + 72.5, "y": 215.0, "w": 25.0, "h": 2.5}       # linea rossa di arrivo
    C["linea_arena_y"] = YL

    # ---- RAMPA (salita di 20° percorrendo verso nord) ----
    C["rampa"] = {"x": 0, "y": 180, "w": 30, "h": 30, "pendenza": 20, "salita_verso": 0}

    # ---- OSTACOLO (blocco di legno 10x10, alto 15 cm) ----
    C["ostacolo"] = {"x": 245, "y": YL - 5, "w": 10, "h": 10}

    # ---- ARENA (zona di evacuazione 120 x 90) ----
    X2 = AX + 120
    C["arena"] = {"x": AX, "y": 0, "w": 120, "h": 90,
                  "ingresso": (YL - 13.5, YL + 13.5),   # apertura sul muro sinistro (y da..a): 27 cm MISURATI
                  "uscita": (AX + 41.5, AX + 68.5)}     # apertura sul muro basso (x da..a): 27 cm
    yi0, yi1 = C["arena"]["ingresso"]
    C["muri"] = [
        ((AX, 0), (X2, 0)), ((X2, 0), (X2, 90)),
        ((AX, 0), (AX, yi0)), ((AX, yi1), (AX, 90)),
        ((AX, 90), (AX + 41.5, 90)), ((AX + 68.5, 90), (X2, 90)),
    ]
    C["triangoli"] = [
        {"colore": "verde", "classe": 3, "poli": [(X2, 0), (X2 - 30, 0), (X2, 30)]},    # palline ARGENTO
        {"colore": "rosso", "classe": 2, "poli": [(X2, 90), (X2 - 30, 90), (X2, 60)]},  # pallina NERA
    ]
    C["palline"] = [
        {"id": "A1", "tipo": "argento", "x": AX + 50.0, "y": 25.0},
        {"id": "A2", "tipo": "argento", "x": AX + 82.0, "y": 62.0},
        {"id": "N1", "tipo": "nera", "x": AX + 28.0, "y": 72.0},
    ]
    C["raggio_pallina"] = 2.25

    # ---- TRAGUARDI del percorso della linea (rettangolo x0, y0, x1, y1) ----
    # richiede = traguardi già raggiunti; esclude = traguardi che non devono esserci; heading = direzione ammessa
    no_dietro = "Incrocio 2: doppio verde, ma NIENTE dietrofront"
    C["traguardi"] = [
        {"chiave": "falso_verde0", "tipo": "ok", "testo": "Incrocio 0: falso verde ignorato, dritto",
         "rett": (0, 212, 30, 225)},
        {"chiave": "falso_verde0_err", "tipo": "errore", "testo": "Incrocio 0: ha girato per un FALSO verde (vicolo cieco)",
         "rett": (26, 225, 50, 245)},
        {"chiave": "rampa", "tipo": "ok", "testo": "Rampa superata", "rett": (0, 140, 40, 172)},
        {"chiave": "falso_verde", "tipo": "ok", "testo": "Incrocio 1: falso verde ignorato, dritto",
         "rett": (108, 120, 135, 140), "esclude": ["doppio_verde"]},
        {"chiave": "falso_verde_err", "tipo": "errore", "testo": "Incrocio 1: ha girato per un FALSO verde",
         "rett": (80, 92, 100, 115), "esclude": ["doppio_verde", "falso_verde"]},
        {"chiave": "dv_err_n", "tipo": "errore", "testo": no_dietro, "rett": (155, 100, 175, 118), "esclude": ["doppio_verde"]},
        {"chiave": "dv_err_s", "tipo": "errore", "testo": no_dietro, "rett": (155, 142, 175, 160), "esclude": ["doppio_verde"]},
        {"chiave": "dv_err_e", "tipo": "errore", "testo": no_dietro, "rett": (176, 120, 200, 140), "esclude": ["doppio_verde"]},
        {"chiave": "doppio_verde", "tipo": "ok", "testo": "Incrocio 2: doppio verde, dietrofront eseguito",
         "rett": (110, 120, 145, 140), "richiede": ["falso_verde"], "heading": (225, 315)},
        {"chiave": "verde_ritorno", "tipo": "ok", "testo": "Incrocio 1 al ritorno: verde a destra, svolta corretta",
         "rett": (80, 102, 100, 118), "richiede": ["doppio_verde"]},
        {"chiave": "ritorno_err", "tipo": "errore", "testo": "Incrocio 1 al ritorno: verde a destra IGNORATO",
         "rett": (30, 120, 75, 140), "richiede": ["doppio_verde"], "esclude": ["verde_ritorno"], "heading": (200, 340)},
        {"chiave": "ritorno_sud_err", "tipo": "errore", "testo": "Incrocio 1 al ritorno: preso il ramo sud (sbagliato)",
         "rett": (80, 145, 100, 165), "richiede": ["doppio_verde"], "esclude": ["verde_ritorno"]},
        {"chiave": "gap", "tipo": "ok", "testo": "Interruzione della linea superata",
         "rett": (80, 55, 100, 84), "richiede": ["verde_ritorno"]},
        {"chiave": "onde", "tipo": "ok", "testo": "Curve a onda superate", "rett": (186, 38, 205, 62)},
        {"chiave": "verde3", "tipo": "ok", "testo": "Incrocio 3 dopo l'arena: verde a sinistra, svolta corretta",
         "rett": (AX + 64, 128, AX + 82, 152), "richiede": ["uscita"]},
        {"chiave": "verde3_err", "tipo": "errore", "testo": "Incrocio 3: verde a sinistra IGNORATO (dritto)",
         "rett": (AX + 45, 152, AX + 65, 172), "richiede": ["uscita"], "esclude": ["verde3"]},
    ]

    # ---- ETICHETTE per il replay ----
    C["etichette"] = [
        ["PARTENZA", 24, 262, "left"], ["INCROCIO 0 · falso verde", 48, 235, "left"], ["RAMPA 20°", 24, 195, "left"],
        ["INCROCIO 1 · falso verde", 94, 122, "left"], ["INCROCIO 2 · doppio verde", 170, 113, "left"],
        ["INTERRUZIONE", 96, 94, "left"], ["ONDE", 155, 66, "center"], ["OSTACOLO", 250, 66, "center"],
        ["ARENA", AX + 4, 6, "left"], ["USCITA", AX + 37, 97, "right"],
        ["INCROCIO 3", AX + 60, 132, "left"], ["ARRIVO", AX + 85, 225, "center"],
    ]

    C["partenza"] = {"x": 15.0, "y": 257.0, "heading": 0.0}
    if variante == "stessa_parete":
        stessa_parete(C, AX, YL)
    return C


def stessa_parete(C, AX, YL):
    """Arena come quella della scuola (video dell'8/10): ingresso e uscita sullo STESSO muro,
    l'ingresso con la striscia argento, poi un pezzo di muro, poi l'uscita con la striscia nera."""
    X2, H = AX + 120, 120
    C["arena"] = {"x": AX, "y": 0, "w": 120, "h": H, "ingresso": (YL - 13.5, YL + 13.5),
                  "uscita": (YL + 35, YL + 62), "uscita_muro": "sinistro"}
    yi0, yi1 = C["arena"]["ingresso"]
    yu0, yu1 = C["arena"]["uscita"]
    C["muri"] = [((AX, 0), (X2, 0)), ((X2, 0), (X2, H)), ((AX, H), (X2, H)),
                 ((AX, 0), (AX, yi0)), ((AX, yi1), (AX, yu0)), ((AX, yu1), (AX, H))]
    C["triangoli"] = [
        {"colore": "verde", "classe": 3, "poli": [(X2, 0), (X2 - 30, 0), (X2, 30)]},
        {"colore": "rosso", "classe": 2, "poli": [(X2, H), (X2 - 30, H), (X2, H - 30)]},
    ]
    C["palline"] = [
        {"id": "A1", "tipo": "argento", "x": AX + 50.0, "y": 25.0},
        {"id": "A2", "tipo": "argento", "x": AX + 82.0, "y": 75.0},
        {"id": "N1", "tipo": "nera", "x": AX + 40.0, "y": 100.0},
    ]
    yu = (yu0 + yu1) / 2
    C["nero_uscita"] = {"x": AX, "y": yu0, "w": 2.5, "h": yu1 - yu0}
    # fuori dall'uscita la linea va a ovest e poi scende fino alla linea rossa
    C["linee"] = C["linee"][:6] + [[(AX, yu), (AX - 40, yu)] + arco(AX - 40, yu + 20, 20, 270, 180)[1:] + [(AX - 60, 215)]]
    C["verdi"] = [v for v in C["verdi"] if v["id"] != "V3"]
    C["rosso"] = {"x": AX - 72.5, "y": 215.0, "w": 25.0, "h": 2.5}
    C["elementi"] = [e for e in C["elementi"] if e["tipo"] != "Ro"] + [
        {"tipo": "Ro", "poli": [(AX - 72.5, 215.0), (AX - 47.5, 215.0), (AX - 47.5, 217.5), (AX - 72.5, 217.5)]}]
    C["traguardi"] = [t for t in C["traguardi"] if t["chiave"] not in ("verde3", "verde3_err")]
    C["etichette"] = [e for e in C["etichette"] if e[0] not in ("USCITA", "INCROCIO 3", "ARRIVO")] + [
        ["INGRESSO", AX - 4, YL - 18, "right"], ["USCITA", AX - 4, yu0 - 3, "right"], ["ARRIVO", AX - 60, 225, "center"]]


SCENARI = {
    # [V29] pista della scuola ricostruita dalle foto del 03/11 (vedi pista_scuola.py)
    "scuola": {"nome": "Pista della SCUOLA: linea lunga, zig-zag, quadrato, INGRESSO argento, arena, USCITA nera, linea rossa", "campo": "scuola"},
    "scuola_rampa": {"nome": "Pista della SCUOLA: dalla rampa con i tubi (piattaforma, cerchio, curve a S)", "campo": "scuola_rampa"},
    "scuola_basso": {"nome": "Pista della SCUOLA: angolo in basso, zig-zag, T con doppio verde", "campo": "scuola_basso"},
    "scuola_parete": {"nome": "Pista della SCUOLA: semicerchio accanto alla parete destra (scatola nera 03/11)", "campo": "scuola_parete"},
    "gara": {"nome": "Gara completa", "partenza": {"x": 15.0, "y": 257.0, "heading": 0.0}},
    "arena": {"nome": "Solo arena (parte davanti all'ingresso)", "partenza": {"x": 305.0, "y": 50.0, "heading": 90.0}},
    "rcj2026": {"nome": "Campo RCJ 2026: piastrelle, rampe, altalena, punteggio ufficiale", "campo": "rcj2026"},
    "lunga": {"nome": "Pista lunga (26 x 14 piastrelle) con arena: ingresso e uscita sullo stesso muro", "campo": "lunga"},
    "contorto": {"nome": "Campo contorto: serpentone a file vicine, 15 interruzioni, punteggio ufficiale", "campo": "contorto"},
    "arena_parete": {"nome": "Arena della scuola: ingresso e uscita sullo stesso muro", "campo": "stessa_parete",
                     "partenza": {"x": 305.0, "y": 50.0, "heading": 90.0}},
}
