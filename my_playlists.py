
from flask import Flask
from flask import render_template, request, g, url_for, redirect
from flask import Blueprint
from recommend.auth import login_required
from recommend.db import get_db, fetch_raw_listener_data

app = Flask(__name__)

bp = Blueprint("my_playlists", __name__, url_prefix="/my_playlists")

@bp.route('/')
@login_required
def index():
    '''Renders the my playlists of the app'''
    username = g.user["username"]
    db = get_db()
    playlists = db.execute('SELECT * FROM recommendations WHERE username=?', (username, )).fetchall()
    playlists_output = []#cleans up the data fetched raw from database
    for i in playlists:
        id = i[0]
        song_uris = i[4].split(';')
        picture = db.execute('SELECT photo_link FROM songs WHERE uri=?', (song_uris[0], )).fetchone()[0]
        song_titles = i[3].split(';')
        playlist_title = i[1]
        print(picture, song_uris, song_titles, playlist_title)
        playlists_output.append([id, picture, song_uris, song_titles, playlist_title])
    return render_template('my_playlists.html', playlists=playlists_output)

@bp.route('/<int:id>')
#@login_required WARNING: commenting out this decorator means anyone can access any playlist of recommendations. This may compromise the integrity of the app.
def open_indv_playlist(id):
    '''Renders the my playlists of the app'''
    db = get_db()
    playlist = db.execute('SELECT * FROM recommendations WHERE id=?', (id, )).fetchone()
    playlist_uris = playlist[4].split(';')
    playlist_titles = playlist[3].split(';')
    playlist_items = []
    for j, i in enumerate(playlist_uris):
        if i.split(':')[1] == 'artist':
            playlist_items.append(db.execute('SELECT artist, photo_link FROM artists WHERE uri=?', (i, )).fetchone())
        elif i.split(':')[1] == 'track':
            playlist_items.append(db.execute('SELECT title, photo_link, artist_name, preview_url FROM songs WHERE uri=?', (i, )).fetchone())
    #for i in playlist_items: print(list(i))
    return render_template('playlist.html', playlist_title=playlist[1], playlist_items=playlist_items)
