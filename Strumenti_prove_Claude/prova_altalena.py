"""Prova dell'ALTALENA (FIX 102/104): mette nello storico del beccheggio uno "stoppie" finto (+21 -> -49 gradi) e chiama
ControllaAltalena. Il simulatore non ha l'altalena.
Uso: python prova_altalena.py <cartella versione> <nome>"""
import sys, os
import comune
src, nome = sys.argv[1], sys.argv[2]
cart = comune.copia_con_main(src, "altalena_" + os.path.basename(os.path.abspath(src)), '''
while not Rwd.GetSwitch()['sw_sof']:
    time.sleep(0.1)
time.sleep(0.5)
_, _, h = Rwd.GetGyro()
adesso = time.time()
finto = [(adesso - 1.0 + 0.1 * k, b, h) for k, b in enumerate([20, 21, 21, 20, 18, 10, -25, -45, -49, -30, 0])]
with Rwd._lock:
    Rwd._storia_becc[:] = finto
print("risultato:", ControllaAltalena())
print("di nuovo subito (deve essere False):", ControllaAltalena())
Rwd.Stop()
''')
import esegui
r = esegui.esegui(cart, nome, 60, {"seme": 1}, "rcj2026")
for t, m in r["log"]:
    if any(k in m for k in ("ALTALENA", "Altalena", "risultato", "di nuovo")):
        print(f"  {t:6.1f} {m[:150]}")
