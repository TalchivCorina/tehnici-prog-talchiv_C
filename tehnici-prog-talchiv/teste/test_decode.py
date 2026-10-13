import base64
import hashlib

from arsenal.forensics.decode import (
    citibil, desfa, desfa_straturi, ghici_strat, rezolva, sparge_hash, sparge_xor,
)


def test_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"


def test_ghici_strat():
    assert ghici_strat("%2Fetc") == "url"
    assert ghici_strat("48656c6c6f") == "hex"
    assert ghici_strat("U2FsdXQ=") == "base64"
    assert ghici_strat("FLAG{x}") == "necunoscut"


def test_desfa_hex_si_url():
    assert desfa("48656c6c6f") == ("hex", b"Hello")
    assert desfa("%2Fetc%2Fpasswd") == ("url", b"/etc/passwd")


def test_text_simplu_nu_e_strat():
    assert desfa("Salut")[0] == "necunoscut"


def test_straturi_multiple():
    clar = b"FLAG{test}"
    val = base64.b64encode(base64.b64encode(clar.hex().encode())).decode()
    straturi, rezultat = desfa_straturi(val)
    assert straturi == ["base64", "base64", "hex"]
    assert rezultat == clar


def test_citibil():
    assert citibil(b"Salut")
    assert not citibil(b"\x80\x81")
    assert not citibil(b"")


def test_xor_un_octet():
    clar = b"Un singur octet tine tot secretul FLAG{xor}"
    date = bytes(b ^ 0x80 for b in clar)
    assert (0x80, clar) in sparge_xor(date)


def test_hash_prin_dictionar(tmp_path):
    wl = tmp_path / "wl.txt"
    wl.write_text("admin\nqwerty\ndragon\n")
    tinta = hashlib.md5(b"dragon").hexdigest()
    assert sparge_hash(tinta, str(wl)) == ("md5", "dragon")
    assert sparge_hash(hashlib.sha1(b"admin").hexdigest(), str(wl)) == ("sha1", "admin")
    assert sparge_hash(hashlib.md5(b"altceva").hexdigest(), str(wl)) == ("md5", None)


def test_lant_complet_base64_peste_xor():
    clar = b"FLAG{lant}"
    val = base64.b64encode(bytes(b ^ 0x80 for b in clar))
    fisa = rezolva(val)
    assert fisa["rezultat"] == clar.decode()
    assert fisa["strat"] == ["base64", "xor(cheie=128)"]
