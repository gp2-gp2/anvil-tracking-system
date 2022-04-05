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
    self.label_version.text = f"App id: {app.id} | branch: {app.branch} | environment: {app.environment}"

  def submit_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    name = self.name_text_box.text
    email = self.email_text_box.text
    phone = self.phone_text_box.text
    education = self.education_drop_down.selected_value
    cover_letter = self.cover_letter_text_area.text
    resume = self.resume_file_uploader.file
    
    if self.validate_form(name, email, phone, education, cover_letter, resume):
      # call to the server function to create card in Trello by calling API
      anvil.server.call('create_card', name, email, phone, education, cover_letter, resume)
      anvil.server.call('insert_applications_to_db', name, email)
      self.reset_form()
      Notification("Your application has been submitted. Thanks for applying!",timeout=5, title="Hi, there!").show()
    else:
      alert("Please fulfill all form fields and attach file with resume before trying to submit.")   
    
  def reset_form(self):
    self.name_text_box.text = ""
    self.email_text_box.text = ""
    self.phone_text_box.text = ""
    self.education_drop_down.selected_value =  None
    self.cover_letter_text_area.text = ""
    self.resume_file_uploader.clear()

  def validate_form(self, name, email, phone, education, cover_letter, resume):
    # validate all fields length
    if not name or not email or not phone or not education or not cover_letter or not resume:
      return False
    return True