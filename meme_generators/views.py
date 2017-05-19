from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import consts
import requests
import json

SEND = 'https://graph.facebook.com/me/messages?access_token=' + consts.PAGE_ACCESS_TOKEN
IMGFLIP_API = 'https://api.imgflip.com/caption_image'

with open('meme_generators/meme_id/meme_id_mapping.json', 'r') as in_f:
	meme_map = json.load(in_f)

def parse_user_input(text):
	return 'One Does Not Simply', 'One Does Not Simply', "Make a Bot Meme Generator"

def meme_through_imgflip(meme_type, caption_top, caption_bottom):
	meme_id = meme_map[meme_type]
	payload['template_id'] = meme_id
	payload['username'] = consts.IMGFLIP_UNAME
	payload['password'] = consts.IMGFLIP_PASS
	payload['text0'] = caption_top
	payload['text1'] = caption_bottom
	response = requests.post(IMGFLIP_API, payload).json()
	if response['success'] is True:
		return response['data']['url']
	else:
		raise ValueError('IMGFLIP API CALL FAILED')
	
def send_status_message(recipient_id, text):
	response_payload = {'recipient' : {'id': recipient_id}}
	response_payload['message'] = {'text' : text}
	send_response = requests.post(SEND, response_payload)
	return send_response

# Create your views here.
@csrf_exempt
def generate(request):
	print(request)
	if request.method == 'GET':
		if 'hub.verify_token' in request.GET and request.GET['hub.verify_token'] == '2318934571':
				return HttpResponse(request.GET['hub.challenge'])
		else:
			return HttpResponse()
	print(request.POST)
	all_messages = request.POST.get('entry')
	for m in all_messages:
		m = m['messaging']
		user_text = m['message']['text']
		send_status_message(m['sender']['id'], "Give us a second! We're working on it.")
		# make a call to wit.ai.
		response = parse_user_input(user_text)
		meme_type, caption_top, caption_bottom = parse_from_wit(response)
		# make a call to imageflip
		payload_url = meme_through_imgflip(meme_type, caption_top, caption_bottom)
		response_payload = {'recipient' : {'id': m['sender']['id']}}
		response_payload['message'] = {'attachment' : {'type' : 'image', 'payload' : {'url' : payload_url, 'is_reusable'  :True}}}
		send_response = requests.post(SEND, response_payload)
		# store send response reusable FBID.
		return HttpResponse(status=200)
