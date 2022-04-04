from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Form1(Form1Template):

  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    name = self.name_text_box.text
    email = self.email_text_box.text
    phone = self.phone_text_box.text
    cover_letter = self.cover_letter_text_area.text
    resume = self.resume_file_uploader.file
    
    # call to the server function to create card in Trello by calling API
    anvil.server.call('create_card', name, email, phone, cover_letter, resume)
    
    self.reset_form()
    Notification("Your application has been submitted. Thanks for applying!",timeout=5, title="Hi, there!").show()
    
  def reset_form(self):
    self.name_text_box.text = ""
    self.email_text_box.text = ""
    self.phone_text_box.text = ""
    self.cover_letter_text_area.text = ""
    self.resume_file_uploader.clear()

  def validate_form(self):
    pass