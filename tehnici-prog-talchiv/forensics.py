# -*- coding: utf-8 -*-
"""Lucrarea B (B1-B4) - forensics pe fisiere.

Rulare din radacina depozitului (dupa `python probe/pregateste.py`):
    python forensics.py
"""
import io
import re
import zipfile

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

SEMNATURI = [
    (b"%PDF", "pdf"),
    (b"\x89PNG", "png"),
    (b"\xff\xd8", "jpeg"),
    (b"PK\x03\x04", "zip/docx"),
]


#B1
def tip_real(cale):
    """Tipul real dupa primii octeti (magic bytes), nu dupa extensie."""
    with open(cale, "rb") as f: # "rb": fisier binar, fara alterarea octetilor
        cap = f.read(8)
    for semnatura, nume in SEMNATURI:
        if cap.startswith(semnatura):
            return nume
    return cap.hex()


#B2
def strings(cale, minim=4):
    """Secventele de caractere imprimabile (ca utilitarul `strings`)."""
    with open(cale, "rb") as f:
        date = f.read()
    return [m.decode("ascii") for m in re.findall(rb"[ -~]{%d,}" % minim, date)]


#B3
def _grade_zecimale(dms, emisfera):
    grade, minute, secunde = (float(x) for x in dms)
    val = grade + minute / 60 + secunde / 3600
    return -val if emisfera in ("S", "W") else val


def exif_si_gps(cale):
    """Intoarce (exif_citibil, (lat, lon) sau None). Foloseste getexif(), API-ul public."""
    exif = Image.open(cale).getexif()
    citibil = {TAGS.get(t, t): v for t, v in exif.items() if t != 0x8825}
    gps = exif.get_ifd(0x8825) # blocul GPS (tag 34853)
    if not gps:
        return citibil, None
    gps_nume = {GPSTAGS.get(t, t): v for t, v in gps.items()}
    citibil["GPSInfo"] = gps_nume
    lat = _grade_zecimale(gps_nume["GPSLatitude"], gps_nume["GPSLatitudeRef"])
    lon = _grade_zecimale(gps_nume["GPSLongitude"], gps_nume["GPSLongitudeRef"])
    return citibil, (lat, lon)


#B4
def file_carving_zip(cale, iesire="gasit.zip"):
    """Gaseste semnatura ZIP in fisier, salveaza arhiva separat si intoarce offsetul."""
    with open(cale, "rb") as f:
        date = f.read()
    i = date.find(b"PK\x03\x04")
    if i == -1:
        return None
    with open(iesire, "wb") as f:
        f.write(date[i:])
    return i


def citeste_arhiva(cale_zip):
    """Citeste continutul arhivei fara sa o extraga pe disc."""
    with zipfile.ZipFile(cale_zip) as z:
        return {nume: z.read(nume).decode("utf-8", errors="replace") for nume in z.namelist()}


def main():
    print("== B1. Magic bytes")
    for cale in ("probe/foto.jpg", "probe/ascuns.png", "probe/xor.bin", "probe/mesaj.txt"):
        print("  %-18s -> %s" % (cale, tip_real(cale)))

    print("\n== B2. strings pe probe/ascuns.png")
    for s in strings("probe/ascuns.png"):
        print("  ", s)

    print("\n== B3. EXIF si GPS din probe/foto.jpg")
    exif, coord = exif_si_gps("probe/foto.jpg")
    for k, v in exif.items():
        print("  %s = %s" % (k, v))
    if coord:
        lat, lon = coord
        print("  coordonate zecimale: %.4f, %.4f" % (lat, lon))
        print("  harta: https://www.openstreetmap.org/?mlat=%.4f&mlon=%.4f#map=16/%.4f/%.4f"
              % (lat, lon, lat, lon))

    print("\n== B4. File carving din probe/ascuns.png")
    i = file_carving_zip("probe/ascuns.png")
    if i is None:
        print("  nu am gasit nicio semnatura ZIP")
    else:
        print("  arhiva extrasa de la octetul", i, "-> gasit.zip")
        for nume, continut in citeste_arhiva("gasit.zip").items():
            print("  in arhiva: %s = %r" % (nume, continut))


if __name__ == "__main__":
    main()
