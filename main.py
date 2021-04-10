# Required libraries 
import os
import time
from time import sleep
import random
import pickle
import requests
import sys


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDialog, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.uic import loadUi    
from PyQt5.QtCore import pyqtRemoveInputHook
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


#define user agents
PC_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63'
MOBILE_USER_AGENT = 'Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0. 3945.79 Mobile Safari/537.36'



# Define function to check if config.pickle is empty or not
def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

# Define delay function
def delay ():
    time.sleep(random.randint(2,3))

# Define waitfor Function
def waitUntilVisible(browser: WebDriver, by_: By, selector: str, time_to_wait: int = 10):
    WebDriverWait(browser, time_to_wait).until(ec.visibility_of_element_located((by_, selector)))

# Define browser setup function
def browserSetup(user_agent: str = PC_USER_AGENT) -> WebDriver:
    #create Chrome browser with added arguements
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument("user-agent=" + user_agent)
    options.add_argument('log-level=3')
    options.add_argument("start-maximized")
    # ChromeDriverManager().install() is a workaround if you don't want to explain what the Chrome driver is 
    # ChromeDriverManager will automatically download the drivers Selenium requires
    chrome_browser_obj = webdriver.Chrome(ChromeDriverManager().install(), options = options)
    return chrome_browser_obj
	
# Define display credentials
def displayCredentials():
	global email
	# Open config.pickle to unpickle email and password and send to login function
	with open('config.pickle','rb') as account_dict:
		accountinfo = pickle.load(account_dict)
	
	email = accountinfo[1]		
	password = accountinfo[2]


	print('[LOGIN] Email: '+str.upper(email))
	delay()
	# Set up browser and call login function
	browser = browserSetup()
	login(browser, email, password)


# Define login function
def login(browser: WebDriver, email: str, pwd: str):
	   	browser.get('https://gamermine.com')
	   	# Wait for the page to complete loading
	   	waitUntilVisible(browser, By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/header/div/button', 10)
	   	delay()
	   	try:
	   		loginBtn = browser.find_element_by_css_selector('#main-content > div:nth-child(1) > header > div > button')
	   		loginBtn.click()
	   	except:
	   		pass
	   	# Type in email
	   	browser.find_element_by_css_selector('body > div:nth-child(7) > div > div > div.dialog.auth-dialog > div.body > div > div.auth-form > input[type=text]:nth-child(1)').send_keys(email)
	   	delay()
	   	# Type in password
	   	print('[LOGIN]', 'Writing password...')
	   	browser.find_element_by_css_selector('body > div:nth-child(7) > div > div > div.dialog.auth-dialog > div.body > div > div.auth-form > input[type=password]:nth-child(2)').send_keys(pwd)
	   	# Click login button
	   	browser.find_element_by_css_selector('body > div:nth-child(7) > div > div > div.dialog.auth-dialog > div.body > div > div.auth-form > button').click()
	   	delay()
	   	try:
	   		# Detect if there's an alert on sign-in, typically indicated by a red bar above the login screen
	   		# Send user back to inputCredentials if unable to login
	   		waitUntilVisible(browser, By.CSS_SELECTOR, '#main-content > div.Toastify > div > div > div.Toastify__toast-body', 10)
	   		print('[LOGIN] Unable to login...')
	   		delay()
	   		browser.quit()
	   		inputCredentials()
	   	
	   	except:
	   		# If red bar not detected, log-in successful
	   		print('[LOGIN] Logged-in successfully.')
	   		checkGamermineLogin(browser) 
	   		

# Def function to get account variables
def checkGamermineLogin(browser: WebDriver):
    # Access Gamermine
    browser.get('https://gamermine.com')
    delay()
    # Accept Cookies
    try:
        browser.find_element_by_id('bnp_btn_accept').click()
    except:
        pass
    delay()
    # Refresh page
    browser.get('https://gamermine.com')
    delay()
    # Update account name
    ACCOUNT_NAME = str(browser.find_element_by_css_selector('#main-content > div:nth-child(2)\
    	> header > div.user > div.user-dropdown-wrapper > div > a > div > span').get_attribute('innerHTML'))
    # Update counter
    POINTS_COUNTER = str(browser.find_element_by_class_name('balance-counter').get_attribute('innerHTML'))
   # Update Gamermine inventory notifications
    INVENTORY = str(browser.find_element_by_css_selector('#main-content > div.bottom-tray.open > div.button-container > button.inventory-button.widget-button.action-trigger > div').get_attribute('innerHTML'))
    # Update daily counter
    DAILY_COUNTER = str(browser.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[7]\
    	/div[1]/button[1]/div/span').get_attribute('innerHTML'))
    # Display variables
    try: 
    	print('[ACCOUNT] You are currently logged into Gamermine as: ' + str(ACCOUNT_NAME) +'.' )
    	print('[GOLD] You have ' + str(POINTS_COUNTER) + ' gold on your account!')    	
    	print('[INVENTORY] You have ' + str(INVENTORY) + ' new items in your inventory!')
    except:
    	pass
    # After displaying account variables, check if daily bonus is ready
    dailyChestReadyorNot(browser, DAILY_COUNTER)

# Define function to check daily chest 
def dailyChestReadyorNot(browser: WebDriver, DAILY_COUNTER: str):
	# Check value of daily counter
	if DAILY_COUNTER == "READY!":
			print('[DAILY BONUS] Attempting to claim the daily bonus...')
			getDailyBonus(browser)
	else: 
		pass
	delay()
	# After getting daily bonus, check Steam reward
	openSteamReward(browser)
		
# Define function to get daily bonus if counter is ready
def getDailyBonus(browser: WebDriver):
	# Icon on bottom right of the screen 
	chest = browser.find_element_by_css_selector('#main-content > div.bottom-tray.open > div.button-container \
		> button.daily-bonus-button.action-trigger.widget-button.ready > div > span')
	chest.click()
	delay()
	dailyFree = (browser.find_element_by_css_selector('body > div:nth-child(11) \
		> div > div > div > div.body > div > div:nth-child(2) > div > h3 > div > span').get_attribute('innerHTML'))
	# Click claim
	claimButton = browser.find_element_by_css_selector('body > div:nth-child(11) > div > div > div > div.body > button')
	claimButton.click()
	print('[DAILY BONUS] Successfully claimed ' + str(dailyFree) + ' gold!')
	delay()
	openSteamReward(browser)

# Define function to open the Steam reward webpage
def openSteamReward (browser: WebDriver):
	browser.get('https://gamermine.com/earn/rewards/steam')
	steamRewardReadyorNot(browser)

# Define function to check if Steam reward is available to claim
def steamRewardReadyorNot(browser: WebDriver):
	time.sleep(5)
	STEAM_REWARD = str(browser.find_element_by_css_selector('#main-content > div:nth-child(3) > div > div.middle > div > div > div.col-md-10.reward-content > div > div.hero.small.with-button > button').get_attribute('innerText'))
	if 'CLAIM' in STEAM_REWARD:
		delay()
		print('[STEAM REWARD] Attempting to claim Steam reward...')
		getSteamReward(browser)
	elif 'REQUIREMENT' in STEAM_REWARD:
		print('[STEAM REWARD] Requirements not met for daily reward.')
		browser.close()
		print('POWERED BY PASSIVEBOT.COM')
		quit()
	else:
		print('[STEAM REWARD] Check back in ' + str(STEAM_REWARD))
		browser.close()
		print('POWERED BY PASSIVEBOT.COM')
		quit()

def getSteamReward(browser: WebDriver):
	steamAmount = (browser.find_element_by_css_selector('#main-content > div:nth-child(3) > div > div.middle > div > div > div.col-md-10.reward-content > div > div.hero.small.with-button > button > div > b > div > span').get_attribute('innerHTML'))
	claimButton = browser.find_element_by_css_selector('#main-content > div:nth-child(3) > div > div.middle > div > div > div.col-md-10.reward-content > div > div.hero.small.with-button > button')
	claimButton.click()
	delay()
	print('[STEAM REWARD] Successfully claimed ' + str(steamAmount) + ' gold!')
	delay()
	browser.close()
	print('POWERED BY PASSIVEBOT.COM')
	quit()
	
# Define login dialog box
class Login(QDialog):
    def __init__(self):
        super(Login,self).__init__()
        loadUi("input.ui",self)
        # String value
        title = "Gamermine Bot"
        self.setWindowTitle(title)
        label = QLabel(self)
        pixmap = QPixmap('logo.png')
        label.setPixmap(pixmap)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.inputButton.clicked.connect(self.inputCredentials)

    # Define function to input email and password onto config.pickle using pickle lib
    def inputCredentials(self):
    	email=self.email.text()
    	password=self.password.text()
    	delay()

    	configuration = {1: email, 2: password}
    	with open('config.pickle','wb') as account_dict:
    		pickle.dump(configuration, account_dict)

    	displayCredentials()


# Define start dialog box
class Start(QDialog):
    def __init__(self):
        super(Start,self).__init__()
        loadUi("start.ui",self)
        label = QLabel(self)
        pixmap = QPixmap('logo.png')
        label.setPixmap(pixmap)
        self.startButton.clicked.connect(displayCredentials)


# Bot starts here        
ticker = is_non_zero_file('config.pickle')
pyqtRemoveInputHook()
if ticker ==1:
		app=QApplication(sys.argv)
		mainwindow=Start()
		mainwindow.setStyleSheet("background-color: white;")
		widget=QtWidgets.QStackedWidget()
		widget.addWidget(mainwindow)
		widget.setWindowTitle("Gamermine bot")
		widget.setFixedWidth(326)
		widget.setFixedHeight(200)
		widget.show()
else:
		app=QApplication(sys.argv)
		mainwindow=Login()
		mainwindow.setStyleSheet("background-color: white;")
		widget=QtWidgets.QStackedWidget()
		widget.addWidget(mainwindow)
		widget.setWindowTitle("Gamermine bot")
		widget.setFixedWidth(326)
		widget.setFixedHeight(235)
		widget.show()
	

app.exec_()
app.quit()
os._exit(1)

