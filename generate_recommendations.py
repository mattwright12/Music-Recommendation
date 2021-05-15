

import sqlite3
import numpy as np
from recommend.api.api_call import *
from recommend.api.api_return_parser import *
from recommend.db import get_db
from recommend.fourier import fourier_from_track_uri, fourier_artists_top_songs_from_uri, convert_fourier_to_string
from recommend.fourier import convert_fourier_string_to_complex_numbers, normalise_complex_array
from shapely.geometry import Point


def generate_recommendations(listener_profile_id, username):
    '''Generates recommendations given the id of a listener profile. The function does not return as the recommendations are saved to a database'''
    add_artists_top_tracks_to_database(fetch_related_artists_for_listener_profile(listener_profile_id))
    find_closest_fouriers(listener_profile_id, username)

def fetch_related_artists_for_listener_profile(profile_id):
    '''Fetches the 'related_artists' field for a given listener profile id'''
    c = get_db()
    return c.execute('SELECT related_artists FROM listener_profiles WHERE id=?', (profile_id, )).fetchone()[0].split(';')


def add_track_to_db(track_uri, track_title):
    '''Adds a track to the songs table of the database alongside its Fourier result and Spotify Audio Features data'''
    db = get_db()
    if db.execute('SELECT uri FROM songs WHERE uri=?', (track_uri, )).fetchone() == None:
        track = audio_features(retrieve_audio_features_of_track(track_uri))
        metadata = search_track_by_uri(track_uri)
        db.execute(
            "INSERT INTO songs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (track_title, track_uri, track.return_danceability(),
             track.return_energy(), track.return_key(), track.return_loudness(), track.return_mode(),
             track.return_speechiness(), track.return_acousticness(), track.return_instrumentalness(),
             track.return_liveness(), track.return_valence(), track.return_tempo(), track.return_duration_ms(),
             track.return_time_signature(), metadata['album']['images'][0]['url'],
             metadata['album']['artists'][0]['external_urls']['spotify'], metadata['album']['artists'][0]['name'],
             metadata['preview_url'], convert_fourier_to_string(normalise_complex_array(fourier_from_track_uri(track_uri)))),
        )
        db.commit()


def add_artists_top_tracks_to_database(artist_list):
    '''Adds the top three tracks of an artist to the database, alongside Fourier data and Spotify Audio Features'''
    tracks = {}
    for artist in artist_list:
        try:
            top_tracks = retrieve_artists_top_tracks(artist, 5, True)
            for i in top_tracks:
                tracks[i[0]] = i[1]
        except IndexError:
            pass
    for i in list(tracks.keys()): add_track_to_db(i, tracks[i])



def abs_list(a):
    '''Returns the complex equivalents of all the values in a list.'''
    return [complex(i) for i in a]

def abs_difference(a, b):
    '''Returns the absolute difference between two lists. See more here: https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html '''
    a = np.array(abs_list(a))
    b = np.array(abs_list(b))
    return np.linalg.norm(a - b)

def _abs_difference(a, b):
    '''An alternative absolute difference function, it is currently unused'''
    total = 0
    for i in range(len(a)):
        total += Point(a[i].real, a[i].imag).distance(Point(b[i].real, b[i].imag))
    return total


def find_closest_fouriers(playlist_id, username, threshold=0.3, force_no_recommendations=10):
    '''Finds the closest songs in terms of Fouriers to the average Fourier of a list'''
    #threshold is proportion of mean it needs to be under to be deemed close enough
    db = get_db()
    differences = {}
    uri_to_track_name = {}
    title = db.execute('SELECT title, listener_data FROM listener_profiles WHERE id=?', (playlist_id, )).fetchone()[0]
    x = db.execute('SELECT listener_data FROM listener_profiles WHERE username=?', (username, )).fetchall()
    tracks = []
    for i in x:
        for j in i[0].split(';'):
            tracks.append(j)
    print('TRACKS', tracks)
    playlist_fourier = convert_fourier_string_to_complex_numbers(db.execute('SELECT fourier FROM listener_profiles WHERE id=?', (playlist_id, )).fetchone()[0])
    songs = db.execute('SELECT title, uri, fourier FROM songs').fetchall()
    for song in songs:
        fourier = convert_fourier_string_to_complex_numbers(song[2])
        if fourier != None and song[1] not in tracks:
            differences[song[1]] = abs_difference(playlist_fourier, fourier)
            uri_to_track_name[song[1]] = song[0]
    list_mean = sum(list(differences.values()))/len(list(differences.values()))
    threshold *= list_mean
    titles = []
    uris = []
    if force_no_recommendations:
        threshold = sorted(differences.values())[force_no_recommendations]
    for i in list(differences.keys()):
        if differences[i] <= threshold:
            titles.append(uri_to_track_name[i])
            uris.append(i)
    db.execute('INSERT INTO recommendations(title, username, titles, uris) VALUES (?, ?, ?, ?)', (title, username, ';'.join(titles), ';'.join(uris)))
    db.commit()

        
