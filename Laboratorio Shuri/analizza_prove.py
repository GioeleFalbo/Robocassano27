#!/usr/bin/env python3
"""Analisi della batteria di Shuri.
Uso: python3 analizza_prove.py [cartella_prove]   (default: l'ultima in Prove/)
Produce nella cartella: riepilogo.json, risultati.png, replay.html; aggiorna storico.csv
"""
import sys, json, glob, subprocess, collections
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

QUI = Path(__file__).resolve().parent
prove_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else sorted((QUI / "Prove").glob("*_ClaudeRob_V*"))[-1]
meta = json.loads((prove_dir / "batteria.json").read_text())

righe, dettagli = [], {}
for p in meta["prove"]:
    f = prove_dir / f"replay_{p['nome']}.json"
    if not f.exists():
        righe.append({"prova": p["nome"], "descrizione": p["descrizione"], "scenario": p["scenario"], "esito": "NON ESEGUITA", "errore": p.get("errore_lancio")}); continue
    r = json.loads(f.read_text()); s = r.get("punteggio") or {}
    ev = r["eventi"]; tipi = collections.Counter(e["tipo"] for e in ev)
    salv = s.get("salvataggi") or []
    vittime_ok = sum(1 for v in salv if v.get("valido")) if salv else tipi.get("salvata", 0)
    tot, mx = s.get("totale_2026"), s.get("massimo_2026")
    riga = {"prova": p["nome"], "descrizione": p["descrizione"], "scenario": p["scenario"],
            "esito": r["fine"], "tempo_s": r["durata"], "punti": tot, "massimo": mx,
            "perc": round(tot / mx * 100, 1) if tot is not None and mx else None,
            "punti_2027": s.get("totale_2027"), "piastrelle": s.get("piastrelle"),
            "lop": s.get("lop"), "lop_zona": s.get("lop_zona"), "urti": r["urti"],
            "vittime": vittime_ok, "uscita_zona": s.get("uscita_zona", tipi.get("ok", 0) >= 2),
            "arrivato": s.get("arrivato", r["fine"] == "arrivo"), "errore": (r.get("errore") or "")[-600:]}
    righe.append(riga)
    # eventi notevoli: LoP, errori, info, urti (con il log del programma nei 3 s prima di ogni LoP)
    notevoli = []
    for e in ev:
        if e["tipo"] in ("lop", "errore", "caduta", "info", "ko", "avviso"):
            prima = [l[1] for l in r["log"] if e["t"] - 3 <= l[0] <= e["t"]][-6:]
            notevoli.append({"t": e["t"], "tipo": e["tipo"], "testo": e["testo"], "log_prima": prima})
    dettagli[p["nome"]] = {"eventi_notevoli": notevoli,
                           "urti_t": [e["t"] for e in ev if e["tipo"] == "urto"],
                           "punti_mancati": None}
df = pd.DataFrame(righe)

# confronto con la batteria precedente (storico)
storico_f = QUI / "storico.csv"
storico = pd.read_csv(storico_f, sep=";") if storico_f.exists() else pd.DataFrame()
prec = None
if not storico.empty:
    altre = storico[storico.cartella != prove_dir.name]
    if not altre.empty:
        ultima = altre.cartella.iloc[-1]
        prec = altre[altre.cartella == ultima].set_index("prova")
        df["punti_prec"] = df.prova.map(prec["punti"]) if "punti" in prec else None
        df["delta"] = (df.punti - df.punti_prec).round(1)
        df["batteria_prec"] = ultima
nuovo = df[["prova", "scenario", "esito", "tempo_s", "punti", "massimo", "perc", "piastrelle", "lop", "urti", "vittime", "arrivato"]].copy()
nuovo.insert(0, "cartella", prove_dir.name); nuovo.insert(1, "codice", meta["codice"]); nuovo.insert(2, "data", meta["data"])
if not storico.empty: storico = storico[storico.cartella != prove_dir.name]   # rianalisi: niente doppioni
(pd.concat([storico, nuovo], ignore_index=True) if not storico.empty else nuovo).to_csv(storico_f, sep=";", index=False)

# medie per pista
medie = df.groupby("scenario").agg(prove=("prova", "size"), punti_medi=("punti", "mean"), perc_media=("perc", "mean"),
                                   lop_totali=("lop", "sum"), urti_medi=("urti", "mean")).round(1).reset_index()

# grafico
d = df[df.esito != "NON ESEGUITA"].copy()
senza = d.perc.isna()
d.loc[senza, "perc"] = d.loc[senza, "arrivato"].map(lambda a: 100.0 if a else 3.0)
fig, ax = plt.subplots(figsize=(11, 5.2))
col = ["#9CA3AF" if sz else "#2E9E5B" if v >= 95 else "#F2A900" if v >= 75 else "#D1495B" for v, sz in zip(d.perc, senza)]
y = range(len(d))
ax.barh(list(y), d.perc, color=col)
if "punti_prec" in d and d.punti_prec.notna().any():
    pp = (d.punti_prec / d.massimo * 100)
    ax.scatter(pp, list(y), marker="|", s=300, color="black", label="batteria precedente", zorder=3)
    ax.legend(frameon=False, loc="lower right")
for i, (_, r) in enumerate(d.iterrows()):
    if pd.isna(r.punti):
        testo = f"arena senza punteggio: {'uscito e arrivato' if r.arrivato else 'NON arriva (' + str(r.esito) + ')'} · vittime {int(r.vittime)}/3 · urti {int(r.urti)}"
    else:
        testo = f"{r.punti:.0f}/{r.massimo:.0f}  LoP {int(r.lop or 0)} · urti {int(r.urti)} · vittime {int(r.vittime)}" + ("" if r.arrivato else " · non arriva")
    ax.text(min(r.perc, 100) + 0.5, i, testo, va="center", fontsize=8.5)
ax.set_yticks(list(y)); ax.set_yticklabels(d.descrizione, fontsize=9); ax.invert_yaxis()
ax.set_xlim(0, 175); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xlabel("% del punteggio massimo (regolamento 2026)")
ax.set_title(f"Shuri · {meta['codice']} nel {meta['simulatore']} · {meta['data'].replace('T', ' ')}", loc="left", fontweight="bold")
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.grid(axis="x", alpha=0.25); fig.tight_layout(); fig.savefig(prove_dir / "risultati.png", dpi=140); plt.close(fig)

# pagina di replay per vedere come si muove il robot (prove principali + quelle con problemi)
sim = QUI.parent / meta["simulatore"]
scelte = ["rcj2026_s1", "lunga_s1", "contorto_s1", "arena_parete_s1"]
problemi = [r["prova"] for r in righe if r.get("lop") or (r.get("perc") is not None and r["perc"] < 90) or r.get("errore")]
args = []
for n in dict.fromkeys(scelte + problemi):
    f = prove_dir / f"replay_{n}.json"
    if f.exists():
        desc = next(p["descrizione"] for p in meta["prove"] if p["nome"] == n)
        args.append(f"{f}:{meta['codice']} · {desc}")
try:
    subprocess.run(["python3", str(sim / "crea_replay.py"), str(prove_dir / "replay.html"), *args], cwd=sim, check=True, capture_output=True, timeout=170)
except Exception as e:
    print("replay non creato:", e)

out = {"batteria": meta, "risultati": json.loads(df.to_json(orient="records")), "medie_per_pista": json.loads(medie.to_json(orient="records")),
       "dettagli": dettagli, "batteria_precedente": None if prec is None else df.get("batteria_prec", pd.Series([None])).iloc[0]}
(prove_dir / "riepilogo.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(df[["prova", "esito", "punti", "massimo", "perc", "lop", "urti", "vittime", "arrivato"]].to_string(index=False))
print("\nMEDIE\n", medie.to_string(index=False))
print("\nOK", prove_dir)
