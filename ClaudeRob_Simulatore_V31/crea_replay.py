"""
Mette insieme una o più prove (replay_*.json) in un'unica pagina HTML da aprire nel browser.

Uso:
    python crea_replay.py uscita.html replay_v2_gara.json:"Gara · v2" replay_originale_gara.json:"Gara · originale" ...
Se non passate niente, usa le quattro prove standard.
"""
import json
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import campo as campo_mod

PROVE_STANDARD = [
    ("replay_V26_rampa.json", "Pista lunga · V26: falso argento all'inizio della rampa, entra nell'«arena» sulla rampa (8 LoP)"),
    ("replay_V27_rampa.json", "Pista lunga · V27: stesso falso argento, ingresso annullato (non è in piano), arriva in fondo"),
    ("replay_L27_s1.json", "Pista lunga · V27: verdi in diagonale, 3 vittime"),
    ("replay_R27_s1.json", "Campo 2026 · V27, punteggio pieno"),
    ("replay_C27_s2.json", "Contorto · V27: vicolo cieco e ritorno all'incrocio"),
    ("replay_P27_s1.json", "Arena con parete · V27: 3 vittime e uscita"),
    ("replay_L26_s2.json", "Pista lunga (sim V27) · V26: entra dritta dopo l'incrocio"),
    ("replay_L25b_s2.json", "Pista lunga (sim V27) · V25: entra storta dopo l'incrocio"),
]


def compatta(r, etichetta):
    campioni = []
    palline = []
    ultimo = None
    for c in r["campioni"]:
        stringa = c[19]
        if stringa != ultimo:
            stato = []
            for parte in stringa.split("|"):
                i, x, y, s = parte.split(",")
                stato.append([i, float(x), float(y), s])
            palline.append([c[0], stato])
            ultimo = stringa
        campioni.append(c[:19] + c[20:])     # [V22] dopo il 19: rollio, quota, inquadratura, altalena, punti
    cfg = r["config"]
    return {
        "etichetta": etichetta,
        "nome": r["nome"],
        "scenario": r.get("scenario", "gara"),
        "scenario_nome": r.get("scenario_nome", ""),
        "campo": campo_mod.SCENARI.get(r.get("scenario", "gara"), {}).get("campo", "normale"),
        "fine": r["fine"],
        "durata": r["durata"],
        "errore": r.get("errore"),
        "statistiche": r["statistiche"],
        "urti": r["urti"],
        "campioni": campioni,
        "stati": r["stati"],
        "eventi": r["eventi"],
        "log": r["log"],
        "palline": palline,
        "config": cfg,
        "punteggio": r.get("punteggio"),
    }


def per_json(C):
    """[V22] Il campo a piastrelle usa dizionari con chiavi (colonna, riga): in JSON diventano liste."""
    D = {k: v for k, v in C.items() if k not in ("quote", "celle_linea", "tolleranza")}
    if "quote" in C:
        D["quote"] = [dict(q, cella=list(c)) for c, q in C["quote"].items() if q["tipo"] != "piana" or q["z"] > 0.5]
    return D


def crea(uscita, prove):
    import piastrelle
    campo = per_json(campo_mod.crea_campo())
    dati = {"campo": campo, "campi": {"normale": campo}, "prove": [], "catalogo": piastrelle.catalogo()}
    for percorso, etichetta in prove:
        with open(os.path.join(QUI, percorso), encoding="utf-8") as f:
            p = compatta(json.load(f), etichetta)
        if p["campo"] not in dati["campi"]:
            dati["campi"][p["campo"]] = per_json(campo_mod.crea_campo(p["campo"]))
        if len(dati["prove"]) == 0:
            dati["campo"] = dati["campi"][p["campo"]]
        dati["prove"].append(p)
    modello = open(os.path.join(QUI, "visualizzatore.html"), encoding="utf-8").read()
    js = json.dumps(dati, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = modello.replace("/*__DATI__*/null", js)
    with open(uscita, "w", encoding="utf-8") as f:
        f.write(html)
    sys.stdout.write(f"Creato {uscita} ({len(html) / 1e6:.1f} MB)\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        crea(os.path.join(QUI, "replay.html"), PROVE_STANDARD)
    else:
        prove = []
        for a in sys.argv[2:]:
            p, _, e = a.partition(":")
            prove.append((p, e or p))
        crea(sys.argv[1], prove or PROVE_STANDARD)
