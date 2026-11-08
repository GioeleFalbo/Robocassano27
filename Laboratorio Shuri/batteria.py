#!/usr/bin/env python3
"""Batteria di prove di Shuri: fa girare il codice del robot nel simulatore su più piste e semi.
Uso:  python3 batteria.py [cartella_codice] [--forza]
Va lanciata PIÙ VOLTE finché non stampa "FATTO": ogni chiamata esegue qualche gara
(al massimo ~2 minuti) e riprende da dove si era fermata (file in_corso.json).
- cartella_codice: di default l'ultima ClaudeRob_V<n> in 02_Robotica
- senza --forza la batteria parte solo se il codice è cambiato dall'ultima volta
  (o se l'ultima batteria ha più di 7 giorni)
Risultati in Prove/AAAA-MM-GG_HHMM_<versione>/ : replay_*.json + batteria.json
"""
import sys, os, re, json, hashlib, shutil, datetime as dt
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

QUI = Path(__file__).resolve().parent
ROBOTICA = QUI.parent

def num(p):
    n = re.findall(r"\d+", p.name); return int(n[-1]) if n else -1

def ultimo_simulatore():
    c = [p for p in ROBOTICA.glob("ClaudeRob_Simulatore_V*") if p.is_dir() and (p / "esegui.py").exists()]
    return sorted(c, key=num)[-1] if c else None

def ultimo_codice():
    c = [p for p in ROBOTICA.glob("ClaudeRob_V*") if p.is_dir() and (p / "RwdFoto.py").exists()]
    return sorted(c, key=num)[-1] if c else None

def impronta(cartella):
    h = hashlib.sha256()
    for f in sorted(Path(cartella).glob("*.py")):
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()[:16]

# (nome, scenario, secondi, configurazione, descrizione)
BATTERIA = [
    ("rcj2026_s1", "rcj2026", 480, {"seme": 1}, "Campo RCJ 2026, seme 1"),
    ("rcj2026_s2", "rcj2026", 480, {"seme": 2}, "Campo RCJ 2026, seme 2"),
    ("rcj2026_s3", "rcj2026", 480, {"seme": 3}, "Campo RCJ 2026, seme 3"),
    ("lunga_s1", "lunga", 480, {"seme": 1}, "Pista lunga della scuola, seme 1"),
    ("lunga_s2", "lunga", 480, {"seme": 2}, "Pista lunga della scuola, seme 2"),
    ("contorto_s1", "contorto", 480, {"seme": 1}, "Campo contorto, seme 1"),
    ("contorto_s2", "contorto", 480, {"seme": 2}, "Campo contorto, seme 2"),
    ("arena_parete_s1", "arena_parete", 480, {"seme": 1}, "Arena della scuola"),
    ("stress_argento_rampa", "lunga", 480, {"seme": 1, "yolo_argento_rampa": True}, "STRESS: falso argento a inizio rampa"),
    ("stress_bussola", "rcj2026", 480, {"seme": 1, "bussola_distorsione": 15}, "STRESS: giroscopio disturbato di 15°"),
    ("stress_porta", "arena_parete", 480, {"seme": 1, "yolo_porta_solo_ingresso": True}, "STRESS: YOLO vede solo la porta d'ingresso"),
    # [3/11, simulatore V29] i guasti visti nella scatola nera vera del 3/11 e la pista della scuola
    ("stress_guasti_reali", "rcj2026", 480, {"seme": 1, "imu_bloccato": True, "tof_fr_spurie": 0.15, "tof_lat_spurie": 0.1},
     "STRESS: giroscopio bloccato + laser che saltano (come il robot vero il 3/11)"),
    ("stress_guasti_lunga", "lunga", 480, {"seme": 1, "imu_bloccato": True, "tof_fr_spurie": 0.15, "tof_lat_spurie": 0.1},
     "STRESS: gli stessi guasti sulla pista lunga"),
    ("scuola", "scuola", 420, {"seme": 1}, "Pista della SCUOLA (foto del 3/11): linea lunga, zig-zag, quadrato, ingresso, arena, uscita, arrivo"),
    ("scuola_rampa", "scuola_rampa", 300, {"seme": 1}, "Pista della SCUOLA: dalla rampa con i tubi"),
    ("scuola_parete", "scuola_parete", 300, {"seme": 1}, "Pista della SCUOLA: semicerchio accanto alla parete destra (Simulatore V30)"),
]

LIMITE_REALE = 110   # secondi reali massimi per una gara: oltre, il programma è bloccato

def una_prova(args):
    """Ogni gara gira in un processo separato con un cronometro: se il programma del robot
    resta in un ciclo che non fa avanzare il tempo simulato, la gara viene fermata."""
    import subprocess
    sim, codice, nome, scenario, tmax, cfg = args
    codice_py = (f"import sys; sys.path.insert(0, {str(sim)!r}); import esegui; "
                 f"esegui.esegui({str(codice)!r}, {('shuri_' + nome)!r}, {tmax}, {dict(cfg)!r}, {scenario!r})")
    try:
        p = subprocess.run([sys.executable, "-c", codice_py], cwd=sim, capture_output=True, text=True, timeout=LIMITE_REALE)
        return nome, None if p.returncode == 0 else ("errore del simulatore: " + p.stderr[-400:])
    except subprocess.TimeoutExpired:
        return nome, f"BLOCCATO: dopo {LIMITE_REALE} s reali la gara non era finita (il tempo simulato non avanza: probabile ciclo senza sleep nel codice)"

def main():
    import time
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    forza = "--forza" in sys.argv
    sim = ultimo_simulatore()
    corso_f = QUI / "in_corso.json"
    if corso_f.exists():
        corso = json.loads(corso_f.read_text())
        codice, cartella = ROBOTICA / Path(corso["codice_path"]).name, QUI / "Prove" / corso["cartella"]  # percorso relativo: la cartella montata cambia a ogni sessione
    else:
        codice = Path(argv[0]).resolve() if argv else ultimo_codice()
        if not codice or not sim:
            print("ERRORE: non trovo il codice (ClaudeRob_V*) o il simulatore (ClaudeRob_Simulatore_V*) in 02_Robotica"); sys.exit(2)
        imp = impronta(codice)
        stato_f = QUI / "ultimo_stato.json"
        tutto = json.loads(stato_f.read_text()) if stato_f.exists() else {}
        if "impronta" in tutto: tutto = {tutto.get("codice", "?"): tutto}   # vecchio formato
        stato = tutto.get(codice.name, {})
        vecchia = stato.get("data")
        giorni = (dt.datetime.now() - dt.datetime.fromisoformat(vecchia)).days if vecchia else 999
        if not forza and stato.get("impronta") == imp and stato.get("codice") == codice.name and stato.get("simulatore") == sim.name and giorni < 7:
            print(f"NIENTE DA FARE: {codice.name} non è cambiato dall'ultima batteria ({vecchia})"); return
        ora = dt.datetime.now()
        cartella = QUI / "Prove" / f"{ora:%Y-%m-%d_%H%M}_{codice.name}"
        cartella.mkdir(parents=True, exist_ok=True)
        corso = {"codice_path": str(codice), "cartella": cartella.name, "data": ora.isoformat(timespec="minutes"), "impronta": imp, "esiti": {}}
        corso_f.write_text(json.dumps(corso, indent=2))
    inizio = time.time()
    while True:
        fatte = {f.stem.replace("replay_", "") for f in cartella.glob("replay_*.json")} | {k for k, v in corso["esiti"].items() if v}
        mancanti = [b for b in BATTERIA if b[0] not in fatte]
        if not mancanti or time.time() - inizio > 75: break
        onda = mancanti[:3]
        with ProcessPoolExecutor(max_workers=3) as ex:
            esiti = dict(ex.map(una_prova, [(sim, codice, n, s, t, c) for n, s, t, c, _ in onda]))
        corso["esiti"].update(esiti); corso_f.write_text(json.dumps(corso, indent=2))
        for n, *_ in onda:
            src = sim / f"replay_shuri_{n}.json"
            if src.exists(): shutil.move(str(src), cartella / f"replay_{n}.json")
            elif esiti.get(n) is None: corso["esiti"][n] = "nessun replay prodotto"
        corso_f.write_text(json.dumps(corso, indent=2))
    fatte = {f.stem.replace("replay_", "") for f in cartella.glob("replay_*.json")}
    mancanti = [b[0] for b in BATTERIA if b[0] not in fatte and not corso["esiti"].get(b[0])]
    if mancanti:
        print(f"IN CORSO: {len(BATTERIA) - len(mancanti)}/{len(BATTERIA)} gare fatte. Rilancia batteria.py per continuare."); return
    meta = {"data": corso["data"], "codice": codice.name, "impronta": corso["impronta"],
            "simulatore": sim.name, "cartella": cartella.name,
            "prove": [{"nome": n, "scenario": s, "secondi": t, "config": c, "descrizione": d, "errore_lancio": corso["esiti"].get(n)}
                      for n, s, t, c, d in BATTERIA]}
    (cartella / "batteria.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    sf = QUI / "ultimo_stato.json"
    tutto = json.loads(sf.read_text()) if sf.exists() else {}
    if "impronta" in tutto: tutto = {tutto.get("codice", "?"): tutto}
    tutto[codice.name] = {"data": meta["data"], "impronta": meta["impronta"], "codice": codice.name, "simulatore": sim.name, "cartella": cartella.name}
    sf.write_text(json.dumps(tutto, indent=2))
    corso_f.rename(QUI / "Prove" / cartella.name / "in_corso_chiuso.json")
    print("FATTO", cartella)

if __name__ == "__main__":
    main()
