import os
from arsenal.privesc.enum import citeste_linii, nume, GTFO

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start")

def cai(fisier):
    return set(citeste_linii(fisier))

baza = cai(os.path.join(DIR, "baza_suid.txt"))
acum = cai(os.path.join(DIR, "suid.txt"))
print("baza:", len(baza), " acum:", len(acum))

noi = acum - baza
print(len(noi), "SUID noi fata de sistemul curat")
for c in sorted(noi):
    print(" ", c)

risc = {nume(c): ("mare" if nume(c) in GTFO else "normal") for c in noi}
periculoase = [c for c in sorted(noi) if nume(c) in GTFO]
print("periculoase NOI:", periculoase)