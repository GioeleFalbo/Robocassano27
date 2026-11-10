#!/usr/bin/env python3
"""Modelli 3D SEMPLIFICATI dei componenti elettronici e meccanici del robot (servo, schede, batteria, buck).

Uso (dalla cartella principale della repository):
    python3 .claude/skills/anatomia/componenti.py

Scrive gli STL in Meccanica_STL/componenti/ (millimetri). Sono blocchi fatti di scatole e cilindri con le misure dei
datasheet (valori indicativi, da controllare con il calibro): servono a capire ingombri e posizioni nell'esploso, non a
stampare. Li abbiamo costruiti noi: nessun problema di licenza. Se trovate i modelli ufficiali (STEP/STL), si possono
sostituire tenendo lo stesso nome del file.
Coordinate: Y in alto, il pezzo appoggiato su Y = 0 e centrato su X e Z.
"""
import math, os, struct

QUI = os.path.dirname(os.path.abspath(__file__))
USCITA = os.path.abspath(os.path.join(QUI, "..", "..", "..", "Meccanica_STL", "componenti"))


def scatola(x0, y0, z0, dx, dy, dz):
    """Parallelepipedo con lo spigolo minimo in (x0, y0, z0): 12 triangoli."""
    p = [(x0 + i * dx, y0 + j * dy, z0 + k * dz) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    facce = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    tri = []
    for a, b, c, d in facce:
        tri += [(p[a], p[b], p[c]), (p[a], p[c], p[d])]
    return tri


def cilindro(cx, y0, cz, r, h, n=24):
    """Cilindro verticale (asse Y) con la base a y0."""
    tri = []
    for i in range(n):
        a1, a2 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p1, p2 = (cx + r * math.cos(a1), cz + r * math.sin(a1)), (cx + r * math.cos(a2), cz + r * math.sin(a2))
        b1, b2, t1, t2 = (p1[0], y0, p1[1]), (p2[0], y0, p2[1]), (p1[0], y0 + h, p1[1]), (p2[0], y0 + h, p2[1])
        tri += [(b1, b2, t2), (b1, t2, t1), ((cx, y0, cz), b2, b1), ((cx, y0 + h, cz), t1, t2)]
    return tri


def servo(L, W, H, flangia_L, flangia_y, perno_da_bordo):
    """Servo di formato standard: corpo, alette di fissaggio, albero e disco della squadretta."""
    t = scatola(-L / 2, 0, -W / 2, L, H, W)
    t += scatola(-flangia_L / 2, flangia_y, -W / 2, flangia_L, 2.5, W)
    px = -L / 2 + perno_da_bordo
    t += cilindro(px, H, 0, 3, 5) + cilindro(px, H + 5, 0, 10, 2)
    return t


def scheda(L, W, pezzi):
    """Circuito stampato 1,6 mm + componenti (scatole) sopra."""
    t = scatola(-L / 2, 0, -W / 2, L, 1.6, W)
    for (x, z, dx, dz, h) in pezzi:
        t += scatola(-L / 2 + x, 1.6, -W / 2 + z, dx, h, dz)
    return t


# nome file -> (descrizione, triangoli)
MODELLI = {
    # Feetech FS5106R (datasheet): 40,8 x 20,1 x 38,0 mm, alette 54 mm a circa 28 mm da sotto
    "Servo_FS5106R.stl": servo(40.8, 20.1, 38.0, 54.0, 27.5, 10.0),
    # DM996 (formato MG996R): 40,7 x 19,7 x 42,9 mm, alette 54 mm a circa 30 mm
    "Servo_DM996.stl": servo(40.7, 19.7, 42.9, 54.0, 30.0, 10.0),
    # Arduino Nano: 45 x 18 mm, porta USB su un lato corto, chip al centro
    "Arduino_Nano.stl": scheda(45, 18, [(0, 5, 9, 8, 4), (19, 5.5, 7, 7, 1.5), (3, 0, 38, 2.5, 2.5), (3, 15.5, 38, 2.5, 2.5)]),
    # PCA9685 16 canali (formato Adafruit): 62,5 x 25,4 mm, 16 connettori a 3 pin, morsetto di alimentazione
    "PCA9685_16canali.stl": scheda(62.5, 25.4, [(10, 0, 41, 7.6, 8.5), (26, 16, 10, 8, 10), (20, 12, 8, 8, 1.5)]),
    # Buck DC-DC tipo LM2596 (scheda blu con bobina, dalla foto): 43 x 21 mm
    "Buck_DCDC.stl": scheda(43, 21, [(26, 6, 9, 9, 9), (3, 3, 6, 6, 1)])
                     + cilindro(-43 / 2 + 15, 1.6, 0, 6, 8) + cilindro(-43 / 2 + 5, 1.6, 4, 4, 10)
                     + cilindro(43 / 2 - 5, 1.6, 4, 4, 10),
    # Raspberry Pi 5: 85 x 56 mm; su un lato corto Ethernet e 2 doppie USB, chip al centro
    "Raspberry_Pi_5.stl": scheda(85, 56, [(66, 2, 21, 16, 13.5), (66, 20, 17, 14, 16), (66, 38, 17, 14, 16),
                                          (25, 20, 15, 15, 2.5), (8, 3, 51, 5, 8.5)]),
    # scheda a 2 relè (blu, dalla foto): circa 50 x 38 mm, due relè e i morsetti
    "Rele_2_canali.stl": scheda(50, 38, [(6, 3, 19, 15.5, 15), (6, 20, 19, 15.5, 15), (30, 3, 8, 32, 10)]),
    # LiPo Zeee 3S 2200 mAh 50C: circa 106 x 34 x 25 mm (da misurare), cavi di bilanciamento e di potenza
    "LiPo_Zeee_3S_2200.stl": scatola(-53, 0, -17, 106, 25, 34) + scatola(53, 8, -8, 12, 8, 4) + scatola(53, 8, 4, 8, 5, 4),
}


def scrivi(nome, tri):
    with open(os.path.join(USCITA, nome), "wb") as f:
        f.write(nome.encode()[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(tri)))
        for a, b, c in tri:
            f.write(struct.pack("<12fH", 0, 0, 0, *a, *b, *c, 0))


if __name__ == "__main__":
    os.makedirs(USCITA, exist_ok=True)
    for nome, tri in MODELLI.items():
        scrivi(nome, tri)
        print(f"{nome}: {len(tri)} triangoli")
    print("FATTO:", os.path.relpath(USCITA, os.path.join(QUI, "..", "..", "..")))
