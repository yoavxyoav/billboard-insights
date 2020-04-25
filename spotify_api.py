from __future__ import print_function  # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

CID = '44fe800219464e71a583778604f1a2df'
SECRET = '2d56de73e69941958a549f69f838c8dd'


class Spotify:
    """"Spotify web API data scraping"""

    def __init__(self, artist, song, song_id):
        """"initiating class using search string"""
        self.artist = artist
        self.song = song
        self.id = song_id
        client_credentials_manager = SpotifyClientCredentials(CID, SECRET)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def get_value_dict(self):
        """"get data from web API
        :param self: getting sp object and search str
        :return: 2 dictionaries of features for track """
        sp = self.sp
        search_str = self.artist + ' ' + self.song

        result = sp.search(search_str, type='track')
        try:
            value_dict = result['tracks']['items'][0]  # assuming the 1st one is the right one
        except IndexError:  # no results
            return None, None
        album_keys = ['release_date', 'name']
        track_keys = ['available_markets', 'duration_ms', 'explicit', 'popularity']
        excluded_audio_feat = ['type', 'id', 'uri', 'track_href', 'analysis_url', 'mode', 'time_signature',
                               'duration_ms', 'key']
        audio_analysis_keys = ['bars', 'beats', 'tatums', 'sections', 'segments']

        track_dict = {key: value_dict[key] for key in track_keys}
        track_dict['song_name'] = self.song
        track_dict['artist_name'] = self.artist
        track_dict['id'] = self.id
        for key in album_keys:
            track_dict['album_' + key] = value_dict['album'][key]
        audio_feature = sp.audio_features(value_dict['id'])[0]
        for key in audio_feature.keys():
            if key not in excluded_audio_feat:
                track_dict['audio_' + key] = audio_feature[key]

        audio_analysis = sp.audio_analysis(value_dict['id'])
        audio_analysis_dict = dict()
        for key in audio_analysis_keys:
            audio_analysis_dict[key] = audio_analysis[key]
            audio_analysis['feature'] = key
        return track_dict, audio_analysis_dict


x = Spotify('the weekend', 'blinding lights', 'whatever')

a, b = x.get_value_dict()
print(a)
print(a.keys())
print(b)
print(b.keys())
