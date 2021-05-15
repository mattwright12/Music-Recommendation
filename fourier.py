import requests
import numpy as np
from recommend.db import *
import sqlite3
from pydub import AudioSegment
import io
from recommend.api.api_call import retrieve_artists_top_tracks, search_track_by_uri
import statistics



def fourier_from_preview_url(preview_url, n=100):
    '''Returns the fourier analysis of a track given its preview url. N is the number of frequencies analysed'''
    return np.fft.fft(AudioSegment.from_file(io.BytesIO(requests.get(preview_url + '.mp3').content), format="mp3").get_array_of_samples(), n=n)

def fourier_from_track_uri(uri):
    '''Returns the Fourier analysis for a track given its URI'''
    db = get_db()
    preview_url = db.execute('SELECT preview_url FROM songs WHERE uri=?', (uri, )).fetchone()
    try:#try if it is in database, where the preview url is already stored
        return fourier_from_preview_url(preview_url[0])
    except:#not in database, so search api
        preview_url = search_track_by_uri(uri)['preview_url']
        if preview_url == None:
            return None
        else:
            return fourier_from_preview_url(preview_url)

def fourier_artists_top_songs_from_uri(uri):
    '''Averages (arithmetically) the Fouriers of an artists top 3 tracks'''
    fouriers = []
    averaged_fouriers = []
    for i in retrieve_artists_top_tracks(uri):
        fourier = fourier_from_track_uri(i)
        if fourier is not None: fouriers.append(fourier)
    if fouriers != []:
        for i in range(len(fouriers[0])):

            average = 0
            for j in range(3):
                try: average += fouriers[j][i]
                except: pass
            average /= 3
            averaged_fouriers.append(average)
        return averaged_fouriers
    return None

def convert_fourier_to_string(fourier):
    '''Converts a list of numpy.complex128 fourier results into a string that can be stored in sqlite'''
    if fourier is not None: return ';'.join([str(i) for i in fourier])
    return ''

def convert_fourier_string_to_complex_numbers(fourier):
    '''Converts a 'Fourier string' (the way they are stored in the database, see below) back into a list of complex numbers, with can then be manipulated by the program'''
    fourier = fourier.split(';')
    if fourier == ['']: return None
    return [complex(x) for x in fourier]

def normalise_complex_array(a):
    '''Inputs an array of complex number and normalises them between -1 and 1 and i and -i'''
    try:
        if a == None: return []
    except:
        pass
    real = [x.real for x in a]
    real_mean = statistics.mean(real)
    real_range = max(real)-min(real)
    imaginary = [x.imag for x in a]
    imaginary_mean = statistics.mean(imaginary)
    imaginary_range = max(imaginary)-min(imaginary)
    real_data = [(x-real_mean)/real_range for x in real]
    imaginary_data = [(x-imaginary_mean)/imaginary_range for x in imaginary]
    output = []
    for i in range(len(real_data)):
        output.append(complex(real_data[i], imaginary_data[i]))
    return output




def generate_fourier_from_uri_list(list):
    '''Generte Fourier analyses for a list of uris'''
    fouriers = []
    db = get_db()
    for i in list:
        if i.split(':')[1] == 'track': fouriers.append(db.execute('SELECT fourier FROM songs WHERE uri=?', (i, )).fetchone()[0].replace('(', '').replace(')', '').split(';'))
        elif i.split(':')[1] == 'artist': fouriers.append(db.execute('SELECT fourier FROM artists WHERE uri=?', (i, )).fetchone()[0].replace('(', '').replace(')', '').split(';'))
        else: pass
    fouriers_filtered = [x for x in fouriers if x != ['']]#removes all None values
    averages = []
    if fouriers_filtered != []:
        for i in range(len(fouriers_filtered[0])):
            average = 0
            for j in range(len(fouriers_filtered)):
                average += complex(fouriers_filtered[j][i])
            average /= len(fouriers_filtered)
            averages.append(average)
    return averages