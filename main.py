from scraper import Scraper
from schedule import Schedule
from configparser import ConfigParser

# Config/Globals
USERNAME = ""
PASSWORD = ""
GOOGLE_AUTHENTICATOR_SECRET = ""
FILE_NAME = ""

def main():

  __init_config__()

  # Initialize Scraper
  scraper = Scraper()

  # Initialize Schedule
  schedule = Schedule()

  print("Logging into Publix.org...")
  scraper.login(username=USERNAME, password=PASSWORD, google_authenticator_secret=GOOGLE_AUTHENTICATOR_SECRET)
  print("Login Successful!\n")

  # scrape, parse, and add week 1
  scraper.nav_schedule_page()
  week1 = scraper.get_schedule()
  print(f"Gathered Schedule: {week1}")
  schedule.addShifts(week1)
  print("Added Schedule to Calendar!\n")
  
  # scrape, parse, and add week 2
  scraper.nav_schedule_next()
  week2 = scraper.get_schedule()
  print(f"Gathered Schedule: {week2}")
  schedule.addShifts(week2)
  print("Added Schedule to Calendar!\n")
  
  # scrape, parse, and add week 3
  scraper.nav_schedule_next()
  week3 = scraper.get_schedule()
  print(f"Gathered Schedule: {week3}")
  schedule.addShifts(week3)
  print("Added Schedule to Calendar!\n")

  
  scraper.driver.quit()
  print("Webdriver safely quit\n")

  print(f"Calendar exported to: {FILE_NAME}")
  schedule.export(FILE_NAME)
  

def __init_config__(self): 
  try:
    config = ConfigParser()
    config.read('settings.ini')
    USERNAME = config['LOGIN']['username']
    PASSWORD = config['LOGIN']['password']
    GOOGLE_AUTHENTICATOR_SECRET = config['LOGIN']['google_authenticator_secret']
    FILE_NAME = config['LOGIN']['file_name']


  except Exception as e:
    print("Configuration file is missing or invalid.\nGo to https://github.com/pubsub for more information.")

if __name__ == "__main__":
  main()