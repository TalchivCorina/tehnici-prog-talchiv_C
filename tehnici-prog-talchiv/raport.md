# Laboratorul 6. Informații invizibile: forensics și steganografie

Student: _<Nume Prenume>, grupa <grupa>_ · Disciplina: Tehnici de programare (UTM · FCIM)

Cadru legal: am lucrat exclusiv pe fișierele generate de `probe/pregateste.py` și pe propriile mele fișiere.

Pregătire: `python probe/pregateste.py` (scrie în `probe/`). Rulări din rădăcina depozitului.

## Lucrarea A. Decoderul universal (`arsenal/forensics/decode.py`)

Unealta recunoaște stratul (url / hex / base64), îl desface în buclă (maxim 8 straturi), încearcă XOR cu cheie de un octet când ajunge la octeți ilizibili și sparge hash-uri prin dicționar. Fișa rezultatului se salvează în `arsenal/forensics/fisa.json`. Testele: `python -m pytest -q` (9 trec).

### Ce ascundea mesajul cu straturi

Comanda: `python arsenal/forensics/decode.py probe/mesaj.txt --fisier`

```
strat: base64 -> base64 -> hex
rezultat: FLAG{straturi_de_encoding}
```

Șirul era codat în trei straturi: hex peste textul clar, apoi base64 peste hex, apoi încă un base64 deasupra. Decodarea merge în ordine inversă. Un text simplu ca `Salut` nu e tratat ca strat (nu e base64 valid), deci bucla se oprește corect.

### Ce cheie XOR am găsit

Comanda: `python arsenal/forensics/decode.py probe/xor.bin --fisier`

```
strat: xor(cheie=128)      # 0x80
rezultat: Un singur octet tine tot secretul... gaseste-l! FLAG{xor_un_octet}
```

Cheia are un singur octet, deci doar 256 de variante; am încercat-o pe toate și am păstrat rezultatul în care toți octeții sunt ASCII imprimabil (32..126). Textul clar are biții de sus 0, iar cheia 0x80 îi aprinde pe toți, de aceea orice altă cheie lasă octeți neimprimabili.

### Ce parole am spart

Comanda: `python arsenal/forensics/decode.py probe/hashuri.txt --fisier`

Lungimea de 32 de caractere hex arată MD5. Nu „decriptez" hash-ul: hashuiesc fiecare cuvânt din `probe/wordlist.txt` și compar.

| hash (MD5) | parola |
|---|---|
| 5f4dcc3b5aa765d61d8327deb882cf99 | password |
| 8621ffdbc5698829397d97767ac13db3 | dragon |
| d8578edf8458ce06fbc5bb76a58c5ca4 | qwerty |
| 0d107d09f5bbe40cade3de5c71e9e9b7 | letmein |
| d0763edaa9d9bd2a9516280e9044d885 | monkey |

Concluzie: toate cele 5 parole sunt cuvinte uzuale și cad în fața unui dicționar de câteva rânduri. MD5 fără sare nu protejează parole.

## Lucrarea B. Forensics pe fișiere și mesaj ascuns

Scripturi: `forensics.py` (B1–B4) și `stego.py` (B5–B6). Rulare: `python forensics.py`.

### B1. Tipul real al fișierelor (magic bytes)

```
probe/foto.jpg     -> jpeg
probe/ascuns.png   -> png
probe/xor.bin      -> d5eea0f3e9eee7f5   (fără semnătură cunoscută: date criptate/brute)
probe/mesaj.txt    -> 546b525a4d466c36   (text ASCII, fără semnătură)
```

Fișierele se deschid cu `"rb"`, altfel octeții se pot altera.

### B2. strings pe `probe/ascuns.png`

```
IHDR
IDATx
15hB
IEND
secret.txtFLAG{ascuns_prin_carving}
secret.txtPK
```

După `IEND` (finalul PNG-ului) apar nume de fișier și un steag: indiciu clar că în coadă e altceva.

### B3. Metadate EXIF și GPS din `probe/foto.jpg`

```
Model = iPhone 13
DateTime = 2026:09:14 10:30:00
Make = Apple
GPSInfo = {'GPSLatitudeRef': 'N', 'GPSLatitude': (47.0, 1.0, 0.0),
           'GPSLongitudeRef': 'E', 'GPSLongitude': (28.0, 51.0, 27.0)}
coordonate zecimale: 47.0167, 28.8575
```

Conversia: `grade + minute/60 + secunde/3600`; emisfera S sau W dă semn negativ. Punctul (47.0167 N, 28.8575 E) cade în Chișinău. Din aceste metadate se vede și telefonul (Apple iPhone 13) și data. De aceea se șterge EXIF înainte de a publica o poză.

### B4. Ce era în arhiva ascunsă

```
arhiva extrasa de la octetul 781 -> gasit.zip
in arhiva: secret.txt = 'FLAG{ascuns_prin_carving}\n'
```

Semnătura `PK\x03\x04` a fost găsită după datele PNG-ului; tot ce urmează e un ZIP valid, deci `ascuns.png` e și PNG, și ZIP.

### B5–B6. Mesajul LSB (`stego.py`)

```
$ python stego.py ascunde
ascuns: 22 octeti in stego.png
$ python stego.py dezvaluie
mesaj dezvaluit: FLAG{ascuns_in_pixeli}
```

Mesajul se scrie în ultimul bit al fiecărui canal R, G, B, urmat de un octet 0 ca marcaj de final. Diferența față de poza originală este cel mult 1 pe canal, deci invizibilă. Salvez doar în PNG: un JPG recompresează imaginea și distruge biții ascunși. Capacitatea pozei de 640×480 este circa 115 KB.

## Opțional. `challenge.bin`

Comanda: `python arsenal/forensics/decode.py probe/challenge.bin --fisier`

Pași: (1) fișierul e text în alfabet base64, deci îl desfac; (2) rezultatul are octeți ilizibili, deci încerc cele 256 de chei XOR; (3) o singură cheie dă text imprimabil.

```
strat: base64 -> xor(cheie=128)
rezultat: FLAG{lant_complet_despicat}
```

Verificare cu indiciul din `probe/challenge_hint.txt`:

```
md5(FLAG{lant_complet_despicat}) = 8c4eb02d9dcef7d0ff91d8e4c7fea91b   # coincide cu indiciul
```
