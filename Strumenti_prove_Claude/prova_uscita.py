"""Prova della PORTA D'USCITA (FIX 103): robot squadrato sulla striscia nera dell'uscita della scuola ma spostato di lato.
Uscita sul muro basso, x da 239,5 a 266,5 (centro 253). La striscia nera è corta (6 cm) sotto il robot, così la centratura
non vede lo spostamento; un muro di prova fuori dalla porta dà al laser davanti qualcosa da misurare.
Uso: python prova_uscita.py <cartella versione> <nome> <spostamento cm> [gradi storto]
Es.: python prova_uscita.py ../ClaudeRob_V39 usc_10 10"""
import sys, os
import comune
src, nome, off = sys.argv[1], sys.argv[2], float(sys.argv[3])
ang = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
cart = comune.copia_con_main(src, "uscita_" + os.path.basename(os.path.abspath(src)), '''
while not Rwd.GetSwitch()['sw_sof']:
    time.sleep(0.1)
time.sleep(0.5)
print("PROVA USCITA")
print("ESITO USCITA:", EsciControllando(180.0, RwdConf.TempoUscitaPorta, nero_gia_visto=True))
Rwd.Stop()
time.sleep(1.0)
''')
import campo, esegui
_orig = campo.crea_campo
def _crea(n):
    C = _orig(n)
    C["nero_uscita"] = {"x": 253.0 + off - 3.0, "y": C["nero_uscita"]["y"], "w": 6.0, "h": C["nero_uscita"]["h"]}
    C["muri"] = list(C["muri"]) + [((225.0, 150.0), (285.0, 150.0))]
    return C
campo.crea_campo = _crea
campo.SCENARI["scuola"] = dict(campo.SCENARI["scuola"])
campo.SCENARI["scuola"]["partenza"] = {"x": 253.0 + off, "y": 104.0, "heading": 180.0 + ang}
r = esegui.esegui(cart, nome, 120, {"seme": 1}, "scuola")
u = comune.replay(nome)["campioni"][-1]
print(f"{nome}: off={off} ang={ang} -> {'USCITO' if u[2] > 128 else 'NON uscito'} (y finale {u[2]:.0f}) t={r['durata']:.0f} urti={r['urti']}")
for l in r["log"]:
    if any(k in l[1] for k in ("Uscita", "Uscendo", "Uscito", "ESITO", "stipite")):
        print(f"   {l[0]:6.1f} {l[1][:170]}")
