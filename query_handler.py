import pymysql
import tqdm
from spotify_api import Spotify
import numpy as np

username = 'Yossi'
password = 'Ratedrko27'


class Query:
    def __init__(self):
        """"Query class for exporting data into mysql db"""
        self.start()  # creates DB and

    @staticmethod
    def start():
        """"creates billboard DB and relevant charts (if needed)"""
        connection = pymysql.connect(user=username, password=password)
        cur = connection.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS  billboard")
        connection.commit()
        cur.close()
        # creating tables
        connection = pymysql.connect(user=username, password=password, database='billboard')
        cur = connection.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS artist (id INT NOT NULL AUTO_INCREMENT, 
                                                            full_name CHAR(255),
                                                             PRIMARY KEY(id))''')

        cur.execute("""CREATE TABLE IF NOT EXISTS song (id INT NOT NULL AUTO_INCREMENT,
                                                            name CHAR(255),
                                                             artist_id INT,
                                                              entry_date DATE,
                                                               entry_position INT,
                                                                PRIMARY KEY (id))""")

        cur.execute('''CREATE TABLE IF NOT EXISTS chart(id INT NOT NULL AUTO_INCREMENT,
                                                        date DATE,
                                                        position INT,
                                                        song_id INT,
                                                        artist_id INT,
                                                        last_week INT,
                                                        total_weeks INT, PRIMARY KEY(id),
                                                        FOREIGN KEY (artist_id) REFERENCES artist(id),
                                                        FOREIGN KEY (song_id) REFERENCES song(id))''')

        cur.execute('''CREATE TABLE IF NOT EXISTS chart(id INT NOT NULL AUTO_INCREMENT,
                                                                date DATE,
                                                                position INT,
                                                                song_id INT,
                                                                artist_id INT,
                                                                last_week INT,
                                                                total_weeks INT, PRIMARY KEY(id),
                                                                FOREIGN KEY (artist_id) REFERENCES artist(id),
                                                                FOREIGN KEY (song_id) REFERENCES song(id))''')
        cur.execute('''CREATE TABLE IF NOT EXISTS song_detail(id INT NOT NULL ,
                                                                available_markets CHAR(255), 
                                                                duration_ms INT, 
                                                                explicit BOOL, 
                                                                popularity INT,
                                                                 song_name CHAR(255), 
                                                                 artist_name CHAR(255),
                                                                 album_release_date DATE,
                                                                  album_name CHAR(255), 
                                                                audio_danceability FLOAT,
                                                                 audio_energy FLOAT,
                                                                audio_loudness FLOAT,
                                                                 audio_speechiness FLOAT, 
                                                                audio_acousticness FLOAT,
                                                                audio_instrumentalness FLOAT,
                                                                audio_liveness FLOAT, 
                                                                audio_valence FLOAT, 
                                                                audio_tempo FLOAT, 
                                                                PRIMARY KEY(id) ,
                                                                FOREIGN KEY (song_pk) REFERENCES song(id)
                                                                )
                                                                ''')
        connection.commit()
        cur.close()

    @staticmethod
    def insert(charts, week):
        """"inserts chart data into db
         :param week: week of table
         :param charts: list of row dicts"""
        if type(charts[0]) is not list:
            charts = [charts]
        connection = pymysql.connect(user=username, password=password, database='billboard')
        cur = connection.cursor()
        for i, chart in enumerate(tqdm.tqdm(charts)):
            for p in chart:
                art = "INSERT IGNORE INTO `artist` (`full_name`) VALUES (%s)"
                cur.execute(art, (p['artist']))

                son = "INSERT IGNORE INTO `song` (`name`, `artist_id`, `entry_date`, `entry_position`) " \
                      "VALUES (%s, (SELECT id FROM artist WHERE full_name = %s), %s, %s)"
                cur.execute(son, (p['song'], p['artist'], week, p['rank']))

                chart1 = "INSERT IGNORE INTO `chart` " \
                         "( `date`, `position`, `song_id`, `artist_id`, `last_week`, `total_weeks`) " \
                         "VALUES (%s, %s, (SELECT id FROM song WHERE name = %s), " \
                         "(SELECT id FROM artist WHERE full_name = %s), %s, %s)"

                cur.execute(chart1, (week, p['rank'], p['song'], p['artist'], p['last_pos'], p['duration']))
            if i == 100:  # commit after 10K rows
                connection.commit()
        connection.commit()
        cur.close()

    @staticmethod
    def get_most_recent_week():
        """"get the most recent week update from billboard.chart
        :return: string date"""
        connection = pymysql.connect(user=username, password=password, database='billboard')
        cur = connection.cursor()
        query = 'select max(date) from chart'
        cur.execute(query)
        most_recent = cur.fetchall()[0][0]
        cur.close()
        return most_recent


def insert_spotify_track():
    """"insert new values into table song_detail
    """
    connection = pymysql.connect(user=username, password=password, database='billboard')
    cur = connection.cursor()
    query = "select s.name,a.full_name,c.song_id " \
            "from (select * from chart " \
            "where song_id not in (select id from song_detail )) as c " \
            "inner join song as s on c.song_id=s.id " \
            "inner join artist as a on a.id =c.artist_id ;"

    cur.execute(query)  # getting all new song's names artist name and song id
    search_string = cur.fetchall()
    count = 0
    for i, res in enumerate(tqdm.tqdm(search_string)):
        spotify = Spotify(*res)
        print('fetching from Spotify WEB API for %s by %s..' % res[:-1])
        track_dict, audio_analysis_dict = spotify.get_value_dict()
        if track_dict is None:
            print('Failed :/ u ')
        else:
            count += 1
            print('track data (with song id as primary key')
            print(track_dict)
            print('track music analysis')
            print(audio_analysis_dict)
    print("successfully retrieved {0} out of {1} ({2}%)".format(count, len(search_string),
                                                                np.around(count * 100 / len(search_string),
                                                                          decimals=2)))
    


x = Query()
insert_spotify_track()
