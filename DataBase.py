import sqlite3

DataBase = sqlite3.connect('WallpapersDataBase.db')
Cursor = DataBase.cursor()
Cursor.executescript('''
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS images;

CREATE TABLE IF NOT EXISTS categories(
    categoryId INTEGER PRIMARY KEY AUTOINCREMENT,
    categoryName TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS images(
    imageId INTEGER PRIMARY KEY AUTOINCREMENT,
    imageLink UNIQUE,
    categoryId INTEGER REFERENCES categories(CategoryId)
);
''')
DataBase.commit()
DataBase.close()