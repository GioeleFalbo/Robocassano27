#!/usr/bin/env python3
"""Confronto tra due versioni del codice del robot: codice e risultati nel simulatore.
Uso: python3 confronta_versioni.py ClaudeRob_V25 ClaudeRob_V27
     (senza argomenti: le ultime due versioni che hanno una batteria in storico.csv)
Scrive in Confronti/<A>_vs_<B>/: SHURI_confronto.md, confronto.json, confronto.png, codice.diff
"""
import sys, re, json, difflib
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

QUI = Path(__file__).resolve().parent
ROB = QUI.parent
st = pd.read_csv(QUI / "storico.csv", sep=";")
def num(n): return int(re.findall(r"\d+", n)[-1])
if len(sys.argv) >= 3: A, B = sys.argv[1], sys.argv[2]
else:
    vers = sorted(st.codice.unique(), key=num); A, B = vers[-2], vers[-1]
out = QUI / "Confronti" / f"{A}_vs_{B}"; out.mkdir(parents=True, exist_ok=True)

# --- codice ---
da, a = ROB / A, ROB / B
fa = {f.name for f in da.glob("*.py")}; fb = {f.name for f in b.glob("*.py")} if (b := a) else set()
diff_tot, righe_piu, righe_meno, cambiati = [], 0, 0, []
for nome in sorted(fa | fb):
    x = (da / nome).read_text(encoding="utf-8", errors="ignore").splitlines() if nome in fa else []
    y = (a / nome).read_text(encoding="utf-8", errors="ignore").splitlines() if nome in fb else []
    if x == y: continue
    d = list(difflib.unified_diff(x, y, f"{A}/{nome}", f"{B}/{nome}", lineterm="", n=2))
    p = sum(1 for l in d if l.startswith("+") and not l.startswith("+++")); m = sum(1 for l in d if l.startswith("-") and not l.startswith("---"))
    righe_piu += p; righe_meno += m; cambiati.append({"file": nome, "aggiunte": p, "tolte": m, "stato": "nuovo" if nome not in fa else "tolto" if nome not in fb else "modificato"})
    diff_tot += d
(out / "codice.diff").write_text("\n".join(diff_tot), encoding="utf-8")
def fix_set(c): return {int(m) for f in c.glob("*.py") for m in re.findall(r"\[FIX (\d+)\]", f.read_text(encoding="utf-8", errors="ignore"))}
fix_nuovi = sorted(fix_set(a) - fix_set(da))
descr_fix = {}
lm = a / "LEGGIMI_MODIFICHE.md"
if lm.exists():
    for l in lm.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"\s*\|\s*(\d+)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", l)   # tabella: | n | file | cosa | perché |
        if m and int(m.group(1)) in fix_nuovi and int(m.group(1)) not in descr_fix:
            descr_fix[int(m.group(1))] = f"{m.group(3).strip()[:150]} — perché: {m.group(4).strip()[:110]}"

# --- risultati: ultima batteria di ciascuna versione ---
def ultima(v):
    s = st[st.codice == v]
    return s[s.cartella == s.cartella.iloc[-1]].set_index("prova") if len(s) else None
RA, RB = ultima(A), ultima(B)
righe = []
if RA is not None and RB is not None:
    for prova in RB.index:
        ra = RA.loc[prova] if prova in RA.index else None; rb = RB.loc[prova]
        def v(r, k): return None if r is None or pd.isna(r[k]) else r[k]
        pa, pb = v(ra, "punti"), v(rb, "punti")
        righe.append({"prova": prova, "scenario": rb.scenario, "punti_A": pa, "punti_B": pb, "massimo": v(rb, "massimo"),
                      "delta": None if pa is None or pb is None else round(pb - pa, 1),
                      "esito_A": v(ra, "esito"), "esito_B": v(rb, "esito"), "lop_A": v(ra, "lop"), "lop_B": v(rb, "lop"),
                      "urti_A": v(ra, "urti"), "urti_B": v(rb, "urti"), "vittime_A": v(ra, "vittime"), "vittime_B": v(rb, "vittime")})
df = pd.DataFrame(righe)
migliorate = df[df.delta > 0].prova.tolist() if len(df) else []
peggiorate = df[df.delta < 0].prova.tolist() if len(df) else []

# --- grafico ---
if len(df):
    d = df.copy(); d["pA"] = d.punti_A / d.massimo * 100; d["pB"] = d.punti_B / d.massimo * 100
    fig, ax = plt.subplots(figsize=(11, 5.5)); y = range(len(d))
    ax.barh([i - 0.2 for i in y], d.pA.fillna(0), height=0.4, color="#9CA3AF", label=A)
    ax.barh([i + 0.2 for i in y], d.pB.fillna(0), height=0.4, color="#3B75AF", label=B)
    for i, r in d.iterrows():
        txt = "senza punteggio (arena)" if pd.isna(r.massimo) else ("A bloccato/non eseguito" if pd.isna(r.punti_A) else f"{r.delta:+.0f} punti")
        col = "#2E9E5B" if (r.delta or 0) > 0 else "#D1495B" if (r.delta or 0) < 0 else "#6B7280"
        ax.text(max(r.pA if not pd.isna(r.pA) else 0, r.pB if not pd.isna(r.pB) else 0) + 1, i, txt, va="center", fontsize=9, color=col, fontweight="bold")
    ax.set_yticks(list(y)); ax.set_yticklabels(d.prova, fontsize=9); ax.invert_yaxis(); ax.set_xlim(0, 135)
    ax.set_xlabel("% del punteggio massimo"); ax.legend(frameon=False, loc="lower right")
    ax.set_title(f"Confronto {A} → {B} nel simulatore", loc="left", fontweight="bold")
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(out / "confronto.png", dpi=140); plt.close(fig)

res = {"A": A, "B": B, "codice": {"file_cambiati": cambiati, "righe_aggiunte": righe_piu, "righe_tolte": righe_meno, "fix_nuovi": fix_nuovi, "descrizione_fix": descr_fix},
       "risultati": json.loads(df.to_json(orient="records")) if len(df) else [], "migliorate": migliorate, "peggiorate": peggiorate,
       "batteria_A": None if RA is None else RA.cartella.iloc[0], "batteria_B": None if RB is None else RB.cartella.iloc[0]}
(out / "confronto.json").write_text(json.dumps(res, ensure_ascii=False, indent=2, default=str))
md = [f"# Confronto {A} → {B}", "", "![](confronto.png)", "",
      f"## Codice", f"- File cambiati: {len(cambiati)} · righe aggiunte {righe_piu} · tolte {righe_meno} · diff completo in `codice.diff`"]
md += [f"  - `{c['file']}` ({c['stato']}: +{c['aggiunte']} / -{c['tolte']})" for c in cambiati]
md += [f"- FIX nuovi in {B}: " + (", ".join(f"{n}" for n in fix_nuovi) if fix_nuovi else "nessuno")]
md += [f"  - FIX {n}: {descr_fix[n]}" for n in fix_nuovi if n in descr_fix]
md += ["", "## Risultati (ultima batteria di ciascuna versione)", "", f"| Prova | {A} | {B} | Δ punti | LoP | Urti | Vittime |", "|---|---|---|---|---|---|---|"]
for r in righe:
    f = lambda x: "—" if x is None else (f"{x:.0f}" if isinstance(x, float) else str(x))
    md.append(f"| {r['prova']} | {f(r['punti_A'])} ({r['esito_A'] or 'n.e.'}) | {f(r['punti_B'])} ({r['esito_B']}) | {f(r['delta'])} | {f(r['lop_A'])} → {f(r['lop_B'])} | {f(r['urti_A'])} → {f(r['urti_B'])} | {f(r['vittime_A'])} → {f(r['vittime_B'])} |")
md += ["", f"**Migliorate:** {', '.join(migliorate) or 'nessuna'}  ", f"**Peggiorate:** {', '.join(peggiorate) or 'nessuna'}", "",
       "## Commento di Shuri", "(da compilare: quali FIX spiegano i miglioramenti e cosa controllare nelle prove peggiorate)"]
(out / "SHURI_confronto.md").write_text("\n".join(md), encoding="utf-8")
print(json.dumps({"migliorate": migliorate, "peggiorate": peggiorate, "fix_nuovi": fix_nuovi, "file_cambiati": len(cambiati), "righe": [righe_piu, righe_meno]}, ensure_ascii=False))
print("OK", out)
