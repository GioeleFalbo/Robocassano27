"""Una gara nel simulatore con un riassunto corto.
Uso: python gira.py <cartella versione> <nome> <scenario> [tmax] [seme=2] [altri parametri cfg=valore]
Es.: python gira.py ../ClaudeRob_V39 prova scuola 480 seme=3"""
import sys
import comune, esegui
cart, nome, scen = sys.argv[1], sys.argv[2], sys.argv[3]
tmax = float(sys.argv[4]) if len(sys.argv) > 4 and "=" not in sys.argv[4] else 480
cfg = {"seme": 1}
for a in sys.argv[4:]:
    if "=" in a:
        k, v = a.split("=")
        cfg[k] = float(v)
r = esegui.esegui(cart, nome, tmax, cfg, scen)
p = r.get("punteggio") or {}
out = [f"{nome}: fine={r['fine']} t={r['durata']:.0f} urti={r['urti']} PUNTI={p.get('totale_2026')} LoP={p.get('lop')}"]
for e in r["eventi"]:
    if e["tipo"] in ("lop", "errore"):
        out.append(f"   {e['t']:6.1f} {e['tipo']}: {e['testo'][:100]}")
for l in r["log"]:
    if any(k in l[1] for k in ("ARENA", "Ingresso", "USCITA", "Uscita", "giro a SINISTRA", "giro a DESTRA", "dietrofront", "ALTALENA")):
        out.append(f"      {l[0]:6.1f} {l[1][:110]}")
sys.__stdout__.write("\n".join(out[:80]) + "\n")
