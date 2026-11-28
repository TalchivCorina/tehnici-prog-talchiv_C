"""Unealta de forensics: tip dupa magic bytes + amprenta SHA-256.

Rulare (din radacina depozitului):
    python -m arsenal.forensics.amprente arsenal/forensics/probe
"""
import argparse
import hashlib
import os

# Semnaturi fixe de la inceputul fisierelor (magic bytes)
MAGIC = {b"\x89PNG": "PNG", b"%PDF": "PDF", b"PK\x03\x04": "ZIP"}


def tip(head):
    """Intoarce tipul fisierului dupa primii octeti."""
    for semnatura, nume in MAGIC.items():
        if head.startswith(semnatura):
            return nume
    # return-ul este DUPA bucla: toate semnaturile sunt verificate inainte
    return "necunoscut"


def amprenta_fisier(cale):
    """Citeste fisierul binar (cu with) si intoarce fisa lui."""
    with open(cale, "rb") as f:  # "rb" = binar; with inchide singur fisierul
        date = f.read()
    return {
        "nume": os.path.basename(cale),
        "tip": tip(date[:8]),
        "sha256": hashlib.sha256(date).hexdigest()[:16],
    }


def scaneaza(folder):
    """Amprenteaza toate fisierele din folder, in ordine alfabetica."""
    rez = []
    for nume in sorted(os.listdir(folder)):
        cale = os.path.join(folder, nume)
        if os.path.isfile(cale):
            rez.append(amprenta_fisier(cale))
    return rez


def main():
    parser = argparse.ArgumentParser(description="Amprente SHA-256 si tip de fisier")
    parser.add_argument("folder", help="folderul cu fisiere de examinat")
    args = parser.parse_args()
    for fisa in scaneaza(args.folder):
        print(f"{fisa['nume']:14} {fisa['tip']:11} {fisa['sha256']}")


if __name__ == "__main__":
    main()
