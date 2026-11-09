import httptools as h

print("=== Partea 1 ===")
print(h.search({"q": "python", "page": "2"}))
print(h.search({"q": "hello world & co"}))
print(h.search_url({"q": "python", "page": "2"}))

print("=== Partea 2 ===")
print(h.fetch_with_agent("MyBot/1.0"))
print(h.default_agent())

print("=== Partea 3 ===")
print(h.post_json({"name": "Ana", "age": 19, "tags": ["a", "b"]}))
print(h.post_form({"user": "ana", "city": "Bălți"}))

print("=== Partea 4 ===")
print(h.describe_status(200), h.describe_status(404), h.describe_status(503))
print(h.is_ok(204), h.is_ok(500))

print("=== Partea 5 ===")
print(h.count_redirects(3))
print(h.final_url(2))
print(h.first_hop(3))

print("=== Partea 6 ===")
print(h.cookie_demo("theme", "dark"))
print(h.no_session_demo("theme", "dark"))

print("=== Partea 7 ===")
for path in h.PATHS:
    print(path, h.report(path))

print("=== Programul complet ===")
h.main()

print("=== Bonus ===")
print(h.check_login("admin", "secret"))
print(h.check_login("admin", "greșit"))