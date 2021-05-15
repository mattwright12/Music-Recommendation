import pandas as pd

class API_return_parser_track:
    '''Parses the return of an API call for a track, retrieving certain data from it'''

    def __init__(self, raw_body):
        '''Initiates the object, setting the local body attribute to what the API has returned'''
        if raw_body == None:
            raise('The body text inputted is empty. This is probably because the API call has failed.')
        self.body = raw_body

    def return_track_name(self, result_index=0):
        '''Returns the name of the track at index result_index'''
        return self.body['tracks']['items'][result_index]['name']

    def return_track_uri(self, result_index=0):
        '''Returns the uri of the track at index result_index'''
        return self.body['tracks']['items'][result_index]['uri']

    def return_first_artist_name(self, result_index=0):
        '''Returns the name of the first artist of a track at index result_index'''
        return self.body['tracks']['items'][result_index]['artists'][0]['name']

    def return_all_artists(self, result_index=0):
        '''Returns the all data about all the artists of a track at index result_index'''
        return self.body['tracks']['items'][result_index]['artists']

    def return_first_artist_uri(self, result_index=0):
        '''Returns the uri of the first artist of a track at index result_index'''
        return self.body['tracks']['items'][result_index]['artists'][0]['uri']

    def return_album_name(self, result_index=0):
        '''Returns the album name of the track at index result_index'''
        return self.body['tracks']['items'][result_index]['album']['name']

    def return_album_uri(self, result_index=0):
        '''Returns the uri of the album of the track at index result_index'''
        return self.body['tracks']['items'][result_index]['album']['uri']

    def return_release_date(self, result_index=0):
        '''Returns the release date of the track at index result_index'''
        return self.body['tracks']['items'][result_index]['album']['release_date']

    def return_preview_url(self, result_index=0):
        '''Returns the preview url of the track at index result_index'''
        return str(self.body['tracks']['items'][result_index]['preview_url'])

    def return_cover_art_url(self, result_index=0):
        '''Returns the url of the covert art of the album of the track at index result_index'''
        return self.body['tracks']['items'][result_index]['album']['images'][0]['url']

    def to_table(self):
        '''Converts the song data into a Pandas dataframe so that it might be displayed '''
        df = pd.DataFrame(columns = ['Track Name', 'Artist', 'Album', 'Preview URL', 'Cover Art URL', 'Track URI'])
        for i in range(len(self.body['tracks']['items'])):
            df.loc[i] = [self.return_track_name(result_index=i), self.return_first_artist_name(result_index=i), self.return_album_name(result_index=i), self.return_preview_url(result_index=i), self.return_cover_art_url(result_index=i), self.return_track_uri(result_index=i)]
        return df





class API_return_parser_artist:
    '''Parses the return of an API call for a track, retrieving certain data from it'''

    def __init__(self, raw_body):
        '''Initiates the object, setting the local body attribute to what the API has returned'''
        if raw_body == None:
            raise ('The body text inputted is empty. This is probably because the API call has failed.')
        self.body = raw_body

    def return_artist_name(self, result_index=0):
        '''Returns the name of the track at index result_index'''
        return self.body['artists']['items'][result_index]['name']

    def return_art_url(self, result_index=0):
        '''Returns the url of the covert art of the album of the track at index result_index'''
        try:
            return self.body['artists']['items'][result_index]['images'][0]['url']
        except:
            return None

    def return_followers_count(self, result_index=0):
        '''Returns the url of the covert art of the album of the track at index result_index'''
        return self.body['artists']['items'][result_index]['followers']['total']

    def return_artist_uri(self, result_index=0):
        '''Returns the unique Spotify URI of the artist'''
        return 'spotify:artist:' + self.body['artists']['items'][result_index]['id']

    def to_table(self):
        '''Converts the song data into a Pandas dataframe so that it might be displayed '''
        df = pd.DataFrame(columns = ['Artist', 'Followers', '', '', 'Cover Art URL', 'Artist URI'])
        for i in range(len(self.body['artists']['items'])):
            df.loc[i] = [self.return_artist_name(result_index=i), '', '', '', self.return_art_url(result_index=i), self.return_artist_uri(result_index=i)]
        return df


class audio_features:
    '''Class that organises the results of retrieve_audio_features_of_track() into a series of getters for
    each individual field'''

    def __init__(self, audio_features_json):
        '''Sets all of the parameters from the inputted json (audio_features_json)'''
        if audio_features_json:
            self.danceability = audio_features_json[0]['danceability']
            self.energy = audio_features_json[0]['energy']
            self.key = audio_features_json[0]['key']
            self.loudness = audio_features_json[0]['loudness']
            self.mode = audio_features_json[0]['mode']
            self.speechiness = audio_features_json[0]['speechiness']
            self.acousticness = audio_features_json[0]['acousticness']
            self.instrumentalness = audio_features_json[0]['instrumentalness']
            self.liveness = audio_features_json[0]['liveness']
            self.valence = audio_features_json[0]['valence']
            self.tempo = audio_features_json[0]['tempo']
            self.time_signature = audio_features_json[0]['time_signature']
            self.duration_ms = audio_features_json[0]['duration_ms']
        else:
            raise ConnectionError('Oops! Cannot connect to server, please try again later.')

    '''Below are a series of self-explanatory getters for all of the audio features'''
    def return_danceability(self): return self.danceability
    def return_energy(self): return self.energy
    def return_key(self): return self.key
    def return_loudness(self): return self.loudness
    def return_mode(self): return self.mode
    def return_speechiness(self): return self.speechiness
    def return_acousticness(self): return self.acousticness
    def return_instrumentalness(self): return self.instrumentalness
    def return_liveness(self): return self.liveness
    def return_valence(self): return self.valence
    def return_tempo(self): return self.tempo
    def return_duration_ms(self): return self.duration_ms
    def return_time_signature(self): return self.time_signature


