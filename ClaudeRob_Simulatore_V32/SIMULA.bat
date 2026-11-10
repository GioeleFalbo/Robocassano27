@echo off
rem ============================================================
rem  SIMULATORE ClaudeRob - doppio clic per una gara simulata
rem  Da terminale:  SIMULA.bat [campo] [cartella del codice]
rem    campo: scuola_nuova (se non lo scrivete: la pista della scuola a piastrelle), scuola_nuova_buio, rcj2026, lunga, contorto, gara, arena, arena_parete, scuola, scuola_rampa, scuola_basso, scuola_parete
rem    codice: ..\ClaudeRob_V41 (se non lo scrivete)
rem ============================================================
cd /d "%~dp0"
set CAMPO=%~1
if "%CAMPO%"=="" set CAMPO=scuola_nuova
set CODICE=%~2
if "%CODICE%"=="" set CODICE=..\ClaudeRob_V41

set PY=python
where py >nul 2>nul && set PY=py

%PY% -c "import numpy, cv2" >nul 2>nul
if errorlevel 1 (
    echo Prima volta: installo numpy e opencv-python...
    %PY% -m pip install numpy opencv-python
)

if not exist "%CODICE%\RwdFoto.py" (
    echo Non trovo %CODICE%\RwdFoto.py
    echo Mettete la cartella del codice del robot accanto a questa, oppure scrivete il percorso:
    echo   SIMULA.bat scuola_nuova "C:\percorso\ClaudeRob_V41"
    pause
    exit /b 1
)

echo Gara simulata sul campo %CAMPO% con il codice in %CODICE% ...
%PY% esegui.py "%CODICE%" prova_%CAMPO% 480 %CAMPO%
%PY% crea_replay.py prova_%CAMPO%.html replay_prova_%CAMPO%.json:"Prova %CAMPO%"
start "" "prova_%CAMPO%.html"
pause
