# Avvio del robot con l'ultima versione

`avvia_ultima_versione.sh` (12/11) fa partire il robot **sempre con l'ultima versione** copiata sul Raspberry. Così non
serve più il comando `ln -sfn ... ~/ClaudeRob_GARA` a ogni versione nuova.

A ogni accensione:
1. sceglie la cartella `~/ClaudeRob_V<n>` con il **numero più alto** che contiene `RwdFoto.py` (una cartella vuota o
   copiata a metà viene saltata; nomi come `ClaudeRob_V46_copia` vengono ignorati);
2. se mancano, ci copia i **4 modelli YOLO** da `/home/pi`;
3. rende eseguibile `avvia.sh`;
4. sposta `~/ClaudeRob_GARA` su quella cartella, scrive quale versione parte (con l'impronta) e la fa partire.

Quello che fa lo scrive anche in `~/avvio_robot.log`. Non cancella niente.

## Restare su una versione (per esempio per tornare indietro)

```
echo ClaudeRob_V43 > ~/ClaudeRob_FISSA
```
Finché c'è questo file parte quella versione. Per tornare all'ultima: `rm ~/ClaudeRob_FISSA`.

## Metterlo sul robot (una volta sola)

Dal terminale del robot (`pi@master:~ $`):
```
curl -L -o ~/avvia_ultima_versione.sh https://raw.githubusercontent.com/Giooooonni93/Robocassano27/main/Raspberry/avvia_ultima_versione.sh
chmod +x ~/avvia_ultima_versione.sh
cp ~/.config/labwc/autostart ~/.config/labwc/autostart.prima_del_12nov_ultima
echo 'env LANG=C.UTF-8 LC_ALL=C.UTF-8 lxterminal --geometry=120x40 -e /home/pi/avvia_ultima_versione.sh &' > ~/.config/labwc/autostart
```
Poi `sudo reboot`. Per tornare all'avvio di prima:
`cp ~/.config/labwc/autostart.prima_del_12nov_ultima ~/.config/labwc/autostart`.

## Avviarlo a mano dal terminale del robot (in VNC, non da SSH)

```
env LANG=C.UTF-8 LC_ALL=C.UTF-8 ~/avvia_ultima_versione.sh
```
Prima controllate che non stia già girando: `pgrep -af RwdFoto`.
