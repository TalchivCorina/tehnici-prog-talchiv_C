import requests

BASE = "https://httpbin.org" # adresa serverului, schimbata intr-un singur loc
PATHS = ["/get", "/redirect/2", "/delay/1", "/status/404", "/delay/5"]
TIMEOUT = 10                         


# Partea 1
def search(params):
    """GET pe /get cu parametri in URL; returneaza parametrii primiti de server."""
    r = requests.get(f"{BASE}/get", params=params, timeout=TIMEOUT)
    return r.json().get("args")

def search_url(params):
    """Returneaza adresa completa construita de requests, cu tot cu parametri."""
    r = requests.get(f"{BASE}/get", params=params, timeout=TIMEOUT)
    return r.url

# Partea 2
def fetch_with_agent(agent):
    """GET pe /headers cu User-Agent=agent; returneaza User-Agent-ul vazut de server."""
    r = requests.get(f"{BASE}/headers", headers={"User-Agent": agent}, timeout=TIMEOUT)
    return r.json()["headers"].get("User-Agent")

def default_agent():
    """Returneaza User-Agent-ul trimis de requests cand nu setezi nimic."""
    r = requests.get(f"{BASE}/headers", timeout=TIMEOUT)
    return r.json()["headers"].get("User-Agent")

#Partea 3
def post_json(data):
    """POST cu datele ca JSON pe /post; returneaza JSON-ul primit de server."""
    r = requests.post(f"{BASE}/post", json=data, timeout=TIMEOUT)
    return r.json().get("json")

def post_form(data):
    """POST cu datele ca formular pe /post; returneaza formularul primit de server."""
    r = requests.post(f"{BASE}/post", data=data, timeout=TIMEOUT)
    return r.json().get("form")

# Partea 4
def describe_status(code):
    """GET pe /status/<code>; returneaza 'succes', 'eroare client' sau 'eroare server'."""
    r = requests.get(f"{BASE}/status/{code}", timeout=TIMEOUT)
    if 200 <= r.status_code < 300:
        return "succes"
    if 400 <= r.status_code < 500:
        return "eroare client"
    if 500 <= r.status_code < 600:
        return "eroare server"
    return "altceva"


def is_ok(code):
    """GET pe /status/<code>; True daca cererea a reusit, altfel False."""
    try:
        r = requests.get(f"{BASE}/status/{code}", timeout=TIMEOUT)
        r.raise_for_status()
        return True
    except requests.RequestException:   # include HTTPError (4xx/5xx)
        return False

#Partea 5
def count_redirects(n):
    """GET pe /redirect/<n>; returneaza cate redirectionari au fost urmate."""
    r = requests.get(f"{BASE}/redirect/{n}", timeout=TIMEOUT)
    return len(r.history)

def final_url(n):
    """GET pe /redirect/<n>; returneaza adresa la care ai ajuns."""
    r = requests.get(f"{BASE}/redirect/{n}", timeout=TIMEOUT)
    return r.url

def first_hop(n):
    """GET pe /redirect/<n> FARA a urma redirectionarea; returneaza antetul Location."""
    r = requests.get(f"{BASE}/redirect/{n}", allow_redirects=False, timeout=TIMEOUT)
    return r.headers.get("Location")

#Partea 6
def cookie_demo(name, value):
    """Seteaza un cookie, apoi citeste cookie-urile inapoi cu O SINGURA sesiune."""
    with requests.Session() as s:                       # sesiunea tine minte cookie-urile
        s.get(f"{BASE}/cookies/set", params={name: value}, timeout=TIMEOUT)
        r = s.get(f"{BASE}/cookies", timeout=TIMEOUT)
    return r.json().get("cookies")

def no_session_demo(name, value):
    """Acelasi lucru cu apeluri simple requests.get (fara sesiune); cookie-ul se pierde."""
    requests.get(f"{BASE}/cookies/set", params={name: value}, timeout=TIMEOUT)
    r = requests.get(f"{BASE}/cookies", timeout=TIMEOUT)  # cerere noua, fara memorie
    return r.json().get("cookies")

# Partea 7
def report(path):
    """Descrie pagina de la BASE + path; nu se opreste niciodata cu eroare."""
    try:
        r = requests.get(BASE + path, timeout=3)
        return {
            "status": r.status_code,
            "final_url": r.url,
            "redirects": len(r.history),
            "seconds": round(r.elapsed.total_seconds(), 2),
            "content_type": r.headers.get("Content-Type"),
        }
    except requests.RequestException as e:                # timeout, fara conexiune etc.
        return {"status": None, "error": type(e).__name__}


def main():
    rezultate = []
    for path in PATHS:
        d = report(path)
        d["path"] = path # adaug adresa in dictionar
        rezultate.append(d)

    reusite = [d for d in rezultate if d["status"] == 200]
    for d in sorted(reusite, key=lambda d: d["seconds"], reverse=True):
        print(f"{d['path']} -> {d['status']}, {d['seconds']} secunde")

    print(f"Reusite: {len(reusite)} | Esuate: {len(rezultate) - len(reusite)}")

#Bonus
def check_login(user, password):
    """True daca serverul accepta datele de autentificare, altfel False."""
    try:
        r = requests.get(f"{BASE}/basic-auth/admin/secret",
                         auth=(user.encode("utf-8"), password.encode("utf-8")),  # permite diacritice
                         timeout=TIMEOUT)
        return r.status_code == 200
    except (requests.RequestException, UnicodeError):
        return False


if __name__ == "__main__":
    main()