
from flask import Flask, g, redirect, url_for
from flask import Blueprint
from recommend.auth import login_required
from sklearn.cluster import KMeans
from recommend.db import get_db
from kneed import KneeLocator
from recommend.fourier import generate_fourier_from_uri_list, convert_fourier_to_string
from recommend.api.api_call import get_related_artists, get_related_artists_for_track_in_db
from recommend.generate_recommendations import generate_recommendations

app = Flask(__name__)

bp = Blueprint("generate_playlists", __name__, url_prefix="/add_tastes/generate_playlists")


@bp.route('/')
@login_required
def index():
    '''Runs all of the scripts necessary to cluster the data the user has entered into playlists.'''

    # 1. Fetch all of the songs and artists (raw listener data) of the current user
    username = g.user["username"]
    db = get_db()
    r = db.execute('SELECT listener_data FROM listener_raw_data WHERE username=?', (username,)).fetchall()

    # 2. Setting up variables
    af = {} # audio_features dictionary, af[<spotify_uri>] = [<spotify_audio_features>]
    titles = []
    indexes = [2, 3, 5, 8, 9, 11]  # data deemed useful

    # 3. Iterates through all of the songs and tracks entered by the listener. All audio features data is stored in the central database, so it adds this to the af dictionary.
    for i in r:
        i = i[0]
        if i.split(':')[1] == 'artist':
            y = db.execute('SELECT * FROM artists WHERE uri=?', (i,)).fetchone()
            titles.append(y[0])
            af[i] = [y[x] for x in indexes]
        elif i.split(':')[1] == 'track':
            y = db.execute('SELECT * FROM songs WHERE uri=?', (i,)).fetchone()
            af[i] = [y[x] for x in indexes]
            titles.append(y[0])
        else:
            raise Exception('That does not appear to be a valid Spotify URI')

    # 4. Clusters songs in the newly created
    playlists = cluster_songs(af)


    # 5. Saving playlists to the database
    for i in list(playlists.keys()):
        related_artists = ';'.join(get_related_artists_for_playlist(playlists[i]))
        title, content, photo_link = generate_title_and_content_and_photo_link(playlists[i])
        fourier = convert_fourier_to_string(generate_fourier_from_uri_list(playlists[i]))
        y = db.execute('SELECT * FROM listener_profiles WHERE username=? AND listener_data=?', (username, ';'.join(playlists[i]))).fetchone()
        if y == None: #avoiding duplicates for user and listener data
            db.execute('INSERT INTO listener_profiles (username, title, listener_data, content, photo_link, fourier, related_artists, playlist_created_for) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (username, title, ';'.join(playlists[i]), content, photo_link, fourier, related_artists, 'False'))

    # 6. Commit changes to the database
    db.commit()

    # 7. Generate Recommendations based off of the newly created Listener Profiles
    playlists = db.execute("SELECT * FROM listener_profiles WHERE username=? AND playlist_created_for='False'", (username, )).fetchall()
    for playlist_id in playlists:
       generate_recommendations(playlist_id[0], username)

    db.close()



    # 8. The user will then be redirected the the 'My Playlists' page
    return redirect(url_for('my_playlists'))


def generate_title_and_content_and_photo_link(playlist):
    '''Based on the artists in the list, this generates a title, summary of genres, and cover art for the playlist'''
    username = g.user["username"]
    photo_links = []
    genres = []
    most_common_genres = []
    artists = []
    titles_currently_in_db = []
    genres_not_in_db = []
    photo_links_currently_in_db = []
    photo_links_not_in_db = []
    db = get_db()
    for i in playlist:
        if i.split(':')[1] == 'artist':
            artists.append(i)
        elif i.split(':')[1] == 'track':
            c = db.execute('SELECT photo_link, artist FROM songs WHERE uri=?', (i,)).fetchone()
            photo_links.append(c[0])
            artists.append('spotify:artist:' + c[1].split('/')[-1])
    for i in artists:
        try:
            c = db.execute('SELECT photo_link, genres FROM artists WHERE uri=?', (i,)).fetchone()
            photo_links.append(c[0])
            for j in c[1].split(', '): genres.append(j)
        except:
            pass
    for i in genres:
        if int(genres.count(i)) > 1: most_common_genres.append(i)
    if most_common_genres != []: genres = most_common_genres

    x = list(db.execute('SELECT title FROM listener_profiles WHERE username=?', (username,)).fetchall())
    for i in x:
        titles_currently_in_db.append(i[0])
    for i in genres:
        if i.title() not in titles_currently_in_db:
            genres_not_in_db.append(i)
    try:
        title = max(set(genres_not_in_db), key=genres_not_in_db.count).title()
    except: title = 'Playlist'

    x = list(db.execute('SELECT photo_link FROM listener_profiles WHERE username=?', (username,)).fetchall())
    for i in x:
        photo_links_currently_in_db.append(i[0])
    for i in photo_links:
        if i not in photo_links_currently_in_db:
            photo_links_not_in_db.append(i)
    if photo_links_not_in_db != []:
        photo_link = max(set(photo_links_not_in_db), key=photo_links_not_in_db.count)
    else: photo_link = max(set(photo_links), key=photo_links.count)

    return title, ', '.join(genres).title()[:46]+'...', photo_link

def locate_knee_of_clusters(sse_data, length):
    '''Cluster optimising algorithm, using the 'Elbow' technique (https://realpython.com/k-means-clustering-python/#choosing-the-appropriate-number-of-clusters)'''
    if length > 1 and len(sse_data) > 1:
        x = KneeLocator(range(1, length), sse_data, curve="convex", direction="decreasing").elbow
        if x != None: return x
        else: return 1
    else: return 1

def cluster_songs(audio_data, force_no_of_clusters=False):
    '''Clusters a dictionary of a songs according to unsupervised k-means learning. The dictionary is as so: audio_data[<spotify_uri>]= [<audio_features>].
    It returns a list of the clusters (each cluster being itself a sub-list). The number of clusters is optimised according to the elbow technique,
    hence the algorithm is run several times in a for loop, and they are then compared. The number of clusters can also be forced.'''
    sse = []
    audio_features = list(audio_data.values())
    length = len(audio_features) // 2 #so that clusters contain at least two items
    for k in range(1, length):
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(audio_features)
        sse.append(kmeans.inertia_)
    if not force_no_of_clusters: kmeans = KMeans(n_clusters=locate_knee_of_clusters(sse, length))
    if force_no_of_clusters: kmeans = KMeans(n_clusters=force_no_of_clusters)
    kmeans.fit(audio_features)
    predictions = kmeans.predict(audio_features)
    clustered_songs = {}
    for i in range(locate_knee_of_clusters(sse, length)):
        clustered_songs[i] = []
    for j, i in enumerate(predictions):
        clustered_songs[i].append(list(audio_data.keys())[j])
    return clustered_songs


def get_related_artists_for_playlist(uris):
    related_artists = []
    for i in uris:
        if i.split(':')[1] == 'track': related_artists.append(get_related_artists_for_track_in_db(i))
        elif i.split(':')[1] == 'artist': related_artists.append(get_related_artists(i))
        else: pass
    output = []
    for i in related_artists:
        for j in i:
            if j not in uris and j not in output:
                output.append(j)
    return output


