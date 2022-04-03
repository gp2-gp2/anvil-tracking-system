import anvil.secrets
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import json

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

KEY = anvil.secrets.get_secret('trello_api_key')
TOKEN = anvil.secrets.get_secret('trello_api_token')

NEW_APPLICATIONS_LIST_ID = "624895a3d8c5a2596c8f6e5c"

@anvil.server.callable
def create_card(name, email, phone, cover_letter, resume):
  url = "https://api.trello.com/1/cards"
  query = {
    # api credentials
    'key': KEY,
    'token': TOKEN,
    # list to create our card on
    'idList': NEW_APPLICATIONS_LIST_ID,
    # set the card name to be the applicant's name
    'name': name,
    # position the new card at the bottom of the list
    'pos': 'bottom',
    # add the description to the card containing the email, phone, and cover letter
    'desc': f''' Email: {email} Phone: {phone} Cover letter: {cover_letter}'''
  }
  response = requests.request(
    'POST', 
    url, 
    params=query
  )
  # get the card ID and pass it to our new create attachment function
  new_card_id = response.json().get('id')
  create_card_attachment(new_card_id, resume)
  
def create_card_attachment(card_id, attachment):
  url = f'https://api.trello.com/1/cards/{card_id}/attachments'
  files = {'file': (attachment.get_name(), attachment.get_bytes(), 'application/json')}
  query = {
    'key': KEY,
    'token': TOKEN,
    'name': attachment.get_name()
  }
  response = requests.request(
    'POST',
    url,
    files=files,
    params=query
  )