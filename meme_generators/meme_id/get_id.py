import requests
import json

IMG_FLIP_ID_API = 'https://api.imgflip.com/get_memes'
meme_to_id_mapping = {}
response = requests.get(IMG_FLIP_ID_API).json()
if response['success'] == True:
	memes = response['data']['memes']
	with open('meme_id_mapping.json', 'w') as out_f:
		json.dump(memes, out_f)
else:
	print('failed request')
	print(response)