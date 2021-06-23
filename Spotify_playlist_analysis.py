import spotipy,os,sys
from csv import DictWriter

from spotipy.oauth2 import SpotifyOAuth

#scope = "user-library-read"
scope = "user-read-currently-playing"
SPOTIPY_CLIENT_ID = "800343d83a574916a368c4d9a7910859"
SPOTIPY_CLIENT_SECRET = "1dabe407bf0d45a4b85dcef282ca53f5"
SPOTIPY_REDIRECT_URI = "http://localhost:1419"
os.environ['SPOTIPY_CLIENT_ID'] = SPOTIPY_CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI
current_play_list = []

def writeToCSV(track_features, track_contents):
	field_names = track_features
	print (field_names)
	print (track_contents)
	file_name = "current_songs_feature.csv"
	file_exists = os.path.isfile(file_name)
	with open(file_name,"a", newline ="") as csv_obj:
		dict_Obj = DictWriter(csv_obj, dialect = "excel", fieldnames = field_names)
		if not file_exists:
			dict_Obj.writeheader()
		dict_Obj.writerow(track_contents)
		csv_obj.close()


def get_saved_lib_tracks(scope):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_saved_tracks()
	for i in range(10):
		print (results['items'][i]['track']['name'], (results['items'][i]['track']['id']))

def get_audio_features_tracks(spObj,track_name, track_id):
	results = spObj.audio_features(track_id)
	#print (list(results[0].keys()))
	print (track_name, results[0])
	track_features = ["name"] + list(results[0].keys())
	track_contents = results[0]
	track_contents["name"] = track_name
	writeToCSV(track_features,track_contents)

def get_current_playing_track_info(scope):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_playing_track()
	track_name = results['item']['name']
	track_id = results['item']['id']
	get_audio_features_tracks(sp, track_name, track_id)

def main():
	get_current_playing_track_info(scope)


if __name__ == "__main__":
	main()
