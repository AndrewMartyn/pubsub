import pyotp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import datetime
from bs4 import BeautifulSoup
from lxml import etree
import re

class Scraper:
  def __init__(self):
    # initialize driver
    self.__init_driver__()

    # initialize config
    self.__init_config__()


  # destructor
  # def __del__(self):
  #   self.driver.quit()
    

  def __init_driver__(self):
    try:
      chrome_options = Options()
      chrome_options.add_argument('--headless')
      chrome_options.add_argument('--no-sandbox')
      chrome_options.add_argument('--disable-dev-shm-usage')

      self.driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
      print(e)





  def login(self, username, password, google_authenticator_secret):
    try:
      self.driver.maximize_window()
      self.driver.get("https://publix.org")

      self.driver.find_element(By.XPATH, '/html/body/main/div[4]/div/div/form/button').click()
      # wait for email field and enter username
      WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'i0116'))).send_keys(self.__username)

      # wait for next button and click
      WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'idSIButton9'))).click()

      # wait for password field and enter password
      WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'i0118'))).send_keys(self.__password)

      # wait for sign in button and click
      WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'idSIButton9'))).click()

      # click verification code option
      WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="idDiv_SAOTCS_Proofs"]/div[1]/div'))).click()

      # enter otp
      totp = pyotp.TOTP(self.__otp_secret)
      WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'idTxtBx_SAOTCC_OTC'))).send_keys(totp.now())

      # click submit
      WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'idSubmit_SAOTCC_Continue'))).click()

      # wait till we are on the home page
      WebDriverWait(self.driver, 10).until(EC.title_is('Home'))
    except Exception as e:
      print(e)

  
  def nav_schedule_page(self):
    try:
      WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/main/div[5]/div/div[1]/div/div/h4/a'))).click()
      # get current week date
      dom = etree.HTML(str(BeautifulSoup(self.driver.page_source, features='lxml')))
      self.current_week = dom.xpath('//*[@id="scheduledweek"]/div[1]/div[2]/div[1]/text()')[1]
      self.current_week = re.search(': (.*)\n', self.current_week).group(1)
      self.current_week = self.__convert_date(date=self.current_week, offset=0)
      self.driver.get(f"https://www.publix.org/api/sitecore/Scheduling/GetPreviousorNextWeekSchedule?weekstartDate={self.current_week}")
      print(f"Schedule Week of: {self.current_week}")

    except Exception as e:
      print(e)


  def __convert_date(_, date, offset=0):
    try:
      as_datetime = datetime.datetime.strptime(date, "%m/%d/%Y")
      next_week = (as_datetime + datetime.timedelta(days=offset)).strftime("%m/%d/%Y")
      return next_week
    except Exception as e:
      print(e)
    
  
  def nav_schedule_next(self):
    # go to next schedule page
    try:
      self.current_week = self.__convert_date(date=self.current_week, offset=7)
      self.driver.get(f"https://www.publix.org/api/sitecore/Scheduling/GetPreviousorNextWeekSchedule?weekstartDate={self.current_week}")
      print(f"Schedule Week of: {self.current_week}")
    except Exception as e:
      print(e)
      

  def get_schedule(self):
    schedule = list()
    
    try:
      html = self.driver.page_source

      soup = BeautifulSoup(html, features="lxml")

      if len(soup.find_all('span', string='Schedule information is currently unavailable. Please try again later.')) > 0:
        raise Exception('Schedule information is currently unavailable. Please Try again later.') 

      # self.current_week = soup.find('div', {'class': 'week-header'}).text.strip().split(':')[1]


      week_html = soup.find_all('a', {'data-target': True})
      for day_html in week_html:
        is_working = True if day_html.find('div', {'class': 'dataOfWeek'}).text.strip() != 'Not Scheduled' else False
        if not is_working:
          continue

        day_details_html = soup.find('div', {'id': day_html.get('data-target')[1:]})

        day_details = day_details_html.find_all('div', {'class': 'col-xs-6'})
      
        date = day_html.find('div', {'class': 'dayOfWeek'}).find_all('div')[1].text.strip()

        # in the case that we're at the end of the year 
        # this is really ugly but works by checking to see if the week enters into the new year
        # TODO: make more elegant
        # if int(date.split('/')[0]) == 12 and int(date.split('/')[1]) < int(self.current_week.split('/')[1]):
        #   date = date + "/" + str(int(self.current_week.split('/')[2])+1)
        # else:
        #   date = date + "/" + self.current_week.split('/')[2]
        date = date + "/" + self.current_week.split('/')[2]

        

        store = day_details_html.find('div', {'class': 'store-number'}).find('u').text.strip()
        role = day_details[0].text.strip()
        shift_time = day_details[1].text.strip()
        meal_time = day_details[3].text.strip()
        net_hours = day_details[5].text.strip()

        day = [date, store, role, shift_time, meal_time, net_hours]
        schedule.append(day)
    except Exception as e:
      print(e)
    
    return schedule
  