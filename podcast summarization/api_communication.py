import requests
from api_secrets import API_KEY_ASSEMBLYAI, API_KEY_LISTENNOTES
import time
import pprint
import json

transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
headers_assemblyai = {'authorization': API_KEY_ASSEMBLYAI,
                      'content-type': "application/json"}

listennotes_episode_endpoint = "https://listen-api.listennotes.com/api/v2/episodes"
headers_listennotes = {'X-ListenAPI-Key': API_KEY_LISTENNOTES,}

def get_episode_audio_url(episode_id):
    url = listennotes_episode_endpoint + '/' + episode_id
    response = requests.request('GET', url, headers=headers_listennotes)

    #pprint.pprint(data)
    
    data = response.json()
    thumbnail = data['thumbnail']
    podcast_title = data['podcast']['title']
    episode_title = data['title']
    audio_url = data['audio']

    return audio_url, thumbnail, podcast_title, episode_title


#transcribe
def transcribe(audio_url, auto_chapters):

    transcript_request = {'audio_url': audio_url,
                          'auto_chapters': auto_chapters}
    
    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers_assemblyai)
    pprint.pprint(transcript_response.json())
    return transcript_response.json()['id']



#poll
def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers = headers_assemblyai)
    return polling_response.json()

def get_transcription_result_url(audio_url, auto_chapters):
    transcript_id = transcribe(audio_url, auto_chapters)
    while True:
        data = poll(transcript_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']
        
        print("waiting 60 seconds...")
        time.sleep(60)



#save transcript
def save_transcript(episode_id):
    audio_url, thumbnail, podcast_title, episode_title = get_episode_audio_url(episode_id)
    data, error = get_transcription_result_url(audio_url, auto_chapters= True)

    if data:
        filename = episode_id + '.txt'
        with open(filename, 'w')as f:
            f.write(data['text'])

        filename = episode_id + '_chapters.json'
        with open(filename, 'w') as f:
            chapters = data['chapters']

            data = {'chapters': chapters}
            data['audio_url'] = audio_url
            data['thumbnail'] = thumbnail
            data['episode_title'] = episode_title
            data['podcast_title'] = podcast_title
            
            json.dump(data, f, indent=4)
            print("Transcript saved")
            return True
    
    elif error:
        print("Error!!", error)
        return False
