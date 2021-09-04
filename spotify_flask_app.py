from flask import Flask, render_template
import pandas as pd
from Spotify_playlist_analysis import get_current_playing_track_info, plot_recently_played, get_recently_played_tracks

scope_auth = "user-read-private user-library-read user-read-private user-read-currently-playing user-read-recently-played user-follow-read playlist-read-private playlist-modify-public user-modify-playback-state"

app = Flask(__name__,template_folder="template_folder")

@app.route('/')
def intro_fn():
	graphJSON = plot_recently_played("recently_played.csv")
	print (graphJSON)
	return render_template("recently_played.html",graphJSON=graphJSON)
@app.route('/recently_played')
def recently_played_songs():
	graphJSON = plot_recently_played("recently_played.csv")
	print (graphJSON)
	return render_template("recently_played.html",graphJSON=graphJSON)
@app.route('/display_songs')
def display_songs():
	track_info = get_recently_played_tracks(scope_auth, "recently_played.csv")
	track_names = []
	for i in track_info:
		track_names.append(i["name"])
	return render_template("recently_played.html",songs=track_names)
if __name__ =="__main__":
	app.run(host="0.0.0.0",port=6770)