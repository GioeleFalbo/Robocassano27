"""Prova dell'USCITA ALL'ANGOLO (FIX 104): seguendo il muro sinistro dell'arena della scuola il robot vede la striscia nera
davanti, ma è davanti al muro accanto alla porta (porta da x=239,5). Chiama EsciDallaPortaDavanti come il giro dei muri.
Uso: python prova_uscita_angolo.py <cartella versione> <nome> <x del robot: 222-234>
Es.: python prova_uscita_angolo.py ../ClaudeRob_V39 ang_230 230"""
import sys, os
import comune
src, nome, x = sys.argv[1], sys.argv[2], float(sys.argv[3])
cart = comune.copia_con_main(src, "angolo_" + os.path.basename(os.path.abspath(src)), '''
import os as _os
while not Rwd.GetSwitch()['sw_sof']:
    time.sleep(0.1)
time.sleep(0.5)
print("PROVA ANGOLO")
print("ESITO ANGOLO:", EsciDallaPortaDavanti(-1, 180.0, float(_os.environ.get("MURO", "10"))))
Rwd.Stop()
time.sleep(1.0)
''')
import campo, esegui
os.environ["MURO"] = str(x - 210 - 7.8)
_orig = campo.crea_campo
def _crea(n):
    C = _orig(n)
    C["muri"] = list(C["muri"]) + [((225.0, 150.0), (285.0, 150.0))]
    return C
campo.crea_campo = _crea
campo.SCENARI["scuola"] = dict(campo.SCENARI["scuola"])
campo.SCENARI["scuola"]["partenza"] = {"x": x, "y": 106.0, "heading": 180.0}
r = esegui.esegui(cart, nome, 150, {"seme": 1}, "scuola")
u = comune.replay(nome)["campioni"][-1]
print(f"{nome}: x={x} -> {'USCITO' if u[2] > 128 else 'NON uscito'} (finale x {u[1]:.0f} y {u[2]:.0f}) t={r['durata']:.0f} urti={r['urti']}")
for l in r["log"]:
    if any(k in l[1] for k in ("Uscita", "Uscendo", "Uscito", "ESITO", "Esco", "Striscia")):
        print(f"   {l[0]:6.1f} {l[1][:170]}")
