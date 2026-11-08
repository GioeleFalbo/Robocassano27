"""
Esegue il VOSTRO programma (RwdFoto.py) dentro il mondo simulato e salva il replay.

Uso:
    python esegui.py "cartella con i vostri file .py" nome_prova [secondi_massimi] [scenario]
    scenario = rcj2026 (campo 2026 a piastrelle, punteggio ufficiale), gara (percorso vecchio), arena (parte davanti all'ingresso)
               oppure arena_parete (arena della scuola: ingresso e uscita sullo stesso muro)
Esempio:
    python esegui.py "../ClaudeRob_V24" V21 420 gara

Produce: replay_<nome_prova>.json  (da aprire con crea_replay.py)
"""
import json
import os
import sys
import time as _t

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)

import campo as campo_mod
import mondo as mondo_mod
import finto_hw


def esegui(cartella, nome, tmax=420.0, cfg=None, scenario="gara"):
    cartella = os.path.abspath(cartella)
    campo = campo_mod.crea_campo(campo_mod.SCENARI[scenario].get("campo", "normale"))
    if "partenza" in campo_mod.SCENARI[scenario]:
        campo["partenza"] = dict(campo_mod.SCENARI[scenario]["partenza"])
    cfg = dict(cfg or {})
    if "percorso" in campo:
        # [V22] 8 minuti di gara, come da regolamento. [V26] "tempo_gara" nel cfg per vedere tutta la pista
        tmax = min(tmax, float(cfg.pop("tempo_gara", 480.0)))
    seme = int(cfg.pop("seme", 1))          # [V22] seme del rumore dei sensori: prove diverse = gare diverse
    M = mondo_mod.Mondo(campo, cfg, seme)
    M.tempo_max = tmax
    inizio_reale = _t.perf_counter()
    stdout = sys.stdout
    contesto = finto_hw.installa(M)
    sys.path.insert(0, cartella)
    vecchia_dir = os.getcwd()
    os.chdir(cartella)
    errore = None
    try:
        finto_hw.collega_moduli(M, contesto)
        percorso = os.path.join(cartella, "RwdFoto.py")
        sorgente = open(percorso, encoding="utf-8").read()
        G = {"__name__": "__main__", "__file__": percorso}
        M.globali = G
        exec(compile(sorgente, percorso, "exec"), G)
        M.fine = M.fine or "programma terminato"
    except mondo_mod.FineSimulazione as e:
        M.fine = str(e)
    except Exception as e:
        import traceback
        errore = traceback.format_exc()
        M.evento("errore", f"ERRORE PYTHON nel vostro codice: {type(e).__name__}: {e}")
        M.fine = "errore Python"
    finally:
        os.chdir(vecchia_dir)
        finto_hw.ripristina()
    durata_reale = _t.perf_counter() - inizio_reale
    stdout.write(f"[{nome}] fine: {M.fine} dopo {M.t:.1f} s simulati ({durata_reale:.1f} s reali)\n")
    if errore:
        stdout.write(errore)
    risultato = {
        "nome": nome,
        "scenario": scenario,
        "scenario_nome": campo_mod.SCENARI[scenario]["nome"],
        "fine": M.fine,
        "durata": round(M.t, 2),
        "errore": errore,
        "statistiche": M.statistiche,
        "urti": M.urti,
        "campioni": M.campioni,
        "stati": M.stati,
        "eventi": M.eventi,
        "log": M.log,
        "config": {k: v for k, v in M.cfg.items() if k != "guadagni"},
        "punteggio": M.punteggio() if M.nuovo else None,
    }
    with open(os.path.join(QUI, f"replay_{nome}.json"), "w", encoding="utf-8") as f:
        json.dump(risultato, f, ensure_ascii=False)
    return risultato


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stdout.write(__doc__)
        sys.exit(1)
    tmax = float(sys.argv[3]) if len(sys.argv) > 3 else 420.0
    scenario = sys.argv[4] if len(sys.argv) > 4 else "gara"
    esegui(sys.argv[1], sys.argv[2], tmax, scenario=scenario)
