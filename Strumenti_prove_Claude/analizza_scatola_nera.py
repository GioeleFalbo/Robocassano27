"""Riassunto di una scatola nera vera (run_*.jsonl): intestazione, eventi (senza quelli ripetuti) e campioni in un intervallo.
Uso: python -I analizza_scatola_nera.py <file.jsonl> [da_s a_s]
Es.: python -I analizza_scatola_nera.py ../ScatoleNere/run_2026-11-06_10-48-52_V38.jsonl 236 292"""
import json, sys
recs = []
for l in open(sys.argv[1], errors="replace"):
    l = l.strip().strip("\x00")
    if l:
        try:
            recs.append(json.loads(l))
        except Exception:
            pass
h = recs[0]
print(h.get("versione"), h.get("impronta"), h.get("cartella_codice"))
c = [r for r in recs if r.get("tipo") == "c"]
print("campioni", len(c), "durata", c[-1]["t"] if c else 0)
if len(sys.argv) > 3:
    a, b = float(sys.argv[2]), float(sys.argv[3])
    last = 0
    for r in recs:
        if r.get("tipo") == "c" and a < r["t"] < b and r["t"] - last > 0.25:
            last = r["t"]
            print(f"{r['t']:7.2f} d={r['d']} imu={r['imu']} mot={r['mot']} y={r['yolo']} | {r['stato'][-30:]} | {r['msg'][:60]}")
        if r.get("tipo") == "evento" and a < r["t"] < b:
            print("   EV", r["t"], r["testo"][:130])
else:
    prev = None
    for r in recs[1:]:
        if r.get("tipo") == "evento":
            t = r["testo"]
            if "Qualcosa davanti" in t or "Non è un ostacolo" in t or t == prev:
                continue
            prev = t
            print(f"{r['t']:7.2f} [{r['cat'][:5]}] {t[:140]}")
