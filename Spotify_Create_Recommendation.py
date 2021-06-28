import spotipy,os,sys
from csv import DictWriter
from csv import DictReader
from Spotify_playlist_analysis import get_track_recommendation, create_recommended_playlist
from spotipy.oauth2 import SpotifyOAuth

scope_auth = "user-library-read user-read-private user-read-currently-playing user-read-recently-played user-follow-read playlist-read-private"
SPOTIPY_CLIENT_ID = "800343d83a574916a368c4d9a7910859"
SPOTIPY_CLIENT_SECRET = "c6c4482bee4843828a4b768aeb1ddec0"
SPOTIPY_REDIRECT_URI = "http://localhost:1419"
os.environ['SPOTIPY_CLIENT_ID'] = SPOTIPY_CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI

def curateMixTape(recently_played_list):
	track_db = {}
	with open(recently_played_list, encoding = "cp1252") as csvObj:
		csvReader = DictReader(csvObj)
		for rows in csvReader:
			key_id = rows["Category"]
			track_db.setdefault(key_id,[]).append({"name": rows["name"], "uri": rows["uri"],"id": rows["id"]})
	return track_db
def readCSVJSON(recently_played_list, recommended_played_list):
	track_db = {}
	with open(recently_played_list, encoding = "cp1252") as csvObj:
		csvReader = DictReader(csvObj)
		for rows in csvReader:
			key_id = rows["Category"]
			track_db.setdefault(key_id,[]).append({"name": rows["name"], "uri": rows["uri"],"id": rows["id"]})
	
	with open(recommended_played_list, encoding ="cp1252") as csvObj2:
		csvReader2 = DictReader(csvObj2)
		for rows in csvReader2:
			key_id = rows["predicted_category"]
			track_db.setdefault(key_id,[]).append({"name": rows["name"], "uri": rows["uri"],"id": rows["id"]})
	#csvReader.close()
	#csvReader2.close()
	return track_db

def play_categorical_track(track_db,key,scope):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	list_of_songs = []
	name_of_songs = []
	for i in track_db[key]:
		list_of_songs.append(i["uri"])
		name_of_songs.append(i["name"])
	print (name_of_songs)
	#sp.start_playback(uris=list_of_songs[::-1])
	create_recommended_playlist(scope_auth,"My Current Mix - QB Queen"+key,list_of_songs[::-1])

	

def get_saved_lib_tracks(scope):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_saved_tracks()
	for i in range(10):
		print (results['items'][i]['track']['name'], (results['items'][i]['track']['id']))

def get_current_playing_track_info(scope):
	track_db = {}
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_playing_track()
	print (results["item"].keys())
	print (results["item"]["name"])
	print (results["item"]["type"])
	track_name = results['item']['name']
	track_id = results['item']['id']
	track_uri = results['item']['uri']
	track_db[track_id] = [track_name, track_uri]
	return track_db

if __name__ == "__main__":
	categorised_db = readCSVJSON(sys.argv[1],sys.argv[2])
	play_categorical_track(categorised_db,sys.argv[3],scope_auth)
	#track_db = get_current_playing_track_info(scope_auth)
	#get_track_recommendation(scope_auth, track_db)

