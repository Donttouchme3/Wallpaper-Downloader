import requests
import time
import os
import re
from bs4 import BeautifulSoup
import sqlite3
from dotenv import load_dotenv


class WallpaperParser:
    def __init__(self, Download=False):
        load_dotenv()
        self.URL = os.getenv('URL')
        self.HOST = os.getenv('HOST')
        self.HEADER = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.52'
        }
        self.Download = Download

    def CategoryParser(self):
        Data = requests.get(self.URL, headers=self.HEADER).text
        Soup = BeautifulSoup(Data, 'html.parser')
        Conainer = Soup.find('ul', class_='filters__list')
        Categories = Conainer.find_all('a', class_='filter__link')
        for Category in Categories:
            CategoryName = Category.get_text(strip=True)
            CategoryLink = self.HOST + Category.get('href')
            CategoryCorrectName = re.search(r'[3]*[A-Za-zА-Яа-я]+', CategoryName)[0]
            CategoryPages = re.search(r'[0-9][0-9]+', CategoryName)[0]

            CategoryId = self.SaveToDataBase(CategoryCorrectName)
            self.CategoryPageParser(CategoryId, CategoryLink, CategoryCorrectName)

    def GetData(self, CategoryLink, i):
        Html = requests.get(CategoryLink + f'/page{i}').text
        Soup = BeautifulSoup(Html, 'html.parser')
        return Soup

    def CategoryPageParser(self, CategoryId, CategoryLink, CategoryCorrectName, CategoryPages = 3):
        for i in range(1, CategoryPages+1):
            Soup = self.GetData(CategoryLink, i)
            try:
                ImageLinks = Soup.find_all('a', class_='wallpapers__link')
                for Link in ImageLinks:
                    ImageLink = self.HOST + Link.get('href')
                    ImageSrc = Link.find('img', class_='wallpapers__image').get('src')
                    # print(ImageLink)
                    Html = requests.get(ImageLink, headers=self.HEADER).text
                    Soup = BeautifulSoup(Html, 'html.parser')
                    ImageFormat = Soup.find_all('span', class_='wallpaper-table__cell')[1].get_text(strip=True)
                    ImageCorrectLink = ImageSrc.replace('300x168', ImageFormat)
                    self.SaveToDataBase_Images(ImageCorrectLink, CategoryId)

                    if self.Download:
                        if CategoryCorrectName not in os.listdir():
                            os.mkdir(str(CategoryCorrectName))
                        ResponseImage = requests.get(ImageCorrectLink, headers=self.HEADER).content
                        ImageName = ImageCorrectLink.replace('https://images.wallpaperscraft.ru/image/single/', '')
                        with open(f'{CategoryCorrectName}/{ImageName}', mode='wb') as file:
                            file.write(ResponseImage)

            except:
                pass

    def SaveToDataBase(self, CategoryName):
        DataBase = sqlite3.connect('WallpapersDataBase.db')
        Cursor = DataBase.cursor()
        Cursor.execute('''
        INSERT OR IGNORE INTO categories(categoryName) VALUES (?);
        ''', (CategoryName,))
        DataBase.commit()
        Cursor.execute('''
        SELECT categoryId FROM categories WHERE categoryName = ?
        ''', (CategoryName, ))
        CategoryId = Cursor.fetchone()[0]

        return CategoryId
        DataBase.close()

    def SaveToDataBase_Images(self, Link, CategoryId):
        DataBase = sqlite3.connect('WallpapersDataBase.db')
        Cursor = DataBase.cursor()
        Cursor.execute('''
        INSERT OR IGNORE INTO images(imageLink, categoryId) VALUES (?, ?)
        ''', (Link, CategoryId))
        DataBase.commit()
        DataBase.close()




def StartParsing():
    Parser = WallpaperParser(Download=True)
    Parser.CategoryParser()

StartParsing()
