

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from recommend.db import get_db

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

def create_api_query(track=False, artist=False, album=False, year=False):
    '''Formats the API query based on the arguments'''
    q = ''
    if track: q += 'track:' + track
    elif artist: q += 'artist:' + artist
    elif album: q += 'album:' + album
    elif year: q += 'year:' + year
    return q


def create_api_call(track=None, year=None, artist=None, album=None, genre=None, type='track', limit=10, market=None, offset=0, error_catch=10, advanced_query=False):
    '''Creates a Spotify API call and returns the results'''
    i = 0
    results = False
    while True:
        try:
            if advanced_query:
                results = sp.search(advanced_query, limit=limit, offset=offset, type=type, market=market)
            else:
                results = sp.search(create_api_query(track=track, artist=artist, album=album, year=year), limit=limit, offset=offset, type=type, market=market)
            break
        except:
            i += 1
            time.sleep(0.5)
            print('Trouble connecting. Trying again')
            if i>5:
                break
    if results: return results
    raise ConnectionError('Oops! Cannot connect to server, please try again later.')


def search_artist_by_uri(uri, return_just_name=False):
    '''Creates a Spotify API for an artist's URI'''
    i = 0
    results = False
    while True:
        try:
            results = sp.artist(uri)
            break
        except:
            i += 1
            time.sleep(0.5)
            print('Trouble connecting. Trying again')
            if i>5:
                break
    if results:
        if return_just_name:
            return results['name']
        return results
    raise ConnectionError('Oops! Cannot connect to server, please try again later.')

def search_track_by_uri(uri):
    '''Creates a Spotify API for an artist's URI'''
    i = 0
    results = False
    while True:
        try:
            results = sp.track(uri)
            break
        except:
            i += 1
            time.sleep(0.5)
            print('Trouble connecting. Trying again')
            if i>5:
                break
    if results:
        return results
    raise ConnectionError('Oops! Cannot connect to server, please try again later.')


def retrieve_audio_features_of_track(track_uri):
    '''Returns the Audio Features data of a track, given its URI, from the Spotify API

    For more detail, see here: https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/'''
    return sp.audio_features(tracks=track_uri)
    i = 0
    results = False
    while True:
        try:
            return sp.audio_features(tracks=track_uri)
        except:
            i += 1
            time.sleep(0.5)
            print('Trouble connecting. Trying again')
            if i>5:
                raise ConnectionError('Oops! Cannot connect to server, please try again later.')
            return

def retrieve_artists_top_tracks(artist_uri, n=3, include_titles=False):
    '''Returns the track uris of the artist's three top tracks'''
    if not include_titles:
        r = sp.artist_top_tracks(artist_uri)
        try:
            return [x['uri'] for x in r['tracks'][:n]]
        except IndexError:
            raise IndexError('That artist does not have that many top tracks')
    else:
        r = sp.artist_top_tracks(artist_uri)
        try:
            return [(x['uri'], x['name']) for x in r['tracks'][:n]]
        except IndexError:
            raise IndexError('That artist does not have that many top tracks')


def retrieve_audio_features_of_an_artist(artist_uri):
    '''Returns the mean of the artist's three top tracks'''
    top_tracks = retrieve_artists_top_tracks(artist_uri)
    audio_features = []
    audio_feature_averages = {}
    for i in top_tracks: audio_features.append(retrieve_audio_features_of_track(i))
    for i in list(audio_features[0][0].keys()):
        try:
            audio_feature_averages[i] = (audio_features[0][0][i] + audio_features[1][0][i] + audio_features[2][0][i])*(1/3)
        except:
            pass
    return list(audio_feature_averages.values())


def get_related_artists(artist_uri):
    r = sp.artist_related_artists(artist_uri)
    return [i['uri'] for i in r['artists']]

def get_related_artists_for_track_in_db(track_uri):
    db = get_db()
    artist_uri = 'spotify:artist:' + db.execute('SELECT artist FROM songs WHERE uri=?', (track_uri, )).fetchone()[0].split('/')[-1]
    return get_related_artists(artist_uri)
