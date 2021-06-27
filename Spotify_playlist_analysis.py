import spotipy,os,sys,random
from csv import DictWriter
from csv import DictReader
from spotipy.oauth2 import SpotifyOAuth

scope_auth = "user-read-private user-library-read user-read-private user-read-currently-playing user-read-recently-played user-follow-read playlist-read-private playlist-modify-public user-modify-playback-state"
SPOTIPY_CLIENT_ID = #Your Spotify Client ID
SPOTIPY_CLIENT_SECRET = #Your Spotify Client Secret
SPOTIPY_REDIRECT_URI = "http://localhost:1419"
os.environ['SPOTIPY_CLIENT_ID'] = SPOTIPY_CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI
current_play_list = []
def create_recommended_playlist(scope, track_db):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	user_info = sp.current_user()
	playlist_info = sp.user_playlist_create(user_info["id"], "Recommended For Today", public = True, collaborative = False, description = "Based on what you are recently listening")
	track_uris =[track_db[key][1] for key in track_db.keys()]
	sp.user_playlist_add_tracks(user_info["id"],playlist_info["id"],track_uris)
def get_audio_features_tracks(file_name,spObj,track_name, track_id):
	results = spObj.audio_features(track_id)
	#print (list(results[0].keys()))
	print (track_name, results[0])
	track_features = ["name"] + list(results[0].keys())
	track_contents = results[0]
	track_contents["name"] = track_name
	writeToCSV(file_name,track_features,track_contents)

def get_track_recommendation(scope, track_db):
	track_db_keys = list(track_db.keys())
	print (len(track_db_keys))
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.recommendations(seed_tracks=track_db_keys[0:5])
	for i in results["tracks"]:
		track_name = i["name"]
		track_id = i["id"]
		get_audio_features_tracks("recommended_list.csv",sp, track_name, track_id)
	#print (results["tracks"][0])
def readCSVJSON(file_name):
	track_db = {}
	with open(file_name, encoding = "utf-8") as csvObj:
		csvReader = DictReader(csvObj)
		for rows in csvReader:
			key_id = rows["id"]
			track_db[key_id] = [rows["name"], rows["uri"]]
	return track_db
def writeToCSV(file_name, track_features, track_contents):
	field_names = track_features
	print (field_names)
	print (track_contents)
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

	

def get_user_following(scope):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	#results_users = sp.current_user_followed_users(limit=20)
	results_artists = sp.current_user_followed_artists(limit=20)
	#print (results_users)
	artist_lists = results_artists["artists"]["items"]
	for i in range(len(artist_lists)):
		print (artist_lists[i]["name"])
		print (artist_lists[i]["popularity"])
		print (artist_lists[i]["genres"])
def get_recently_played_tracks(scope):
	file_name = "recently_played_tracks.csv"
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_recently_played(limit=50)
	#print (results.keys())
	#print (results["items"][10].keys())
	#print (results["items"][10])
	for i in results["items"]:
		#print(i["played_at"], i["track"]["name"], i["track"]["id"])
		track_name = i["track"]["name"]
		track_id = i["track"]["id"]
		get_audio_features_tracks(file_name, sp, track_name, track_id)
		#track_iter.append(i["track"]["name"])
		#print ("Context:"+i["context"]+" Played At:"+i["played_at"]+" Name:"+i["track"]["name"])
	#print (results["cursors"])
def get_current_playing_track_info(scope):
	file_name = "currently_playing.csv"
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_playing_track()
	track_name = results['item']['name']
	track_id = results['item']['id']
	get_audio_features_tracks(file_name, sp, track_name, track_id)
	#get_audio_analysis_tracks(sp,track_name,track_id)

def play_curated_list(scope,track_db):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	track_uris =[track_db[key][1] for key in track_db.keys()]
	print (track_uris)
	random_seed = random.randint(0, len(track_uris))
	sp.start_playback(uris=track_uris, offset={"position":random_seed})


def main():
	starter = sys.argv[1]
	print (starter)

	if(starter =="currently_playing"):
		get_current_playing_track_info(scope_auth)
	elif (starter =="recently_played"):
		get_recently_played_tracks(scope_auth)
	elif (starter =="following"):
		get_user_following(scope_auth)
	elif (starter =="recommend"):
		track_db = readCSVJSON(sys.argv[2])
		get_track_recommendation(scope_auth, track_db)
	elif (starter =="play_randomized_playlist"):
		track_db = readCSVJSON("recommended_list.csv")
		play_curated_list(scope_auth, track_db)
	elif (starter =="create_recommended_playlist"):
		track_db = readCSVJSON("recommended_list.csv")
		create_recommended_playlist(scope_auth,track_db)
	else:
		print ("pass valid param")

if __name__ == "__main__":
	main()
