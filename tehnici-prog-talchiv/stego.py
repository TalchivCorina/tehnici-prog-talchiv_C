# -*- coding: utf-8 -*-
"""Lucrarea B (B5-B6) - steganografie LSB.

Ascunde un mesaj in ultimul bit al fiecarui canal (R, G, B) al pixelilor si il
dezvaluie inapoi. Mesajul se termina cu un octet 0. Se salveaza DOAR in PNG
(fara pierdere): un JPG recompresat distruge bitii ascunsi.

    python stego.py ascunde                 # probe/foto.jpg -> stego.png
    python stego.py dezvaluie               # citeste stego.png
    python stego.py ascunde probe/foto.jpg "alt mesaj" iesire.png
"""
import argparse

from PIL import Image

MESAJ_IMPLICIT = "FLAG{ascuns_in_pixeli}"


def ascunde(cale_in, mesaj, cale_out="stego.png"):
    img = Image.open(cale_in).convert("RGB")
    date = bytearray(img.tobytes())            # R,G,B,R,G,B,... cate un octet pe canal
    mesaj_bytes = mesaj.encode("utf-8")
    if b"\x00" in mesaj_bytes:
        raise ValueError("mesajul nu poate contine octetul 0 (e marcajul de final)")
    plin = mesaj_bytes + b"\x00"
    biti = [(octet >> (7 - j)) & 1 for octet in plin for j in range(8)]
    if len(biti) > len(date):
        raise ValueError("mesaj prea lung: incap %d octeti, ai %d" % (len(date) // 8 - 1, len(plin)))
    for i, bit in enumerate(biti):
        date[i] = (date[i] & ~1) | bit         # canal = (canal & ~1) | bit
    Image.frombytes("RGB", img.size, bytes(date)).save(cale_out, format="PNG")
    return len(mesaj_bytes)


def dezvaluie(cale_stego):
    date = Image.open(cale_stego).convert("RGB").tobytes()
    rezultat = bytearray()
    octet, nr_biti = 0, 0
    for canal in date:
        octet = (octet << 1) | (canal & 1)     # aduna ultimii biti
        nr_biti += 1
        if nr_biti == 8:
            if octet == 0:                     # primul octet 0 = final de mesaj
                break
            rezultat.append(octet)
            octet, nr_biti = 0, 0
    return rezultat.decode("utf-8", errors="replace")


def main():
    p = argparse.ArgumentParser(description="Steganografie LSB in PNG.")
    sub = p.add_subparsers(dest="comanda", required=True)

    a = sub.add_parser("ascunde", help="ascunde un mesaj intr-o poza gazda")
    a.add_argument("gazda", nargs="?", default="probe/foto.jpg")
    a.add_argument("mesaj", nargs="?", default=MESAJ_IMPLICIT)
    a.add_argument("iesire", nargs="?", default="stego.png")

    d = sub.add_parser("dezvaluie", help="citeste mesajul dintr-un PNG")
    d.add_argument("stego", nargs="?", default="stego.png")

    args = p.parse_args()
    if args.comanda == "ascunde":
        n = ascunde(args.gazda, args.mesaj, args.iesire)
        print("ascuns: %d octeti in %s" % (n, args.iesire))
    else:
        print("mesaj dezvaluit:", dezvaluie(args.stego))


if __name__ == "__main__":
    main()
