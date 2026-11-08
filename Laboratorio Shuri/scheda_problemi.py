#!/usr/bin/env python3
"""Scheda dei problemi per Claude (e per i ragazzi).
Uso: python3 scheda_problemi.py [cartella_prove]   (default: l'ultima in Prove/)
Legge riepilogo.json e i replay e scrive nella cartella:
  SHURI_scheda_correzioni.json   -> dati strutturati (una voce per problema)
  SHURI_scheda_correzioni.md   -> la stessa cosa in forma leggibile, con le sezioni "Ipotesi" e "Proposta"
                     da completare da Shuri (le altre parti sono già piene di dati)
"""
import sys, re, json, collections
from pathlib import Path

QUI = Path(__file__).resolve().parent
prove_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else sorted((QUI / "Prove").glob("*_ClaudeRob_V*"))[-1]
riep = json.loads((prove_dir / "riepilogo.json").read_text())
meta = riep["batteria"]
codice_dir = QUI.parent / meta["codice"]
sorgenti = {f.name: f.read_text(encoding="utf-8", errors="ignore").splitlines() for f in sorted(codice_dir.glob("*.py"))}
esiti_lancio = {}
chiuso = prove_dir / "in_corso_chiuso.json"
if chiuso.exists(): esiti_lancio = json.loads(chiuso.read_text()).get("esiti", {})

def dove_nel_codice(riga_log):
    """Trova il print che ha prodotto una riga di log: file, riga, funzione, FIX vicini."""
    testo = riga_log.strip()
    pezzo = re.split(r"[:\d{(]", testo)[0].strip()[:40]
    if len(pezzo) < 3: return []
    trovati = []
    for nome, righe in sorgenti.items():
        for i, r in enumerate(righe):
            if "print" in r and pezzo in r:
                funz = next((righe[j].strip() for j in range(i, -1, -1) if righe[j].lstrip().startswith("def ")), "")
                fix = sorted({int(m) for j in range(max(0, i - 40), min(len(righe), i + 40)) for m in re.findall(r"\[FIX (\d+)\]", righe[j])})
                trovati.append({"file": nome, "riga": i + 1, "funzione": funz[:80], "codice": r.strip()[:120], "fix_vicini": fix})
    return trovati[:3]

def finestra_log(replay, t, prima=4.0):
    return [l for l in replay["log"] if t - prima <= l[0] <= t]

def stampa_ripetuta(log):
    c = collections.Counter(l[1] for l in log)
    if not c: return None
    testo, n = c.most_common(1)[0]
    return {"testo": testo, "volte": n} if n >= 5 and n >= len(log) * 0.5 else None

def comando(p):
    cfg = dict(p["config"])
    return (f"cd ../ClaudeRob_Simulatore_*/ && python3 -c \"import esegui; "
            f"esegui.esegui('../{meta['codice']}', 'riprova_{p['nome']}', {p['secondi']}, {cfg}, '{p['scenario']}')\"")

problemi = []
def aggiungi(**k):
    k["id"] = f"P{len(problemi) + 1}"
    problemi.append(k)

prove = {p["nome"]: p for p in meta["prove"]}
risultati = {r["prova"]: r for r in riep["risultati"]}
for nome, p in prove.items():
    r = risultati.get(nome, {})
    base = {"prova": nome, "descrizione": p["descrizione"], "scenario": p["scenario"], "config": p["config"],
            "come_riprodurre": comando(p)}
    errore = esiti_lancio.get(nome) or p.get("errore_lancio")
    if errore and str(errore).startswith("BLOCCATO"):
        aggiungi(**base, tipo="programma bloccato", gravita="alta", secondo=None,
                 cosa_succede=errore + ". Nessun replay: per capire DOVE si blocca, rilanciare con 120, 240, 360 s e leggere le ultime righe del log.",
                 punti_persi=None, log_prima=[], stampa_ripetuta=None, nel_codice=[],
                 criterio_successo="La gara finisce da sola entro 480 s simulati (arrivo o tempo scaduto) in meno di 60 s reali.")
        continue
    f = prove_dir / f"replay_{nome}.json"
    if not f.exists(): continue
    rep = json.loads(f.read_text())
    if rep.get("errore"):
        righe = rep["errore"].strip().splitlines()
        aggiungi(**base, tipo="errore Python", gravita="alta", secondo=rep["durata"], cosa_succede=righe[-1],
                 punti_persi=None, log_prima=[l[1] for l in finestra_log(rep, rep["durata"])][-10:], stampa_ripetuta=None,
                 nel_codice=[{"traceback": "\n".join(righe[-8:])}], criterio_successo="Nessun errore Python nella stessa prova.")
    punti, massimo = r.get("punti"), r.get("massimo")
    persi_tot = round(massimo - punti, 1) if punti is not None and massimo else None
    for e in rep["eventi"]:
        testo = e["testo"]
        if e["tipo"] == "lop":
            tipo, grav = ("LoP nella zona di evacuazione" if "zona" in testo else "LoP sul percorso"), "alta"
        elif e["tipo"] == "errore" and "FUORI dai triangoli" in testo:
            tipo, grav = "vittima lasciata fuori dal triangolo", "alta"
        elif e["tipo"] == "errore" and "PRIMA delle due vive" in testo:
            tipo, grav = "vittima morta salvata prima delle vive (moltiplicatore perso)", "alta"
        elif e["tipo"] == "errore" and "fermo da" in testo:
            tipo, grav = "robot fermo", "alta"
        elif e["tipo"] == "errore":
            tipo, grav = "errore segnalato dal simulatore", "media"
        else:
            continue
        log = finestra_log(rep, e["t"])
        rip = stampa_ripetuta(log)
        ultime = [l[1] for l in log][-12:]
        luoghi = []
        for l in ([rip["testo"]] if rip else []) + list(dict.fromkeys(reversed(ultime))):
            for d in dove_nel_codice(l):
                if d not in luoghi: luoghi.append(d)
            if len(luoghi) >= 4: break
        aggiungi(**base, tipo=tipo, gravita=grav, secondo=e["t"], cosa_succede=testo, punti_persi=persi_tot,
                 log_prima=ultime, stampa_ripetuta=rip, nel_codice=luoghi,
                 criterio_successo=f"Nella stessa prova ({nome}) l'evento non si ripete e i punti salgono oltre {punti:.0f}." if punti else "L'evento non si ripete nella stessa prova.")
    # gara che non arriva per lentezza (senza eventi gravi): solo osservazione
    if r.get("perc") is not None and r["perc"] < 90 and not any(q["prova"] == nome for q in problemi):
        aggiungi(**base, tipo="punteggio basso senza errori evidenti", gravita="media", secondo=None,
                 cosa_succede=f"{r['punti']:.0f}/{r['massimo']:.0f} punti ({r['perc']}%), esito {r['esito']}", punti_persi=persi_tot,
                 log_prima=[], stampa_ripetuta=None, nel_codice=[], criterio_successo="Punteggio almeno al 90% del massimo.")
    urti = r.get("urti") or 0
    if urti >= 6:
        aggiungi(**base, tipo="molti urti", gravita="bassa", secondo=None, cosa_succede=f"{urti} urti in una gara",
                 punti_persi=None, log_prima=[], stampa_ripetuta=None, nel_codice=[], criterio_successo="Meno di 4 urti nella stessa prova.")

for q in problemi:
    q["ipotesi"] = "(da compilare da Shuri)"
    q["proposta"] = "(da compilare da Shuri)"
ordine = {"alta": 0, "media": 1, "bassa": 2}
problemi.sort(key=lambda q: (ordine[q["gravita"]], q["prova"], q["secondo"] or 0))
for i, q in enumerate(problemi, 1): q["id"] = f"P{i}"
out = {"versione": meta["codice"], "simulatore": meta["simulatore"], "data_batteria": meta["data"], "cartella_codice": f"02_Robotica/{meta['codice']}",
       "medie_per_pista": riep["medie_per_pista"], "problemi": problemi}
(prove_dir / "SHURI_scheda_correzioni.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))

md = [f"# Scheda per Claude — {meta['codice']} (batteria del {meta['data'].replace('T', ' ')})", "",
      "Questo file è scritto per essere letto da Claude (e dai ragazzi) per **migliorare il codice del robot**.",
      "Regole per chi lo usa:",
      f"- Il codice da cui partire è `02_Robotica/{meta['codice']}`: **non modificarlo**. Copialo in una nuova cartella",
      "  `ClaudeRob_V<n+1>`, applica lì le correzioni, segna ogni modifica nel codice con `# [FIX n]` (numerazione",
      "  di `LEGGIMI_MODIFICHE.md`) e aggiorna `CHANGELOG.md` e `LEGGIMI_MODIFICHE.md`.",
      "- Correggi un problema alla volta, partendo da quelli a gravità **alta**.",
      "- Per verificare: ogni problema ha **come riprodurlo** (comando da lanciare nella cartella `Laboratorio Shuri`)",
      "  e un **criterio di successo**. Poi Shuri rifà tutta la batteria e il confronto con questa versione.",
      "- Il simulatore prova la logica del programma: YOLO è un oracolo e alcune misure in CONFIG sono stime.", "",
      "## Medie per pista", "", "| Pista | Prove | Punti medi | % media | LoP totali | Urti medi |", "|---|---|---|---|---|---|"]
for m in riep["medie_per_pista"]:
    md.append(f"| {m['scenario']} | {m['prove']} | {m['punti_medi'] if m['punti_medi'] is not None else '—'} | {m['perc_media'] if m['perc_media'] is not None else '—'} | {m['lop_totali']} | {m['urti_medi']} |")
md += ["", f"## Problemi ({len(problemi)})", ""]
for q in problemi:
    md += [f"### {q['id']} · [{q['gravita'].upper()}] {q['tipo']} — {q['descrizione']}" + (f", secondo {q['secondo']}" if q['secondo'] else ""), "",
           f"- **Cosa succede:** {q['cosa_succede']}"]
    if q.get("punti_persi"): md.append(f"- **Punti persi nella gara:** {q['punti_persi']}")
    if q.get("stampa_ripetuta"): md.append(f"- **Stampa ripetuta prima dell'evento:** \"{q['stampa_ripetuta']['testo']}\" × {q['stampa_ripetuta']['volte']}")
    if q.get("log_prima"):
        md += ["- **Ultime stampe del programma prima dell'evento:**", "  ```"] + [f"  {l}" for l in q["log_prima"]] + ["  ```"]
    if q.get("nel_codice"):
        md.append("- **Dove guardare nel codice:**")
        for d in q["nel_codice"]:
            if "traceback" in d: md += ["  ```", *[f"  {x}" for x in d["traceback"].splitlines()], "  ```"]
            else: md.append(f"  - `{d['file']}` riga {d['riga']} in `{d['funzione']}` → `{d['codice']}`" + (f" (FIX vicini: {', '.join(map(str, d['fix_vicini']))})" if d['fix_vicini'] else ""))
    md += [f"- **Come riprodurlo:** `{q['come_riprodurre']}`", f"- **Criterio di successo:** {q['criterio_successo']}",
           f"- **Ipotesi:** {q['ipotesi']}", f"- **Proposta:** {q['proposta']}", ""]
(prove_dir / "SHURI_scheda_correzioni.md").write_text("\n".join(md), encoding="utf-8")
print(f"{len(problemi)} problemi → {prove_dir / 'SHURI_scheda_correzioni.md'}")
