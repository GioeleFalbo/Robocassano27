#!/bin/bash
# ============================================================
#  SIMULATORE ClaudeRob - doppio clic nel Finder (Mac, anche M1/M2/M3)
#  Dal Terminale:  ./SIMULA.command [campo] [cartella del codice]
#    campo: scuola_nuova (se non lo scrivete: la pista della scuola a piastrelle), scuola_nuova_buio, rcj2026, lunga, contorto, gara, arena, arena_parete, scuola, scuola_rampa, scuola_basso, scuola_parete
#    codice: ../ClaudeRob_V41 (se non lo scrivete)
# ============================================================
cd "$(dirname "$0")" || exit 1
CAMPO="${1:-scuola_nuova}"
CODICE="${2:-../ClaudeRob_V41}"

if ! command -v python3 >/dev/null 2>&1; then
    echo "Manca Python 3: installatelo da python.org (versione per macOS) e riprovate."
    read -r -p "Premete Invio per chiudere"
    exit 1
fi
# ambiente Python tutto dentro questa cartella (.venv): non tocca il resto del Mac
if [ ! -x .venv/bin/python ]; then
    echo "Prima volta: preparo l'ambiente Python..."
    python3 -m venv .venv || { read -r -p "Errore. Premete Invio per chiudere"; exit 1; }
fi
if ! .venv/bin/python -c "import numpy, cv2" >/dev/null 2>&1; then
    echo "Prima volta: installo numpy e opencv-python (serve internet)..."
    .venv/bin/python -m pip install --upgrade pip >/dev/null
    .venv/bin/python -m pip install numpy opencv-python || { read -r -p "Errore. Premete Invio per chiudere"; exit 1; }
fi
if [ ! -f "$CODICE/RwdFoto.py" ]; then
    echo "Non trovo $CODICE/RwdFoto.py"
    echo "Mettete la cartella del codice del robot accanto a questa, oppure scrivete il percorso:"
    echo "  ./SIMULA.command scuola_nuova \"/percorso/ClaudeRob_V41\""
    read -r -p "Premete Invio per chiudere"
    exit 1
fi
echo "Gara simulata sul campo $CAMPO con il codice in $CODICE ..."
.venv/bin/python esegui.py "$CODICE" "prova_$CAMPO" 480 "$CAMPO"
.venv/bin/python crea_replay.py "prova_$CAMPO.html" "replay_prova_$CAMPO.json:Prova $CAMPO"
open "prova_$CAMPO.html"
