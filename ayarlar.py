import copy
import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

# Bu dosyanın bulunduğu klasöre göre, bot nereden çalıştırılırsa çalıştırılsın bulunur
AYAR_DOSYASI = Path(__file__).resolve().parent / "settings.json"

_onbellek = {"mtime": None, "veri": {}}


def get_settings() -> dict:
    # Dosya değişmediyse bellekteki kopyayı verir, değiştiyse yeniden okur
    try:
        mtime = AYAR_DOSYASI.stat().st_mtime
    except FileNotFoundError:
        return {}

    if _onbellek["mtime"] != mtime:
        try:
            with open(AYAR_DOSYASI, "r", encoding="utf-8") as f:
                _onbellek["veri"] = json.load(f)
            _onbellek["mtime"] = mtime
        except json.JSONDecodeError as e:
            log.error("settings.json okunamadı: %s", e)

    # Kopya veriyoruz, çağıran taraf değiştirirse bellekteki asıl veri bozulmasın
    return copy.deepcopy(_onbellek["veri"])


def save_settings(data: dict) -> None:
    # Önce geçici dosyaya yaz, sonra yer değiştir: yazma yarıda kesilirse asıl dosya bozulmaz
    gecici = AYAR_DOSYASI.with_suffix(".json.tmp")
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(gecici, AYAR_DOSYASI)
    _onbellek["mtime"] = None  # bir sonraki okumada tazele