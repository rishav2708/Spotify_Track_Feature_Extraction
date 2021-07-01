import spotipy,os,sys,random,glob
from csv import DictWriter
from csv import DictReader
from spotipy.oauth2 import SpotifyOAuth

scope_auth = "user-read-private user-library-read user-read-private user-read-currently-playing user-read-recently-played user-follow-read playlist-read-private playlist-modify-public user-modify-playback-state"
SPOTIPY_CLIENT_ID = "800343d83a574916a368c4d9a7910859"
SPOTIPY_CLIENT_SECRET = "c6c4482bee4843828a4b768aeb1ddec0"
SPOTIPY_REDIRECT_URI = "http://localhost:1419"
os.environ['SPOTIPY_CLIENT_ID'] = SPOTIPY_CLIENT_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = SPOTIPY_CLIENT_SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = SPOTIPY_REDIRECT_URI
current_play_list = []
def create_recommended_playlist(scope, playlist_name,track_uris,description_text):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	user_info = sp.current_user() 
	playlist_info = sp.user_playlist_create(user_info["id"], playlist_name, public = True, collaborative = False, description = description_text)
	#track_uris =[track_db[key][1] for key in track_db.keys()]
	tot_len = 0
	while (tot_len <= len(track_uris)):
		sp.user_playlist_add_tracks(user_info["id"],playlist_info["id"],track_uris[tot_len:tot_len+100])
		tot_len+=100
def get_audio_features_tracks(file_name,spObj,track_name, track_id):
	results = spObj.audio_features(track_id)
	#print (list(results[0].keys()))
	print (track_name, results[0])
	track_features = ["name"] + list(results[0].keys())
	track_contents = results[0]
	track_contents["name"] = track_name
	writeToCSV(file_name,track_features,track_contents)

def get_track_recommendation(file_name, scope, track_db):
	track_db_keys = list(track_db.keys())
	print (len(track_db_keys))
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	for i in range(0, len(track_db_keys)-5):
		results = sp.recommendations(seed_tracks=track_db_keys[i:i+4])
		for j in results["tracks"]:
			track_name = j["name"]
			track_id = j["id"]
			get_audio_features_tracks(file_name,sp, track_name, track_id)
	#print (results["tracks"][0])
def readCSVJSON(file_name):
	track_db = {}
	with open(file_name, encoding = "cp1252") as csvObj:
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
	with open(file_name,"a", newline ="", encoding = "cp1252") as csv_obj:
		dict_Obj = DictWriter(csv_obj, dialect = "excel", fieldnames = field_names)
		if not file_exists:
			dict_Obj.writeheader()
		try:
			dict_Obj.writerow(track_contents)
		except:
			print ("skipping this part")
			pass
		csv_obj.close()


def get_saved_lib_tracks(scope):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_saved_tracks()
	for i in range(10):
		print (results['items'][i]['track']['name'], (results['items'][i]['track']['id']))

	

def get_user_following(scope,file_name):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	#results_users = sp.current_user_followed_users(limit=20)
	results_artists = sp.current_user_followed_artists(limit=20)
	#print (results_users)
	artist_lists = results_artists["artists"]["items"]
	for i in range(len(artist_lists)):
		res1 = sp.artist_top_tracks(artist_lists[i]["id"])
		for j in res1["tracks"]:
			track_name = j["name"]
			track_id = j["id"]
			get_audio_features_tracks(file_name,sp,track_name,track_id)
def get_recently_played_tracks(scope,file_name):
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
	#print (track_uris)
	random_seed = random.randint(0, len(track_uris))
	print ("random seed"+str(random_seed))
	sp.start_playback(uris=track_uris, offset={"position":random_seed})

def del_user_playlist_tracks(scope):
	print ("This will delete your playlists")
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	user_info = sp.current_user() 
	results = sp.current_user_playlists()
	print (results.keys())
	menu_num = 1
	album_dict = {}
	for i in results["items"]:
		print (menu_num, i["name"], i["uri"], i["id"])
		album_dict[menu_num]= {"id":i["id"],"name":i["name"]}
		menu_num +=1
	print ("Choose playlists to delete:")
	list_playlists = [int(i) for i in input().split(" ")]
	for i in list_playlists:
		playlist_id = album_dict[i]["id"]
		playlist_name = album_dict[i]["name"]
		print ("deleting now..."+playlist_name+" "+playlist_id)
		sp.user_playlist_unfollow(user_info["id"],playlist_id)

def get_user_playlist_tracks(scope, file_name):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	user_info = sp.current_user() 
	results = sp.current_user_playlists()
	print (results.keys())
	menu_num = 1
	album_dict = {}
	for i in results["items"]:
		print (menu_num, i["name"], i["uri"], i["id"])
		album_dict[menu_num]= {"id":i["id"],"name":i["name"]}
		menu_num +=1
	print ("Choose one album:")
	album_menu_list = [int(i) for i in input().split(" ")]
	#file_name = "playlist"+album_dict[album_menu_num]["name"]+".csv"
	for album_menu_num in album_menu_list:
		res1 = sp.user_playlist_tracks(user_info["id"],album_dict[album_menu_num]["id"])
		for i in res1["items"]:
			print (i["track"]["name"], i["track"]["id"])
			track_name = i["track"]["name"]
			track_id = i["track"]["id"]
			get_audio_features_tracks(file_name, sp, track_name, track_id)
	
	#res1["items"][0]["track"]["name"]
def search_spotify(scope, search_term, search_type):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.search(q=search_term,type="track")
	file_name = "searched_tracks.csv"
	print (results.keys())
	items= results["tracks"]["items"]
	tracking_num = 1
	track_db = {}
	for i in items:
		print (str(tracking_num)+". "+i["name"]+","+i["id"])
		track_db[tracking_num] = {"name":i["name"],"id":i["id"]}
		artist_lists = "Artists: "
		for all_artists in i["artists"]:
			artist_lists+= (all_artists["name"]+",")
		print (artist_lists)
		tracking_num+=1
	print ("Choose from the above list")
	chosen_items = [int(i) for i in input().split(" ")]
	for chosen_one in chosen_items:
		get_audio_features_tracks(file_name, sp, track_db[chosen_one]["name"], track_db[chosen_one]["id"])

def main():
	starter = sys.argv[1]
	print (starter)

	if(starter =="currently_playing"):
		get_current_playing_track_info(scope_auth)
	elif (starter =="recently_played"):
		get_recently_played_tracks(scope_auth, sys.argv[2])
	elif (starter =="following"):
		get_user_following(scope_auth,sys.argv[2])
	elif (starter =="recommend"):
		track_db = readCSVJSON(sys.argv[2])
		recommend_file_name = sys.argv[2][:-4]+"recommended.csv"
		print (recommend_file_name)
		get_track_recommendation(recommend_file_name,scope_auth, track_db)
	elif (starter =="play_randomized_playlist"):
		track_db = readCSVJSON("recommended_list.csv")
		play_curated_list(scope_auth, track_db)
	elif (starter =="create_recommended_playlist"):
		track_db = readCSVJSON("recommended_list.csv")
		create_recommended_playlist(scope_auth,track_db)
	elif (starter =="curate_tracks_from_playlist"):
		get_user_playlist_tracks(scope_auth, sys.argv[2])
	elif (starter =="delete_playlists"):
		del_user_playlist_tracks(scope_auth)
	elif (starter =="search_spotify"):
		search_spotify(scope_auth,sys.argv[2], sys.argv[3])
	elif (starter =="delete_all_csv_files"):
		for i in (glob.glob("*.csv")):
			os.remove(i)
	else:
		print ("pass valid param")

if __name__ == "__main__":
	main()
