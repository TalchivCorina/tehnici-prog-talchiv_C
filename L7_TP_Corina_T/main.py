"""Programul principal: ruleaza raportul folosind functiile din httptools."""
from httptools import PATHS, report


def main():
    rezultate = []
    for path in PATHS:
        d = report(path)
        d["path"] = path
        rezultate.append(d)

    reusite = [d for d in rezultate if d["status"] == 200]
    for d in sorted(reusite, key=lambda d: d["seconds"], reverse=True):
        print(f"{d['path']} -> {d['status']}, {d['seconds']} secunde")

    print(f"Reusite: {len(reusite)} | Esuate: {len(rezultate) - len(reusite)}")


if __name__ == "__main__":
    main()