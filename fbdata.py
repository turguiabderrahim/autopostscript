import os
import re
import sqlite3
import argparse
import itertools

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from facebook_scraper import get_posts

# sqlite setup
conn = sqlite3.connect('posts.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Create table
c.execute("CREATE TABLE IF NOT EXISTS posts (post_text text, price real, number_of_rooms INTEGER, image_url text, post_id text PRIMARY KEY)")

class FacebookPost(object):
    def __init__(self, post_text: str, price: int, image_url: str, post_id: str, number_of_rooms: int):
      self.post_text = post_text
      self.price = price
      self.image_url = image_url
      self.post_id = post_id
      self.number_of_rooms = number_of_rooms

def save_post(post: FacebookPost):
  c.execute("REPLACE INTO posts VALUES (?,?,?,?,?)", (
    post.post_text,
    post.price,
    post.number_of_rooms,
    post.image_url,
    post.post_id
  ))

def get_posts_from_db():
  posts = [FacebookPost(p[0], p[1], p[3], p[4], p[2]) for p in c.execute("SELECT * from posts")]
  return posts

# argument parser setup
parser = argparse.ArgumentParser(description='Scrape Facebook for posts.')
parser.add_argument('--scrape', action='store_true')
parser.add_argument('--display', action='store_true')
parser.add_argument('--plot', action='store_true')
parser.add_argument('--minimum_price', action='store', type=int, default=5000)
parser.add_argument('--maximum_price', action='store', type=int, default=6000)
parser.add_argument('--minimum_rooms', action='store', type=int, default=3)
parser.add_argument('--maximum_rooms', action='store', type=int, default=3)
args = parser.parse_args()

def pretty_print(post: FacebookPost):
  print("\n-----------Post----------\n")
  print(f"\n PRICE: {post.price}\n")
  if number_of_rooms(post):
    print(f"\n number_of_rooms: {number_of_rooms(post)}\n")
  print(post.post_text)

def price(post: FacebookPost):
  searchResults = re.search('[^0-9]([0-9],{0,1}[0-9]{3})[^0-9]', post.post_text)
  if searchResults:
    return searchResults.group(1).replace(',', '')
  return None

def append_price(post: FacebookPost):
  hasPrice = price(post)
  if hasPrice:
    post.price = hasPrice

def within_price_budget(post: FacebookPost):
  if post.price:
    return int(post.price) >= flags['minimum_price'] and int(post.price) <= flags['maximum_price']

def right_size(post: FacebookPost):
  if post.number_of_rooms:
    return int(post.number_of_rooms) >= flags['minimum_rooms'] and int(post.number_of_rooms) <= flags['maximum_rooms']

def has_text(post: FacebookPost):
  return len(post.post_text) > 1

def number_of_rooms(post: FacebookPost):
  match = re.search('([0-9]) חדרים', post.post_text)
  if match:
    return match.group(1)
  return None

def append_rooms(post: FacebookPost):
  hasRooms = number_of_rooms(post)
  if hasRooms:
    post.number_of_rooms = hasRooms


def print_if_passes_filters(post: FacebookPost):
  if passes_filters(post):
    pretty_print(post)

def display():
  for p in get_posts_from_db():
    append_details_from_text(p)
    print_if_passes_filters(p)

def append_details_from_text(post: FacebookPost):
  append_price(post)
  append_rooms(post)

def passes_filters(post: FacebookPost):
  return all((
    within_price_budget(post),
    right_size(post),
    has_text(post)
  ))

# parse args to flags
flags = vars(args)
if flags['display'] and not flags['scrape']:
  display()

pages = 10
credentials = None # (os.getenv('fb_username'), os.getenv('fb_password'))

allGroups = itertools.chain(
  get_posts(group=253957624766723, pages=pages, credentials=credentials), # דירות להשכרה ברמת גן
  get_posts(group=115046608513246, pages=pages, credentials=credentials), # דירות מפה לאוזן בגבעתיים
  get_posts(group=246902125410185, pages=pages, credentials=credentials), # דירות להשכרה ברמת גן / גבעתיים
)

if flags['plot']:
  sns.set(style="whitegrid")
  data = [(post.price, post.number_of_rooms) for post in get_posts_from_db() if (post.price and post.number_of_rooms)]
  df = pd.DataFrame(data, columns=["price", "rooms"])
  sns.jointplot(x="price", y="rooms", data=df, kind="kde");
  plt.show()

if flags['scrape']:
  for post in allGroups:
    currentFacebookPost = FacebookPost(post.get('text'), None, post.get('image'), post.get('post_id'), None)
    append_details_from_text(currentFacebookPost)
    save_post(currentFacebookPost)
    if flags['display']:
      print_if_passes_filters(currentFacebookPost)

# Save (commit) the changes
conn.commit()
c.close()