import requests
BASE = "https://httpbin.org"
PATHS = ["/get", "/redirect/2", "/delay/1", "/status/404", "/delay/5"]

# Partea 1: parametri în URL
def search(params):
    """GET pe /get cu parametri în URL; returnează parametrii primiți de server."""
    r = requests.get(f"{BASE}/get", params=params)
    return r.json().get("args")

def search_url(params):
    """Returnează adresa completă construită de requests, cu tot cu parametri."""
    r = requests.get(f"{BASE}/get", params=params)
    return r.url

# Partea 2: anteturi
def fetch_with_agent(agent):
    """GET pe /headers cu User-Agent=agent; returnează User-Agent-ul văzut de server."""
    r = requests.get(f"{BASE}/headers", headers={"User-Agent": agent})
    return r.json()["headers"].get("User-Agent")

def default_agent():
    """Returnează User-Agent-ul trimis de requests când nu setezi nimic."""
    r = requests.get(f"{BASE}/headers")
    return r.json()["headers"].get("User-Agent")

# Partea 3: trimiterea datelor
def post_json(data):
    """POST cu datele ca JSON pe /post; returnează JSON-ul primit de
    server."""
    r = requests.post("https://httpbin.org/post", json=data)
    print(r.json()["json"]) # {'name': 'Ana'}

    pass
def post_form(data):
    """POST cu datele ca formular pe /post; returnează formularul primit de
    server."""
    r = requests.post("https://httpbin.org/post", data=data)
    print(r.json()["form"]) # {'name': 'Ana'}
    pass

# Partea 4: coduri de stare
def describe_status(code):
    """GET pe /status/<code>; returnează 'succes', 'eroare client' sau 'eroare server'."""
    r = requests.get(f"{BASE}/status/{code}")
    if 200 <= r.status_code < 300:
        return "succes"
    if 400 <= r.status_code < 500:
        return "eroare client"
    if 500 <= r.status_code < 600:
        return "eroare server"
    return "altceva"
 
 
def is_ok(code):
    """GET pe /status/<code>; returnează True dacă cererea a reușit, altfel False."""
    try:
        r = requests.get(f"{BASE}/status/{code}")
        r.raise_for_status()
        return True
    except requests.RequestException:  # include HTTPError
        return False

 # Partea 5: redirecționări
def count_redirects(n):
    """GET pe /redirect/<n>; returnează câte redirecționări au fost urmate."""
    r = requests.get(f"{BASE}/redirect/{n}")
    return len(r.history)
 
 
def final_url(n):
    """GET pe /redirect/<n>; returnează adresa la care ai ajuns."""
    r = requests.get(f"{BASE}/redirect/{n}")
    return r.url
 
 
def first_hop(n):
    """GET pe /redirect/<n> FĂRĂ a urma redirecționarea; returnează antetul Location."""
    r = requests.get(f"{BASE}/redirect/{n}", allow_redirects=False)
    return r.headers["Location"]   

