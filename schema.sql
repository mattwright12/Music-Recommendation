-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS listener_profiles;
DROP TABLE IF EXISTS listener_raw_data;
DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS recommendations;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE listener_raw_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  title TEXT NOT NULL,
  listener_data TEXT NOT NULL
);

CREATE TABLE listener_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  title TEXT NOT NULL,
  listener_data TEXT NOT NULL,
  content TEXT NOT NULL,
  photo_link TEXT NOT NULL,
  fourier TEXT,
  related_artists TEXT,
  playlist_created_for TEXT
);

CREATE TABLE "recommendations" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	"title"     TEXT NOT NULL,
	"username"	TEXT NOT NULL,
	"titles"	TEXT NOT NULL,
	"uris"	TEXT NOT NULL
);





CREATE TABLE songs (
  title TEXT NOT NULL,
  uri TEXT NOT NULL,
  danceability DOUBLE NOT NULL,
  energy DOUBLE NOT NULL,
  key DOUBLE NOT NULL,
  loudness DOUBLE NOT NULL,
  mode DOUBLE NOT NULL,
  speechiness DOUBLE NOT NULL,
  acousticness DOUBLE NOT NULL,
  instrumentalness DOUBLE NOT NULL,
  liveness DOUBLE NOT NULL,
  valence DOUBLE NOT NULL,
  tempo DOUBLE NOT NULL,
  duration_ms DOUBLE NOT NULL,
  time_signature DOUBLE NOT NULL,
  photo_link TEXT,
  artist TEXT NOT NULL,
  artist_name TEXT NOT NULL,
  preview_url TEXT,
  fourier TEXT
);

CREATE TABLE artists (
  artist TEXT NOT NULL,
  uri TEXT NOT NULL,
  danceability DOUBLE NOT NULL,
  energy DOUBLE NOT NULL,
  key DOUBLE NOT NULL,
  loudness DOUBLE NOT NULL,
  mode DOUBLE NOT NULL,
  speechiness DOUBLE NOT NULL,
  acousticness DOUBLE NOT NULL,
  instrumentalness DOUBLE NOT NULL,
  liveness DOUBLE NOT NULL,
  valence DOUBLE NOT NULL,
  tempo DOUBLE NOT NULL,
  duration_ms DOUBLE NOT NULL,
  time_signature DOUBLE NOT NULL,
  photo_link TEXT,
  genres TEXT NOT NULL,
  fourier TEXT
);


