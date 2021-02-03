from datetime import datetime
import re
import regex

from bs4 import BeautifulSoup
import requests
import urllib
import urllib.request
from urllib.request import urlopen, Request

from selenium import webdriver

import numpy as np
import pandas as pd
import threading
import json
import getpass
import time
import os

from more_itertools import unique_everseen
from IPython.display import clear_output

from tqdm import tqdm_notebook

"""
class
"""


# noinspection PyMethodMayBeStatic
class InstaScrape:

    # constructor 
    def __init__(self, driver_loc='/Users/jslee/Downloads/chromedrive'):
        self.postLink = None
        self.postAccessibility = None
        self.postLocation = None
        self.postComment = None
        self.postUnverifiedTags = None
        self.postVerifiedTags = None
        self.postLikes = None
        self.postVerifiedUser = None
        self.postUser = None
        self.postDate = None

        self.driver_loc = driver_loc
        self._username = None
        self._password = None
        self.target_label = None
        self._target = None
        self.activedriver = None
        self._links = None

        self.post_date_l = []
        self.post_user_l = []
        self.post_verif_l = []
        self.post_likes_l = []
        self.post_tags_v_l = []
        self.post_tags_u_l = []
        self.post_l = []
        self.post_location_l = []
        self.post_insta_classifier_l = []
        self.post_link_l = []

        self._df = None

        self._listStack = [
            self.post_date_l, self.post_user_l, self.post_verif_l, self.post_likes_l, self.post_tags_v_l,
            self.post_tags_u_l, self.post_l, self.post_location_l, self.post_insta_classifier_l, self.post_link_l]

        self._functionStack = [
            self.postDate,
            self.postUser,
            self.postVerifiedUser,
            self.postLikes,
            self.postVerifiedTags,
            self.postUnverifiedTags,
            self.postComment,
            self.postLocation,
            self.postAccessibility,
            self.postLink]

    # method to compile for multi-threading
    def threadCompile(self, t_count, iterate, fcn):
        tasks = []
        batches = [i.tolist() for i in np.array_split(iterate, t_count)]

        for i in range(len(batches)):
            tasks.append(threading.Thread(target=fcn, args=[batches[i]]))

        return tasks

    # method to execute multi-threads
    def threadExecute(self, tasks):
        for t in tasks:
            print('execute running...')
            t.start()

        for t in tasks:
            t.join()

        return

    # method to fetch the json rom insta to read
    def fetchJson(self, url):
        page = urlopen(url).read()
        data = BeautifulSoup(page, 'html.parse')
        body = data.find('body')
        script = body.find('script')
        raw = script.text.strip().replace('window._sharedData =', '').replace(';', '')

        return json.loads(raw)

    # helpers
    def userData(self):
        self._username = input('Enter Username:')
        self._password = getpass.getpass('Enter password:')

        return

    def openWebDrive(self):
        print('launching driver..')
        driver = webdriver.Chrome(self.driver_loc)

        return driver

    def closeWebDrive(self, driver):
        print('closing driver...')
        driver.close()

        return

    # method for logging in
    def instaLogin(self, driver, default_url='https://www.instagram.com/accounts/login/?source=auth_switcher'):
        driver.get(default_url)
        time.sleep(2)

        username_field = driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[2]/div/label/input')
        username_field.click()

        username_field.send_keys(self._username)

        try:
            password_field = driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input')
        except:
            password_field = driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[3]/div/label/input')

        password_field.click()
        password_field.send_keys(self._password)
        time.sleep(2)

        login_button = driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/article/div/div[1]/div/form/div[4]')
        login_button.click()
        time.sleep(2)

        floating_window = driver.find_element_by_class_name('piCib')
        button = floating_window.find_element_by_class_name('mt3GC')
        not_now = button.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[2]')
        not_now.click()

        return driver

    def setTarget(self):
        """
        method that sets either a profile or a hashtag as target
        :return: base url to scrape depending on type
        """
        route = input('Choose scraping options - profile posts or hashtags? (p/h)')
        if route == 'h':
            hashtag = input('Type the hashtag label to scrape the post: ')
            self.target_label = '#' + hashtag
            tag_url = 'https://www.instagram.com/explore/tags/'
            self._target = tag_url + hashtag

            return self._target
        else:
            profile = input('Type the profile to scrape posts: ')
            self.target_label = '@' + profile
            profile_url = 'https:/www.instagram.com/'
            self._target = profile_url + profile

            return self._target

    def scrape(self, url):
        self.activedriver.get(url)

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        last_height = self.activedriver.execute_script(
            "return document.body.scrollHeight")

        links = []
        print("\n")
        target = input("Input how many links to scape (minimum): ")
        print("\n")
        print("Scraping..keep the browser open.")
        print("\n")

        while True:
            source = self.activedriver.page_source
            data = BeautifulSoup(source, 'html.parser')
            body = data.find('body')

            for link in body.findAll('a'):
                if re.match("/p", link.get('href')):
                    links.append('https://www.instagram.com' + link.get('href'))
                else:
                    continue

            self.activedriver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            new_height = self.activedriver.execute_script('return document.body.scrollHeight')

            if new_height == last_height:
                break

            last_height = new_height

            print("Scraped ", len(links), "links, ", len(set(links)), " are unique.")

            if len(set(links)) > int(target):
                break

        self._links = list(unique_everseen(links))
        clear_output()

        print("Finished scraping - Max ", len(links), " linked, ", len(self._links), " are unique.")
        print("\n")
        print("Closing driver...")

        self.closeWebDrive(self.activedriver)

        return

    # methods to get data from json
    def getPostDate(self, data):
        return datetime.utcfromtimestamp(
            data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['taken_at_timestamp'].strftime(
                '%Y-%m-%d %H:%M:%S'))

    def getPostUser(self, data):
        return data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']['username']

    def getPostVerifiedUser(self, data):
        return data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']['is_verified']

    def getPostLikes(self, data):
        return data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_preview_like']['count']

    def getTagEndPoint(self, data):
        return data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_to_tagged_user']['edges']

    def getPostVerifiedTags(self, data):
        tag_end_point = self.getTagEndPoint(data)
        entities = []
        verify = []

        for i in range(len(tag_end_point)):
            entities.append(tag_end_point[i]['node']['user']['full_name'])
            verify.append(tag_end_point[i]['node']['user']['is_verified'])

        df = pd.DataFrame({'Brand': entities, 'Verified:': verify})
        df = df[df.Verified == True]

        if len(list(df.Brand)) < 1:
            return np.nan
        else:
            return list(df.Brand)

    def getPostUnverifiedTags(self, data):
        tag_end_point = self.getTagEndPoint(data)
        tags = []
        verify = []

        for i in range(len(tag_end_point)):
            tags.append(tag_end_point[i]['node']['user']['full_name'])
            verify.append(tag_end_point[i]['node']['user']['is_verified'])

        df = pd.DataFrame({'Tag': tags, 'Verified': verify})
        df = df[df.Verified == False]

        if len(list(df.Tag)) < 1:
            return np.nan
        else:
            return ''.join(list(df.Tag))

    def getPostComment(self, data):
        pass

    def getPostLocataion(self, data):
        pass

    def getPostAccessibility(self, data):
        pass

    def getPostLink(self, data):
        pass

    """
    Main:
    """

    def login(self):
        # login
        self.userData()
        driver = self.openWebDrive()
        self.activedriver = self.instaLogin(driver)
        clear_output()
        print("Successfully logged in. Ready to scrape.")

    def getLinks(self):
        return self.scrape(self.setTarget())

    def getData(self):

        def extractData(links=self._links):
            for i in tqdm_notebook(range(len(links))):
                try:
                    data = self.fetchJson(links[i])
                    for f in self._functionStack:
                        if f != self._functionStack[-1]:
                            try:
                                self._listStack[self._functionStack.index(f)].append(f(data))
                            except:
                                self._listStack[self._functionStack.index(f)].apped(np.nan)
                except:
                    pass
            return

        print("multi-threading...")
        threads = int(input("How many threads: "))
        print('\n')
        print("executing...")
        self.threadExecute(self.threadCompile(threads, self._links, extractData))

        df = pd.DataFrame({'searched_for': [self.target_label] * len(self.post_l),
                           'post_link': self.post_link_l,
                           'post_date': self.post_date_l,
                           'post': self.post_l,
                           'user': self.post_user_l,
                           'user_verified_status': self.post_verif_l,
                           'post_likes': self.post_likes_l,
                           'post_verified_tags': self.post_tags_v_l,
                           'post_unverified_tags': self.post_tags_u_l,
                           'post_location': self.post_location_l,
                           'post_image': self.post_insta_classifier_l,
                           })

        df.sort_values(by='post_date', ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        self._df = df
        return df
