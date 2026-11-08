#!/bin/bash
# Doppio clic a fine laboratorio (robot acceso e sulla stessa rete del Mac):
# copia le scatole nere nuove dal robot in 02_Robotica/ScatoleNere/. Non cancella niente.
# La prima volta: tasto destro sul file -> Apri -> Apri (macOS chiede conferma una volta sola).
# Serve la chiave SSH, una volta sola, dal Terminale:  ssh-copy-id pi@<indirizzo del robot>
cd "$(dirname "$0")" || exit 1
bash scarica_scatole.sh "$@"
echo
read -r -p "Premi Invio per chiudere questa finestra"
