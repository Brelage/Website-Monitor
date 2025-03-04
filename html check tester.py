import requests

r = requests.head("https://www.ecos.eu")

head_content = ""
for chunk in r.iter_content(chunk_size=512, decode_unicode=True):
    if chunk:
        head_content += chunk
        if "</head>" in head_content:
            break

print(r)

if "error" not in head_content:
    False
else:
    True