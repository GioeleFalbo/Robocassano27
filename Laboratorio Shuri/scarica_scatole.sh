#!/bin/bash
# =====================================================================================================
#  Shuri · copia le SCATOLE NERE dal robot vero in 02_Robotica/ScatoleNere/
#
#  Uso (dalla cartella "Laboratorio Shuri"):
#     ./scarica_scatole.sh                       dal robot in rete (indirizzo in robot.conf o qui sotto)
#     ./scarica_scatole.sh pi@192.168.2.221      da un indirizzo preciso
#     ./scarica_scatole.sh /Volumes/CHIAVETTA    da una cartella (chiavetta USB, OneDrive...): copia i run_*.jsonl
#
#  Non cancella MAI niente, né sul robot né sul Mac: copia solo i file che mancano.
#  Dal robot in rete serve, UNA VOLTA SOLA, la chiave SSH (così Shuri non deve scrivere la password):
#     ssh-keygen -t ed25519        (Invio a tutte le domande, se non l'avete già)
#     ssh-copy-id pi@<indirizzo del robot>
#  L'indirizzo del robot si vede nel terminale del robot e nel cruscotto ("cruscotto http://...").
#  Uscita: 0 = copiate (o nessuna nuova), 1 = robot o cartella non raggiungibile.
# =====================================================================================================
QUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$QUI/../ScatoleNere"
CARTELLA_ROBOT="/home/pi/OneDrive/ScatolaNera/"     # CARTELLA_SCATOLA in ViennaDataConf.py
ROBOT="pi@192.168.2.221"                             # indirizzo visto nella scatola nera del 29/10
[ -f "$QUI/robot.conf" ] && source "$QUI/robot.conf"   # robot.conf può contenere: ROBOT="pi@..."
SORGENTE="${1:-$ROBOT}"
mkdir -p "$DEST"
prima=$(ls "$DEST"/run_*.jsonl 2>/dev/null | wc -l | tr -d ' ')

if [ -d "$SORGENTE" ]; then
    echo "Copio le scatole nere dalla cartella $SORGENTE"
    find "$SORGENTE" -maxdepth 2 \( -name 'run_*.jsonl' -o -name 'run_*.txt' \) -print0 |
        while IFS= read -r -d '' f; do
            [ -e "$DEST/$(basename "$f")" ] || cp -p "$f" "$DEST/"
        done
else
    echo "Copio le scatole nere dal robot $SORGENTE ($CARTELLA_ROBOT)"
    if ! ssh -o ConnectTimeout=6 -o BatchMode=yes "$SORGENTE" "test -d $CARTELLA_ROBOT" 2>/dev/null; then
        echo "ROBOT NON RAGGIUNGIBILE: $SORGENTE"
        echo "  - il robot è acceso e sulla stessa rete Wi-Fi del Mac?"
        echo "  - l'indirizzo è giusto? (scrivetelo in robot.conf: ROBOT=\"pi@<indirizzo>\")"
        echo "  - la chiave SSH è stata copiata? (ssh-copy-id $SORGENTE, una volta sola)"
        exit 1
    fi
    rsync -a --ignore-existing --include='run_*.jsonl' --include='run_*.txt' --exclude='*' \
          -e "ssh -o ConnectTimeout=6 -o BatchMode=yes" "$SORGENTE:$CARTELLA_ROBOT" "$DEST/" || exit 1
fi
dopo=$(ls "$DEST"/run_*.jsonl 2>/dev/null | wc -l | tr -d ' ')
echo "FATTO: $((dopo - prima)) scatole nere nuove in $DEST (in tutto $dopo)"
