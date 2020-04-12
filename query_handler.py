import pymysql
from config.query_config import *

username = USERNAME
password = PASSWORD

class Query:
    def __init__(self, username=USERNAME, password=PASSWORD):
        """"Query class with two methods:
            insert into MySQL db
            get the most week """
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
        connection.commit()
        cur.close()

    @staticmethod
    def insert(chart, week):
        """"inserts chart data into db
         :param week: week of table
         :param chart: list of row dicts"""
        connection = pymysql.connect(user=username, password=password, database='billboard')
        cur = connection.cursor()
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
        connection.commit()
        cur.close()

    @staticmethod
    def get_most_recent_week():
        """"get the most recent week update from billboard.chart
        :return: string date"""
        connection = pymysql.connect(user=username, password=password, database='billboard')
        cur = connection.cursor()
        query = ('select max(date) from chart')
        cur.execute(query)
        most_recent = cur.fetchall()[0][0]
        return most_recent
