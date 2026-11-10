"""
[Sim V32] LA PISTA DELLA SCUOLA A PIASTRELLE (foto del 10/11/2026 + misure di Battista e del prof).

È una BOZZA da correggere con la squadra: le foto sono prese di sbieco e non si vede tutto. Per correggerla
basta cambiare la lista qui sotto (una riga = una piastrella, nell'ordine in cui il robot le percorre) e
rilanciare `python3 disegna_mappa.py` per vedere la mappa nuova (mappa_scuola.png).

Come si legge
- Il campo è 11 colonne (A..K, da sinistra) x 9 righe (1..9, dall'alto) di piastrelle da 30 cm.
- K.inizia(colonna, riga, direzione): direzione 0 = verso l'alto (nord), 90 = destra, 180 = giù, 270 = sinistra.
- m("tipo", ...) mette una piastrella e passa alla successiva. Tipi: vedi piastrelle.py (dritto, curva_dx,
  zigzag, incrocio, dossi, altalena, arrivo, ...). pendenza=21 = rampa in salita di 21 gradi.
- sotto=True = piastrella del TUNNEL, sotto il ponte (secondo livello).

Misure vere (issue #17)
- Rampe 21 gradi, 2 piastrelle per salire: 2 x 30 x tan(21) = 23,0 cm = altezza del ponte misurata.
- Tunnel sotto il ponte: 91 cm (3 piastrelle), largo 30 cm, alto 22,3 cm liberi (tavola del ponte 0,7 cm).
  Il robot con il braccio alzato è alto 21 cm: passa con 1,3 cm di margine.
- Tubi (dossi) diametro 3 cm; altalena con perno a 5 cm e tavola da 30 cm: 19,5 gradi per parte.
- Arena 120 x 90 cm: INGRESSO argento sul lato LUNGO, USCITA nera sul lato CORTO accanto al triangolo rosso.

Da controllare con la squadra (stime mie): punto di partenza, ordine dei pezzi prima del ponte, quali incroci
hanno i verdi e da che parte, posizione della linea rossa, posizione delle palline.
"""
import piastrelle as P

COLONNE, RIGHE = 11, 9


def crea_campo_scuola_piastrelle():
    K = P.Costruttore(COLONNE, RIGHE)
    m = K.metti
    # --- 1. partenza in alto a sinistra, giù lungo la colonna A ---
    K.inizia(0, 0, 180)
    m("partenza", cp=True, etichetta="PARTENZA")
    m("dritto")
    m("dossi", quanti=1, etichetta="TUBO")
    m("zigzag", etichetta="ZIG-ZAG")
    m("incrocio", forma="+", verdi="falso_dx", etichetta="FALSO VERDE")
    m("dritto", cp=True)
    m("dritto")
    m("curva_sx")                                   # A8: verso destra
    # --- 2. T con il verde a destra, poi verso il ponte ---
    m("incrocio", forma="T", verdi="dx", etichetta="T verde dx")   # B8: giù
    m("curva_sx")                                   # B9: verso destra
    m("onda")                                       # C9
    m("curva_sx")                                   # D9: su
    # --- 3. IL PONTE: rampa 21 gradi con i tubi, sopra il tunnel, discesa 21 gradi ---
    m("dossi", quanti=2, pendenza=21, etichetta="RAMPA 21°")        # D8
    m("dossi", quanti=1, pendenza=21)                                # D7
    m("curva_dx", cp=True, etichetta="PONTE 23 cm")                  # D6 (sopra il tunnel)
    m("dossi", quanti=2)                                             # E6
    m("curva_sx")                                                    # F6: su
    m("dritto", pendenza=-21, etichetta="DISCESA 21°")               # F5
    m("dritto", pendenza=-21)                                        # F4
    # --- 4. in alto: T con il verde a sinistra, gradini, giù verso il tunnel ---
    m("incrocio", forma="T", verdi="sx", etichetta="T verde sx")     # F3: a sinistra
    m("onda")                                                        # E3
    m("dritto")                                                      # D3
    m("curva_sx")                                                    # C3: giù
    m("dritto", cp=True)                                             # C4
    m("dritto")                                                      # C5
    m("curva_sx")                                                    # C6: verso destra
    # --- 5. IL TUNNEL (sotto il ponte, 3 piastrelle) ---
    m("zigzag", sotto=True, etichetta="TUNNEL")                      # D6 sotto
    m("dossi", quanti=1, sotto=True)                                 # E6 sotto: il tubo trasparente
    m("dritto", sotto=True)                                          # F6 sotto
    K.tunnel([(3, 5), (4, 5), (5, 5)], "EW")
    # --- 6. verso l'arena ---
    m("curva_sx")                                                    # G6: su
    m("dritto", cp=True)                                             # G5
    m("incrocio", forma="+", verdi="falso_dx", etichetta="FALSO VERDE")  # G4: dritto
    m("curva_dx")                                                    # G3: verso l'arena
    m("dritto")                                                      # H3: dritto fino alla striscia argento
    # --- 7. ARENA 3 x 4 piastrelle (120 cm sul lato dell'ingresso, 90 cm di profondità) ---
    AX, AY = 8 * P.T, 0.0
    K.arena(sopra=2, uscita_col=1, righe=4, colonne=3, triangoli={"rosso": "basso_sx", "verde": "alto_dx"},
            palline=[{"id": "A1", "tipo": "argento", "x": AX + 50.0, "y": AY + 25.0},
                     {"id": "A2", "tipo": "argento", "x": AX + 70.0, "y": AY + 80.0},
                     {"id": "N1", "tipo": "nera", "x": AX + 40.0, "y": AY + 95.0}])
    # --- 8. dopo l'USCITA (lato corto, in basso): altalena e linea rossa ---
    m("dritto")                                                      # J5
    m("altalena", angolo=19.5, etichetta="ALTALENA 19,5°")           # J6
    m("dritto", cp=True)                                             # J7
    m("onda")                                                        # J8
    m("arrivo", etichetta="ARRIVO")                                  # J9
    C = K.fine((0, 0), 180)
    # parete a destra di una parte della pista (bordo destro, accanto all'altalena e all'arrivo)
    X = COLONNE * P.T
    C["muri"].append(((X, 4 * P.T), (X, RIGHE * P.T)))
    # le pareti del tunnel NON sono tra i muri: valgono solo per chi sta sotto il ponte (vedi mondo.py)
    C["traguardi"] = []
    C["ostacolo"] = None
    return C


if __name__ == "__main__":
    C = crea_campo_scuola_piastrelle()
    print(len(C["percorso"]), "piastrelle di percorso;", "tunnel:", [t["celle"] for t in C.get("tunnel", [])])
    for p in C["percorso"]:
        print(" ", "ABCDEFGHIJK"[p["cella"][0]] + str(p["cella"][1] + 1), p["nome"], "z", p["z"])
