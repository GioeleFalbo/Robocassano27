"""Prova della PORTA D'INGRESSO (FIX 96/101): robot fermo davanti all'ingresso della pista della scuola, spostato di lato.
Porta da y=61,5 a 88,5 (centro 75); robot rivolto verso l'arena (heading 90), 18 cm prima del muro.
Uso: python prova_ingresso.py <cartella versione> <nome> <y del robot> <lato previsto: 1 destra, -1 sinistra, 0 non noto>
Es.: python prova_ingresso.py ../ClaudeRob_V39 ing_95 95 -1      (robot 20 cm a destra della porta: deve andare a sinistra)"""
import sys, os
import comune
src, nome, y, lato = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
cart = comune.copia_con_main(src, "ingresso_" + os.path.basename(os.path.abspath(src)), '''
import os as _os
while not Rwd.GetSwitch()['sw_sof']:
    time.sleep(0.1)
time.sleep(0.5)
IngressoLato = int(_os.environ.get("LATO", "0"))
print("PROVA PORTA: lato previsto", IngressoLato)
EntraDallaPorta(90.0)
Rwd.Stop()
time.sleep(1.0)
''')
import campo, esegui
os.environ["LATO"] = lato
campo.SCENARI["scuola"] = dict(campo.SCENARI["scuola"])
campo.SCENARI["scuola"]["partenza"] = {"x": 192.0, "y": y, "heading": 90.0}
r = esegui.esegui(cart, nome, 150, {"seme": 1}, "scuola")
dentro = any(e["tipo"] == "ok" and "Entrato" in e["testo"] for e in r["eventi"])
print(f"{nome}: y={y} lato={lato} -> {'ENTRATO' if dentro else 'NON entrato'} t={r['durata']:.0f} urti={r['urti']}")
for l in r["log"]:
    if any(k in l[1] for k in ("Ingresso", "apertura", "PROVA", "Entrato")):
        print(f"   {l[0]:6.1f} {l[1][:170]}")
