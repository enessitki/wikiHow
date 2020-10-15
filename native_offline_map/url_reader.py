import requests

img_url = "http://b.tile.osm.org/13/2342/3144.png"
headers = {
    'User-Agent': 'My User Agent 1.0',
    'From': 'youremail@domain.com'  # This is another valid field
}

res = requests.get(img_url, headers=headers)
print(res.content)
