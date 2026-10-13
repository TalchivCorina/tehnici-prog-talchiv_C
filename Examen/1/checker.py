import requests

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    return "https://" + host + "/" + path.lstrip("/")


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    return url.lower().startswith("https://")


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        response = requests.get(url, timeout=5)
        print("Status:", response.status_code)
        print("Content-Type:", response.headers.get("Content-Type", "unknown"))

    except requests.exceptions.RequestException as error:
        print("Eroare la cerere:", str(error))


def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    try:
        response = requests.get(url, timeout=5)
        content_type = response.headers.get("Content-Type", "unknown").split(";")[0]
        return {
            "status": response.status_code,
            "content_type": content_type,
            "length": len(response.content),
            "server": response.headers.get("Server", "unknown")
        }
    except requests.exceptions.RequestException as error:
        return {
            "status": None,
            "error": str(error)
        }


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""
    results = []
    for url in SITES:
        result = check_site(url)
        results.append((url, result))

    successful = []
    for url, result in results:
        if result["status"] == 200:
            successful.append((url, result))
    successful.sort(key=lambda item: item[1]["length"], reverse=True)

    for url, result in successful:
        print(url, "->", result["status"], ",", result["length"], "octeți")

    failed = len(results) - len(successful)
    print("Reușite:", len(successful), "| Eșuate:", failed)
    return results


def check_headers(url):
    """Returnează un dicționar cu: present, missing, score."""
    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.RequestException as error:
        return {
            "status": None,
            "error": str(error)
        }
    response_headers = {name.lower() for name in response.headers}

    present = []
    missing = []
    for header in SECURITY_HEADERS:
        if header.lower() in response_headers:
            present.append(header)
        else:
            missing.append(header)

    score = int(len(present) / len(SECURITY_HEADERS) * 100)
    return {
        "present": present,
        "missing": missing,
        "score": score
    }


def retry_check(url, attempts=3):
    """Încearcă de cel mult `attempts` ori; returnează un dicționar cu: status, attempts."""
    last_status = None
    last_error = None
    attempts_made = 0

    for i in range(attempts):
        attempts_made += 1
        try:
            response = requests.get(url, timeout=5)
            last_status = response.status_code
            last_error = None
            if last_status < 500:
                return {
                    "status": last_status,
                    "attempts": attempts_made
                }

        except requests.exceptions.RequestException as error:
            last_status = None
            last_error = str(error)

    result = {
        "status": last_status,
        "attempts": attempts_made
    }
    if last_error is not None:
        result["error"] = last_error
    return result