from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
import requests
import unicodedata
import json
from bs4 import BeautifulSoup

app = Flask(__name__)

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


s = requests.session()

def get_video(url):
	try:
		r = requests.get(url=url)


		soup = BeautifulSoup(r.content, "html.parser")

		s = soup.find("body")

		var_obj = s.find_all("script")[0].contents[0].replace("var ytInitialPlayerResponse = ", "[")
		var_obj = var_obj.replace("};", "}]")

		js= json.loads(var_obj)[0]

		#print(js)

		formats = js['streamingData']['formats']
		adaptiveFormats = js['streamingData']['adaptiveFormats']

		videoDetails = js['videoDetails']

		thumbnails = videoDetails["thumbnail"]["thumbnails"]
		thumbnails.reverse()

		thumbnail_url = thumbnails[0]['url']

		title = videoDetails['title']


		video_full_obj = {
			'title': title,
			'thumbnail': thumbnail_url,
			'formats': []
		}


		for f in formats:
			#print(f)
			quality = f['quality']
			video_url = f['url']
			
			if 'qualityLabel' in f.keys():
				quality = f['qualityLabel']
			
			obj = {
				'quality': quality,
				'video_url': video_url
			}
			
			video_full_obj['formats'].append(obj)

		for af in adaptiveFormats:
			video_url = af['url']
			type = af['mimeType'].split(";")[0].split("/")[0]
			if type == "audio":
				audio_obj = af
				
				obj = {
					'quality': 'Audio Only',
					'video_url': video_url
				}
				video_full_obj['formats'].append(obj)
				break


		return [video_full_obj]
	except Exception as e:
		print(e)
	
	return []
	
	
@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def home():
	
	data = {"ping": True}
	print(request.form)

	

	response = app.response_class(
		response=json.dumps(data),
		status=200,
		mimetype='application/json'
	)
	return response
	
	
@app.route('/download', methods=['GET', 'POST'])
@cross_origin()
def download_video():
	
	data = {}
	
	try:
		url = request.form['my_video_url']
		data = get_video(url)
	except Exception as e:
		print(e)

	response = app.response_class(
		response=json.dumps(data, ensure_ascii=False).encode('utf8'),
		status=200,
		mimetype='application/json'
	)
	return response	





if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=7450, debug=True)#, debug=True
    

