import requests
import re

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
})

urls = [
    'https://www.prozis.com/be/fr/prozis/100-whey-hydro-isolate-2000-g',
    'https://www.prozis.com/be/fr/prozis/100-proteine-de-soja-900-g',
    'https://www.prozis.com/be/fr/prozis/massive-mass-gainer-2268-g'
]

for url in urls:
    r = s.get(url, timeout=5)
    title = re.findall(r'<meta property="og:title" content="(.*?)"', r.text)
    price = re.findall(r'<meta property="product:price:amount" content="(.*?)"', r.text)
    image = re.findall(r'<meta property="og:image" content="(.*?)"', r.text)
    
    print('URL:', url)
    print(' Title:', title[0] if title else 'N/A')
    print(' Price:', price[0] if price else 'N/A', '€')
    print(' Image:', image[0] if image else 'N/A')
    print('-' * 40)
