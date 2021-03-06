import anvil.email
import anvil.secrets
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import requests
import json
from datetime import datetime
import anvil.tz

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
REJECTED_LIST_ID = "624895bb28c79a7f7f912e45"
TALENTED_LIST_ID = "624c89dc76356a7007071aef"

@anvil.server.callable
def create_card(name, email, phone, education, cover_letter, resume):
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
    'desc': f''' Email: {email} \nPhone: {phone} \nEducation level: {education} \nCover letter: {cover_letter}'''
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

@anvil.server.http_endpoint('/ats/reject_card/list',methods=["POST","HEAD"])
def reject_applicant():
  # Trello sends two requests, first HEAD and then POST. Checking for head request stops 505 on first request.
  if anvil.server.request.method == "HEAD":
    print("HEAD request from Trello API")
    return {}
  
  # get the old list ID or return a falsy object if an old list ID isn't found.
  previous_list_id = anvil.server.request.body_json.get('action', {}).get('data', {}).get('old', {}).get('idList')
  # check if card is being moved onto rejected list
  if previous_list_id and previous_list_id != REJECTED_LIST_ID:
    card_id = anvil.server.request.body_json['action']['data']['card']['id']
    email_from_card = get_email_address_from_card(card_id)
    anvil.email.send(from_name="Coolest Company Ever",
                     to=email_from_card,
                     subject="Application for Chief of Cool at the Coolest Company Ever",
                     text="Sorry to say you aren't cool enough!")

@anvil.server.http_endpoint('/ats/talented_applicant_card/list', methods=["POST", "HEAD"])
def talented_applicant():
  if anvil.server.request.method == "HEAD":
    return {}
  
  previous_list_id = anvil.server.request.body_json.get('action', {}).get('data', {}).get('old', {}).get('idList')
  if previous_list_id and previous_list_id != TALENTED_LIST_ID:
    card_id = anvil.server.request.body_json['action']['data']['card']['id']
    email_from_card = get_email_address_from_card(card_id)
    anvil.email.send(from_name="Coolest Company Ever",
                     to=email_from_card,
                     subject="Application for Chief of Cool at the Coolest Company Ever",
                     text="Hi There!\n\nYour information has been saved for future positions!\nWe wish you all the best!")
    
def get_email_address_from_card(card_id):
  url = f"https://api.trello.com/1/cards/{card_id}"
  
  headers = {
    "Accept": "application/json"
  }
  
  query = {
    'key': KEY,
    'token': TOKEN
  }
  
  response = requests.request(
    "GET",
    url,
    headers=headers,
    params=query
  )
  
  print(f"Get card details from Trello API status: {response}")
  # email extract instead custom field from trello
  response_list = response.json()["desc"][8:].split()
  email = response_list[0]
  return email

@anvil.server.callable
def insert_applications_to_db(name, email):
  app_tables.applications.add_row(CreatedAt=datetime.now(),Email=email, Name=name)