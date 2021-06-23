import spotipy,os,sys
from csv import DictWriter

from spotipy.oauth2 import SpotifyOAuth

scope_user_lib = "user-library-read"
scope_user_current_read = "user-read-currently-playing"
scope_user_recently_played = "user-read-recently-played"
scope_user_follow_read ="user-follow-read"
SPOTIPY_CLIENT_ID = "800343d83a574916a368c4d9a7910859"
SPOTIPY_CLIENT_SECRET = "c6c4482bee4843828a4b768aeb1ddec0"
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

def get_audio_analysis_tracks(spObj, track_name, track_id):
	results = spObj.audio_analysis(track_id)
	print (results.keys())
	print("beats")
	print (results["beats"])

	
	

def get_audio_features_tracks(spObj,track_name, track_id):
	results = spObj.audio_features(track_id)
	#print (list(results[0].keys()))
	print (track_name, results[0])
	track_features = ["name"] + list(results[0].keys())
	track_contents = results[0]
	track_contents["name"] = track_name
	writeToCSV(track_features,track_contents)

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
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_recently_played(limit=50)
	track_iter = []
	#print (results.keys())
	#print (results["items"][10].keys())
	#print (results["items"][10])
	for i in results["items"]:
		#print(i["played_at"], i["track"]["name"], i["track"]["id"])
		track_iter.append(i["track"]["name"])
		#print ("Context:"+i["context"]+" Played At:"+i["played_at"]+" Name:"+i["track"]["name"])
	#print (results["cursors"])
	print (track_iter)
def get_current_playing_track_info(scope):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_playing_track()
	track_name = results['item']['name']
	track_id = results['item']['id']
	get_audio_features_tracks(sp, track_name, track_id)
	#get_audio_analysis_tracks(sp,track_name,track_id)

def main():
	starter = sys.argv[1]
	print (starter)

	if(starter =="currently_playing"):
		get_current_playing_track_info(scope_user_current_read)
	elif (starter =="recently_played"):
		get_recently_played_tracks(scope_user_recently_played)
	elif (starter =="following"):
		get_user_following(scope_user_follow_read)
	else:
		print ("pass valid param")

if __name__ == "__main__":
	main()
