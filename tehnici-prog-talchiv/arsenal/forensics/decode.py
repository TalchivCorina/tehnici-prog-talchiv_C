# -*- coding: utf-8 -*-
"""Lucrarea A - decoderul universal (forensics).

Dat un sir sau un fisier, recunoaste stratul de codare (url / hex / base64),
il desface, iar daca ajunge la octeti ilizibili incearca un XOR cu cheie de un
octet; daca intrarea e un hash de parola, il sparge prin dictionar."""
import argparse
import base64
import binascii
import hashlib
import json
import os
import re
from urllib.parse import unquote

AICI = os.path.dirname(os.path.abspath(__file__))
RADACINA = os.path.dirname(os.path.dirname(AICI))
FISA = os.path.join(AICI, "fisa.json")
WORDLIST_IMPLICIT = os.path.join(RADACINA, "probe", "wordlist.txt")

MAX_STRATURI = 8  # ca sa nu intram in bucla infinita
HASH_DUPA_LUNGIME = {32: "md5", 40: "sha1", 64: "sha256"}


#A2
def ghici_strat(s):
    """Clasifica un sir dupa forma lui, fara sa-l decodeze.
    Ordinea conteaza: url (%), apoi hex (mai strict), apoi base64 (alfabet larg)."""
    if "%" in s:
        return "url"
    if re.fullmatch(r"[0-9a-fA-F]+", s) and len(s) % 2 == 0:
        return "hex"
    if re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s) and len(s) % 4 == 0:
        return "base64"
    return "necunoscut"


#A3
def desfa(s):
    """Desface stratul recunoscut. Intoarce (strat, rezultat_bytes).
    Daca stratul nu se poate desface, intoarce ("necunoscut", s.encode())."""
    strat = ghici_strat(s)
    try:
        if strat == "base64":
            return strat, base64.b64decode(s, validate=True)
        if strat == "hex":
            return strat, bytes.fromhex(s)
        if strat == "url":
            return strat, unquote(s).encode()
    except (binascii.Error, ValueError):
        pass
    return "necunoscut", s.encode()


#A4
def citibil(b):
    """True daca toti octetii sunt in 32..126 (ASCII imprimabil)."""
    return len(b) > 0 and all(32 <= c < 127 for c in b)


def desfa_straturi(s, max_straturi=MAX_STRATURI):
    """Desface straturi in bucla, cat timp ce iese mai e o codare.
    Intoarce (lista_straturi, rezultat_bytes)."""
    straturi = []
    val = s.strip()
    rezultat = val.encode()
    for _ in range(max_straturi):
        strat, b = desfa(val)
        if strat == "necunoscut":
            break
        straturi.append(strat)
        rezultat = b
        if not citibil(b):             # octeti ilizibili: nu mai e text de desfacut
            break
        val = b.decode("ascii")
    return straturi, rezultat


#A5
def sparge_xor(date):
    """Incearca toate cele 256 de chei de un octet. Intoarce [(cheie, clar), ...]
    pentru rezultatele care arata a text."""
    gasite = []
    for k in range(256):
        clar = bytes(b ^ k for b in date)
        if citibil(clar):
            gasite.append((k, clar))
    return gasite


#A6
def e_hash(s):
    return len(s) in HASH_DUPA_LUNGIME and re.fullmatch(r"[0-9a-fA-F]+", s) is not None


def sparge_hash(tinta, cale_wordlist=WORDLIST_IMPLICIT):
    """Identifica algoritmul dupa lungime si cauta parola in wordlist.
    Intoarce (algoritm, parola) sau (algoritm, None)."""
    tinta = tinta.strip().lower()
    algo = HASH_DUPA_LUNGIME.get(len(tinta))
    if algo is None or not os.path.isfile(cale_wordlist):
        return algo, None
    with open(cale_wordlist, encoding="latin1") as f:
        for cuv in f:
            cuv = cuv.strip()
            if hashlib.new(algo, cuv.encode()).hexdigest() == tinta:
                return algo, cuv
    return algo, None


#legatura
def rezolva(date, cale_wordlist=WORDLIST_IMPLICIT):
    """Ia octeti, aplica ce se poate (hash, straturi, XOR) si intoarce o fisa (dict)."""
    pasi = []
    for _ in range(MAX_STRATURI):
        if citibil(date):
            text = date.decode("ascii").strip()
            if e_hash(text):
                algo, parola = sparge_hash(text, cale_wordlist)
                if parola is not None:
                    pasi.append(algo)
                    date = parola.encode()
                    break
            strat, nou = desfa(text)
            if strat == "necunoscut":
                break
            pasi.append(strat)
            date = nou
        else:
            gasite = sparge_xor(date)
            if not gasite:
                break
            cheie, clar = gasite[0]
            pasi.append("xor(cheie=%d)" % cheie)
            date = clar
    text = date.decode("utf-8", errors="replace") if citibil(date) else date.hex()
    return {"strat": pasi, "rezultat": text}


def rezolva_intrare(intrare, e_fisier, cale_wordlist=WORDLIST_IMPLICIT):
    if not e_fisier:
        fisa = rezolva(intrare.encode(), cale_wordlist)
        return {"intrare": intrare, **fisa}
    with open(intrare, "rb") as f:
        date = f.read()
    linii = [l.strip() for l in date.splitlines() if l.strip()]
    if len(linii) > 1 and all(citibil(l) for l in linii):
        # un fisier cu mai multe linii text (ex. hashuri.txt): fiecare linie separat
        return {"intrare": intrare,
                "rezultate": [{"linie": l.decode("ascii"),
                               **rezolva(l, cale_wordlist)} for l in linii]}
    if citibil(date.strip()):
        date = date.strip()
    return {"intrare": intrare, **rezolva(date, cale_wordlist)}


#A7
def main():
    p = argparse.ArgumentParser(description="Decoder universal: straturi, XOR, hash.")
    p.add_argument("intrare", help="un sir sau (cu --fisier) calea unui fisier")
    p.add_argument("--fisier", action="store_true", help="intrarea e o cale de fisier")
    p.add_argument("--wordlist", default=WORDLIST_IMPLICIT,
                   help="dictionarul pentru hash-uri (implicit probe/wordlist.txt)")
    p.add_argument("--out", default=FISA, help="unde salvez fisa JSON")
    a = p.parse_args()

    fisa = rezolva_intrare(a.intrare, a.fisier, a.wordlist)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(fisa, f, indent=2, ensure_ascii=True)
    print(json.dumps(fisa, indent=2, ensure_ascii=True))
    print("fisa salvata in", a.out)


if __name__ == "__main__":
    main()
