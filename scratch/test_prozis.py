import requests
import re

url = 'https://www.prozis.com/be/fr/prozis/100-whey-hydro-isolate-2000-g'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
}

r = requests.get(url, headers=headers, timeout=10)
print('HTML Length:', len(r.text))

# Search for price patterns like "price", "final_price", "€", "EUR"
matches = re.findall(r'[^"{}\n]*price[^"{}\n]*', r.text, re.IGNORECASE)
print('Price lines matching count:', len(matches))
for m in matches[:15]:
    print('  -', m.strip())

og_title = re.findall(r'<meta property="og:title" content="(.*?)"', r.text)
og_price = re.findall(r'<meta property="product:price:amount" content="(.*?)"', r.text)
og_curr = re.findall(r'<meta property="product:price:currency" content="(.*?)"', r.text)

print('OG Title:', og_title)
print('OG Price:', og_price, og_curr)
