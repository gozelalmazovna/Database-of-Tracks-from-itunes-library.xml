'''Creating SQLite Database from .xml file in Python 3.
Database of Tracks from itunes library.xml
Output eaxmple in the Terminal:
--> Enter .xml file name: Library.xml
--> Dict count: 404
--> ('Another One Bites The Dust', 'Greatest Hits', 'Queen', 'Rock')'''

#import libs
import xml.etree.ElementTree as ET
import sqlite3

#Create Database
conn = sqlite3.connect("musiclib.sqlite")
cur = conn.cursor()

#Drop table if there exists and create new one
cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;

CREATE TABLE Artist(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
name TEXT UNIQUE);

CREATE TABLE Genre(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
name TEXT UNIQUE);

CREATE TABLE Album(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
title TEXT UNIQUE,
artist_id INTEGER);

CREATE TABLE Track(
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
title TEXT UNIQUE,
album_id INTEGER,
genre_id INTEGER,
len INTEGER,
rating INTEGER,
count INTEGER);
''')

#Function for searching in xml
def findit(dict,key):
    foundit = False
    for each in dict:
        if foundit:
            return each.text
        if each.tag == "key" and each.text == key:
            foundit = True
    return None

#Open the file and parse it
fname=input("Enter .xml file name: ")
fhand= ET.parse(fname)
stuff = fhand.findall('dict/dict/dict')
print("Dict count:",len(stuff))

#loop to go through each
for every in stuff:
    if findit(every,'Track ID') is None:
        continue

    track = findit(every,'Name')
    genre = findit(every,'Genre')
    artist = findit(every,'Artist')
    album = findit(every,'Album')
    count = findit(every,'Play Count')
    length = findit(every,'Total Time')
    rating = findit(every,'Rating')

    #Final check before updating database
    if track is None or artist is None or album is None:
        continue
    #Update Artist table and get relational number
    cur.execute('''INSERT OR IGNORE INTO Artist(name)
    VALUES(?)''',(artist,))
    cur.execute('''SELECT id FROM ARTIST
    WHERE name=?''',(artist,))
    artist_id = cur.fetchone()[0]

    #Update Genre table and get relational number
    cur.execute('''INSERT OR IGNORE INTO Genre(name)
    Values(?)''',(genre,))
    cur.execute('''SELECT id FROM Genre
    WHERE name=?''',(genre,))
    try:
        genre_id = cur.fetchone()[0]
    except:
        genre_id = None

    #Update Album table and get relational number
    cur.execute('''INSERT OR IGNORE INTO Album(title,artist_id)
    VALUES (?,?)''',(album,artist_id))
    cur.execute('''SELECT id FROM Album
    WHERE title = ?''',(album,))
    album_id = cur.fetchone()[0]

    #Update Track table
    cur.execute('''INSERT OR REPLACE INTO
    Track(title,album_id,genre_id,len,count,rating)
    VALUES(?,?,?,?,?,?)''',(track,album_id,genre_id,length,count,rating))

    conn.commit()

#Use JOIN to retrieve full data and print one row
cur.execute('''SELECT Track.title,Album.title,Artist.name,Genre.name
FROM Track JOIN Album JOIN Artist JOIN Genre
ON Album.artist_id = Artist.id
and Track.album_id = Album.id and Track.genre_id = Genre.id''')

print(cur.fetchone())
