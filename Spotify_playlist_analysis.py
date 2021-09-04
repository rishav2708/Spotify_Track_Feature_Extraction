import spotipy,os,sys,random,glob
from csv import DictWriter
from csv import DictReader
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import plotly.graph_objects as go
import plotly
import matplotlib.pyplot as plt
import pandas as pd
import json
import pickle
from bottle import request
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from numpy import dot
from numpy.linalg import norm
from time import sleep
scope_auth = "user-read-private user-library-read user-read-private user-read-currently-playing user-read-recently-played user-follow-read playlist-read-private playlist-modify-public user-modify-playback-state user-top-read"
SPOTIPY_CLIENT_ID = "800343d83a574916a368c4d9a7910859"
SPOTIPY_CLIENT_SECRET = "c6c4482bee4843828a4b768aeb1ddec0"
OAUTH_AUTHORIZE_URL =  'https://accounts.spotify.com/authorize'
SPOTIPY_REDIRECT_URI = "http://localhost:1419"
CACHE = '.spotipyoauthcache'
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
	return (track_contents)

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
	try:
		os.remove(file_name)
	except:
		print ("okay")
	sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, OAUTH_AUTHORIZE_URL, SPOTIPY_REDIRECT_URI,scope=scope_auth)
	sp = spotipy.Spotify(oauth_manager=sp_oauth)
	#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_recently_played(limit=50)
	track_info = []
	for i in results["items"]:
		track_name = i["track"]["name"]
		track_id = i["track"]["id"]
		track_info.append(get_audio_features_tracks(file_name, sp, track_name, track_id))
	return track_info

def find_pitch_vector_similarity(file_name):
	sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, OAUTH_AUTHORIZE_URL, SPOTIPY_REDIRECT_URI,scope=scope_auth)
	sp = spotipy.Spotify(oauth_manager=sp_oauth)
	data_dump = open(file_name).read()
	segment_info = json.loads(data_dump)
	pitcher_array = []
	max_pitcher_mapper_length = 0
	for i in range(len(segment_info)):
		pitch_mapper = []
		for segment in segment_info[i]["segments"]:
			pitch_mapper.append(segment["pitches"])
			if(max_pitcher_mapper_length < len(pitch_mapper)):
				max_pitcher_mapper_length = len(pitch_mapper)
		pitcher_array.append(pitch_mapper)
	print ("Choose the song, you want to fuse:\n")
	cosine_sim_matrix = {}
	for i in range(len(pitcher_array)):
		cosine_sim_matrix[i] = {}
		for j in range(len(pitcher_array)):
			if (i!= j):
				cosine_sim_matrix[i][j] = []
				for pitch_vector_i in  pitcher_array[i]:
					similar_pitch_vector = []
					for pitch_vector_j in pitcher_array[j]:
						cos_sim = round((dot(pitch_vector_i,pitch_vector_j)/(norm(pitch_vector_i)*norm(pitch_vector_j))),2)
						similar_pitch_vector.append(cos_sim)
					cosine_sim_matrix[i][j].append(similar_pitch_vector)
			else:
				cosine_sim_matrix[i][j] =[]
	with open("cosine_sim_matrix.json","w") as SimMatrix:
			json.dump(cosine_sim_matrix, SimMatrix, ensure_ascii=False,indent=4)
	print ("Pick one song to listen to its fusion:")
	for i in range(len(segment_info)):
		print (str(i)+"."+segment_info[i]["name"][0])
	song1 = int(input())
	idx_saver_data_structure={}
	for song in cosine_sim_matrix[song1]:
		for rows in range(len(cosine_sim_matrix[song1][song])):
			song_seg_idx = []
			for cols in range(len(cosine_sim_matrix[song1][song][rows])):
				if (cosine_sim_matrix[song1][song][rows][cols] >= 0.90):
					song_seg_idx.append((song,cols))
			print (song_seg_idx)
			idx_saver_data_structure.setdefault(rows,[]).append(song_seg_idx)
	with open("selected_segs.json","w") as SegObj:
		json.dump(idx_saver_data_structure, SegObj, ensure_ascii=False,indent=4)
	print ("Choose Segment:\n")
	for segs in idx_saver_data_structure:
		length_of_seg = sum([len(i) for i in idx_saver_data_structure[segs]])
		print ("Segment Number: " + str(segs) + "Clubbed Segs: "+ str(length_of_seg)+"\n")
	og_seg_number = int(input())
	original_song_name = segment_info[song1]["name"][0]
	original_song_uri = segment_info[song1]["name"][1]
	original_song_segment_start_time = segment_info[song1]["segments"][og_seg_number]["start"]
	original_song_segment_duration = segment_info[song1]["segments"][og_seg_number]["duration"]
	sp.start_playback(uris=[original_song_uri],position_ms=original_song_segment_start_time*100)
	sleep(original_song_segment_duration*5)
	for song_lists in (idx_saver_data_structure[og_seg_number]):
		if (len(song_lists) ==0):
			continue
		else:
			for song_tuple in song_lists:
				try:
					song_idx = int(song_tuple[0])
					seg_idx = int(song_tuple[1])
					song_uri = segment_info[song_idx]["name"][1]
					seg_start_time = segment_info[song_idx]["segments"][seg_idx]["start"]
					seg_duration = segment_info[song_idx]["segments"][seg_idx]["duration"]
					sp.start_playback(uris=[song_uri],position_ms=seg_start_time*100)
					sleep(seg_duration*20)
				except:
					continue
	#	sp.start_playback(uris=[song_uri], offset={"position":0}, position_ms=t_start*(100))
	#	for song_tuple in segs:
	#		song_idx

	#sp.start_playback(uris=[song_uri], offset={"position":0}, position_ms=t_start*(100))
	
def get_audio_analysis_tracks(sp, track_name, track_id):
	sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, OAUTH_AUTHORIZE_URL, SPOTIPY_REDIRECT_URI,scope=scope_auth)
	sp = spotipy.Spotify(oauth_manager=sp_oauth)
	results = sp.audio_analysis(track_id)
	segment_info = {}
	segment_info["name"] = track_name
	segment_info["tempo"] = sp.audio_features(track_id)[0]["tempo"]
	segment_info["segments"] = []
	for i in range (len(results["segments"])):
		if ((results["segments"][i]["duration"] >= 1.2) and results["segments"][i]["confidence"] >=0.4):
			seg_idx_dict = {}
			seg_idx_dict["start"] = results["segments"][i]["start"]
			seg_idx_dict["duration"] =results["segments"][i]["duration"]
			seg_idx_dict["pitches"] =results["segments"][i]["pitches"]
			seg_idx_dict["timbre"] =results["segments"][i]["timbre"]
			seg_idx_dict["timbre"] =results["segments"][i]["timbre"]
			segment_info["segments"].append(seg_idx_dict)
		else:
			continue
			#print (results["segments"][i]["pitches"])
		#print (results["segments"][i]["timbre"])

	#for i in range(len(results["sections"])):
		#print (results["sections"][i]["time_signature"]+results["sections"][i]["time_signature_confidence"])
	return (segment_info)
	
	#print (audio_analysis_JSONObj)
def get_current_playing_track_info(scope):
	file_name = "currently_playing.csv"
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	results = sp.current_user_playing_track()
	track_name = results['item']['name']
	track_id = results['item']['id']
	get_audio_features_tracks(file_name, sp, track_name, track_id)
	get_audio_analysis_tracks(sp,track_name,track_id)
	return_string = track_name+" "+track_id
	print (return_string)
	return return_string

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
def get_current_top_tracks(scope, term_range):
	sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
	resp = sp.current_user_top_tracks(time_range=term_range)
	tracks = resp["items"]
	popular_top_tracks = {}
	for i in tracks:
		popular_top_tracks.setdefault(i["id"],[]).append({"name":i["name"],term_range:i["popularity"],"url":i["url"]})



def cluster_elbow(data_frame):
	distortions =[]
	K =range(3,15)
	for k in K:
		kMeanModel = KMeans(n_clusters=k)
		kMeanModel.fit(data_frame)
		distortions.append(kMeanModel.inertia_)
	plt.figure(figsize=(16,8))
	plt.plot(K,distortions,"bx-")
	plt.xlabel("k")
	plt.ylabel("Distortions")
	plt.show()
	optimal_k = 8
	data_frame = create_cluster(data_frame,optimal_k)
	return (data_frame)
def create_cluster(data_frame,optimal_k):
	kmeans = KMeans(n_clusters=optimal_k, random_state=1).fit(data_frame)
	cluster_labels = kmeans.labels_
	data_frame["cluster"]= pd.Series(cluster_labels,index =data_frame.index)
	return data_frame
def train_DataSet(column_list, dataframe_train_X, dataframe_Result_Y):
	print (dataframe_train_X[:])
	print (dataframe_Result_Y)
	train_set_X= df.iloc[:,range(len(column_list))]
	test_result_Y

def plot_recently_played(file_name):
	scaler = MinMaxScaler()
	df = pd.read_csv(file_name)
	thetas = ["danceability","loudness","speechiness","acousticness","instrumentalness","liveness","valence","tempo"]
	df2 = pd.DataFrame(df,columns=thetas)
	df2 = scaler.fit_transform(df2)
	df2 = pd.DataFrame(df2)
	df2 = cluster_elbow(df2)
	#train_DataSet(thetas,df2,df2["cluster"])
	df = df.to_dict("index")
	df2 = df2.to_dict("index")
	#print (df2.keys())
	#print (df2[7][0])
	print (df[0])
	data_plot =[]
	for i in range(1,len(df.keys())):
		radials = []
		for theta in range(len(thetas)):
			radials.append(df2[i][theta])
		data_plot.append(go.Scatterpolar(r=radials,theta=thetas,name=df[i]["name"]))
	
	figure = go.Figure(data=data_plot)
	figure.update_layout(title =df[7]["name"])
	figure.update_traces(fill="toself")
	#figure.show()
	graphDump = json.dumps(figure, cls = plotly.utils.PlotlyJSONEncoder)
	return graphDump

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
	elif (starter =="get_current_top_tracks"):
		get_current_top_tracks(scope_auth)
	elif (starter =="plot_graph"):
		plot_recently_played(sys.argv[2])
	elif (starter =="get_audio_analysis"):
		track_info_db = readCSVJSON(sys.argv[2])
		segment_info = []
		for iid in track_info_db:
			track_name = track_info_db[iid]
			track_id = iid
			segmentOBJ = get_audio_analysis_tracks(scope_auth, track_name, track_id)
			segment_info.append(segmentOBJ)
		with open("audio_analysis_data.json","w") as ObjFile:
			json.dump(segment_info, ObjFile, ensure_ascii=False,indent=4)
	elif (starter == "create_fusion"):
		find_pitch_vector_similarity("audio_analysis_data.json")
	else:
		print ("pass valid param")

if __name__ == "__main__":
	main()
