# Pezzi stampati del robot (STL)

Mandati dal prof in chat il 5 novembre 2026. Unità: millimetri.

| File | Triangoli | Ingombro (mm) |
|---|---|---|
| `BaseLogica.stl` | 1808 | 154 x 26 x 157 |
| `ServoRWDAmmortizzato.stl` | 7114 | 202 x 8 x 151 |
| `CoperturaAlta.stl` | 4332 | 183 x 36 x 154 |
| `SupportoPinzaWebcam_1.stl` | 4556 | 61 x 67 x 157 |
| `CupolaWebArenaLED.stl` | 1282 | 8 x 52 x 148 |
| `Braccio.stl` | 3694 | 79 x 90 x 59 |

`Braccio.stl` (mandato il 10/11, nome originale `0Servo4WDFisso2006PinzaMonoVaccaro.stl`) **non è nelle coordinate di
montaggio** degli altri: è disegnato con il braccio abbassato. Il perno è il centro del disco per la squadretta del servo DM996
(X 41,7, Y 74,6, Z -372,4 nelle sue coordinate). Nell'esploso viene messo sul davanti a sinistra, in posizione indicativa, e
si alza e abbassa con il cursore "Braccio". Manca ancora lo STL della pinza.

## Componenti (modelli semplificati)

In `componenti/` ci sono i modelli 3D **semplificati** (scatole e cilindri con le misure dei datasheet, valori indicativi) di
servo FS5106R, servo DM996, Arduino Nano, PCA9685 a 16 canali, buck DC-DC (tipo LM2596), LiPo Zeee 3S 2200 mAh, Raspberry Pi 5
e scheda a 2 relè. Li costruisce
`python3 .claude/skills/anatomia/componenti.py`: sono nostri, nessun problema di licenza. Servono per gli ingombri e
l'esploso, non per stampare. Nell'esploso sono montati ai tre livelli (dal prof): livello 1 batteria e buck, livello 2 le due
PCA9685 e l'Arduino, livello 3 Raspberry Pi 5 e relè (il punto preciso nel livello è indicativo). Se trovate i modelli
ufficiali si possono sostituire con lo stesso nome.

**Esploso 3D**: `esploso_robot.html` (doppio clic) mostra i pezzi che si smontano con un cursore; clic su un pezzo per la
sua scheda. Si rigenera con `python3 .claude/skills/anatomia/costruisci_esploso.py`.

Il modello 3D del cruscotto (`ClaudeRob_V39/cruscotto/robot.stl`, 19092 triangoli) è fatto con questi 5 pezzi messi insieme.
