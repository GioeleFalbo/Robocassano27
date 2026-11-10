"""
FINTO HARDWARE: sostituisce le librerie del Raspberry con versioni simulate.
Il vostro codice (ViennaClsRobot.py, ViennaClsWebCam.py, RwdFoto.py) NON viene modificato:
crede di parlare con PCA9685, Arduino, PiCamera e YOLO, invece parla con il mondo simulato.

  smbus2      -> registra gli impulsi scritti sulle due PCA9685
  serial      -> finta porta dell'Arduino (i dati dei sensori arrivano dal mondo simulato)
  gpiozero    -> LED sui relè
  picamera2   -> le due telecamere (immagini disegnate dal simulatore)
  ultralytics -> "YOLO oracolo": risponde con quello che c'è davvero davanti alla camera
  time        -> tempo VIRTUALE: time.sleep fa avanzare la simulazione
"""
import builtins
import os
import glob
import sys
import threading
import time
import types

import cv2
import numpy as np

_vero_print = builtins.print
_vero_sleep = time.sleep
_vero_time = time.time
_vero_start = threading.Thread.start


def ripristina():
    """Rimette a posto print, time e thread dopo la simulazione."""
    builtins.print = _vero_print
    time.sleep = _vero_sleep
    time.time = _vero_time
    threading.Thread.start = _vero_start


def installa(mondo):
    M = mondo

    # ---------------- tempo virtuale ----------------
    time.sleep = lambda s: M.avanza(float(s))
    time.time = lambda: 1_700_000_000.0 + M.t

    # ---------------- print -> log del replay ----------------
    def finto_print(*args, sep=" ", end="\n", file=None, flush=False):
        M.scrivi_log(sep.join(str(a) for a in args))
    builtins.print = finto_print

    # ---------------- thread di lettura: li sostituisce il simulatore ----------------
    _start = threading.Thread.start

    def start(self):
        nome = getattr(getattr(self, "_target", None), "__name__", "")
        if nome in ("_arduino_reader", "_bt_reader", "Cattura", "_scrittore_foto"):
            return          # i sensori e la camera li aggiorna direttamente il mondo simulato
        return _start(self)
    threading.Thread.start = start

    # ---------------- smbus2 (PCA9685) ----------------
    class SMBus:
        def __init__(self, n):
            self.mode = {}

        def write_byte_data(self, addr, reg, val):
            if reg == 0xFD and val & 0x10:
                M.spegni_tutto(addr)
            self.mode[(addr, reg)] = val

        def read_byte_data(self, addr, reg):
            return self.mode.get((addr, reg), 0)

        def write_i2c_block_data(self, addr, reg, data):
            ch = (reg - 0x06) // 4
            off = data[2] | (data[3] << 8)
            M.scrivi_pwm(addr, ch, off)
    sys.modules["smbus2"] = types.SimpleNamespace(SMBus=SMBus)

    # ---------------- gpiozero ----------------
    class LED:
        def __init__(self, pin):
            self.pin = pin
            self._v = 0

        @property
        def value(self):
            return self._v

        @value.setter
        def value(self, v):
            self._v = v
            M.led[self.pin] = (v == 0)      # relè attivo basso: value = 0 -> LED acceso
    sys.modules["gpiozero"] = types.SimpleNamespace(LED=LED)

    # ---------------- serial ----------------
    class SerialException(Exception):
        pass

    class Serial:
        def __init__(self, port, baud=9600, timeout=0):
            if "rfcomm" in port:
                raise SerialException("Bluetooth non presente nel simulatore")
            self.port = port

        in_waiting = 0

        def read(self, n):
            return b""

        def reset_input_buffer(self):
            pass

        def close(self):
            pass
    sys.modules["serial"] = types.SimpleNamespace(Serial=Serial, SerialException=SerialException)
    _glob = glob.glob
    glob.glob = lambda p, *a, **k: ["/dev/ttyUSB0"] if "ttyUSB" in p else ([] if "ttyACM" in p else _glob(p, *a, **k))

    # ---------------- picamera2 / libcamera ----------------
    class Controlli:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class Picamera2:
        def __init__(self, idx=0):
            self.idx = idx
            self.controls = Controlli()

        def create_preview_configuration(self, **k):
            return {}

        def configure(self, c):
            pass

        def start(self):
            pass

        def stop(self):
            pass

        def set_controls(self, c):
            pass

        def capture_metadata(self):
            return {"ExposureTime": 6000, "AnalogueGain": 1.4}

        def capture_array(self):
            if self.idx == 0:       # camera della linea (IdCamSL = 0)
                M.frame_pose = (M.x, M.y, M.h)
                return M.immagine_linea(M.frame_pose)
            M.arena_pose = (M.x, M.y, M.h)       # camera dell'arena (IdCamAr = 1)
            M.yolo_vista = ""                    # la camera della linea non viene interrogata
            return M.immagine_arena()

    sys.modules["picamera2"] = types.SimpleNamespace(Picamera2=Picamera2, Preview=None)
    sys.modules["libcamera"] = types.SimpleNamespace(
        controls=types.SimpleNamespace(AfModeEnum=types.SimpleNamespace(Continuous=2, Manual=0)),
        Transform=lambda **k: dict(k))

    # ---------------- ultralytics: YOLO "oracolo" ----------------
    class Valori(list):
        pass

    class Box:
        def __init__(self, cls, conf, xyxy):
            self.cls = [cls]
            self.conf = [conf]
            self.xyxy = [Valori(xyxy)]

    class Risultato:
        def __init__(self, boxes, img):
            self.boxes = boxes
            self._img = img

        def __len__(self):
            return len(self.boxes)

        def __getitem__(self, i):
            return Risultato([self.boxes[i]], self._img)

        def __iter__(self):
            for b in self.boxes:
                yield Risultato([b], self._img)

        def plot(self):
            out = np.ascontiguousarray(self._img[:, :, :3]).copy()
            for b in self.boxes:
                x1, y1, x2, y2 = [int(v) for v in b.xyxy[0]]
                cv2.rectangle(out, (x1, y1), (x2, y2), (0, 200, 0), 2)
            return out

    contesto = {"camera": "linea"}

    class YOLO:
        def __init__(self, percorso, task=None):
            self.nome = str(percorso)
            M.statistiche["caricamenti_yolo"] += 1
            M.avanza(M.cfg["yolo_caricamento"])

        def predict(self, img, conf=0.25, verbose=False, **k):
            M.statistiche["predizioni_yolo"] += 1
            M.avanza(M.cfg["yolo_inferenza"])
            n = self.nome
            if "Cross" in n:
                trovati = M.yolo_cross_linea(img) if contesto["camera"] == "linea" else M.oggetti_arena("cross")
            elif "PalCol" in n:
                trovati = M.oggetti_arena("palline")
            elif "Trian" in n:
                trovati = M.oggetti_arena("triangoli")
            elif "Exit" in n:
                trovati = M.oggetti_arena("uscita")
            else:
                trovati = []
            boxes = [Box(c, p, b) for c, p, b in trovati if p >= conf and b]
            return [Risultato(boxes, img)]

    sys.modules["ultralytics"] = types.SimpleNamespace(YOLO=YOLO)
    sys.modules["ultralytics.utils"] = types.SimpleNamespace(LOGGER=types.SimpleNamespace(handlers=[]))
    sys.modules["torch"] = types.SimpleNamespace(set_num_threads=lambda n: None,
                                                 set_num_interop_threads=lambda n: None)

    # ---------------- OpenCV: niente finestre, niente file ----------------
    cv2.imshow = lambda *a, **k: None
    cv2.waitKey = lambda d=0: (M.avanza(0.001) or -1)
    cv2.destroyAllWindows = lambda *a, **k: None

    def finto_imwrite(nome, img, *a):
        M.avanza(M.cfg["scrittura_foto"])     # il tempo di scrittura su SD resta
        return True
    cv2.imwrite = finto_imwrite

    return contesto


def collega_moduli(mondo, contesto):
    """Dopo l'import dei vostri moduli: aggancia il Robot e sa quale camera sta usando VerificaVerde."""
    import ViennaDataConf
    if hasattr(ViennaDataConf, "CARTELLA_FOTO"):
        # nel simulatore le foto non si scrivono: niente cartelle create sul PC
        ViennaDataConf.CARTELLA_FOTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "foto_simulate") + os.sep
    if hasattr(ViennaDataConf, "CARTELLA_SCATOLA"):
        # la scatola nera del simulatore va in scatole_simulate/ (si apre con cruscotto.html)
        ViennaDataConf.CARTELLA_SCATOLA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scatole_simulate") + os.sep
    import ViennaClsRobot
    import ViennaClsWebCam

    init_orig = ViennaClsRobot.Robot.__init__

    def init(self, *a, **k):
        init_orig(self, *a, **k)
        mondo.robot = self
    ViennaClsRobot.Robot.__init__ = init

    vv_orig = ViennaClsWebCam.VerificaVerde

    def verifica_verde(img):
        # Immagine 440x260 = camera della linea, 224x224 = camera dell'arena (in TrovaUscitaIA)
        contesto["camera"] = "linea" if img.shape[1] == 440 else "arena"
        return vv_orig(img)
    ViennaClsWebCam.VerificaVerde = verifica_verde
