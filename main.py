#required libraries 
import os
import time
from time import sleep
import random
import pickle
import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

#define user agents
PC_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63'
MOBILE_USER_AGENT = 'Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0. 3945.79 Mobile Safari/537.36'

#define function to check if config.txt is empty or not
def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

#define delay function
def delay ():
    time.sleep(random.randint(2,3))

#define waitfor Function
def waitUntilVisible(browser: WebDriver, by_: By, selector: str, time_to_wait: int = 10):
    WebDriverWait(browser, time_to_wait).until(ec.visibility_of_element_located((by_, selector)))

#define browser setup function
def browserSetup(user_agent: str = PC_USER_AGENT) -> WebDriver:
    #create Chrome browser with added arguements
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.add_argument("user-agent=" + user_agent)
    options.add_argument('log-level=3')
    options.add_argument("start-maximized")
    chrome_browser_obj = webdriver.Chrome(options=options)
    return chrome_browser_obj

#define function to input email and password onto config.txt using pickle lib
def inputCredentials():
	email = input('[INPUT] Enter Gamermine email: ')
	password = input('[INPUT] Enter Gamermine password: ')
	delay()

	configuration = {1: email, 2: password}
	with open('config.txt','wb') as account_dict:
		pickle.dump(configuration, account_dict)
	
	displayCredentials()
	
#define display credentials
def displayCredentials():
	#open config.txt to unpickle email and password and send to login function
	with open('config.txt','rb') as account_dict:
		accountinfo = pickle.load(account_dict)
	
	email = accountinfo[1]		
	password = accountinfo[2]
	print('Email: '+email)
	print('Password: '+password)
	delay()
	#set up browser and call login function
	browser = browserSetup()
	login(browser, email, password)


#define login function
def login(browser: WebDriver, email: str, pwd: str):
	   	browser.get('https://gamermine.com/r/freebitcoin')
	   	#wait for the page to complete loading
	   	waitUntilVisible(browser, By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/header/div/button', 10)
	   	delay()
	   	try:
	   		loginBtn = browser.find_element_by_css_selector('#main-content > div:nth-child(1) > header > div > button')
	   		loginBtn.click()
	   	except:
	   		pass
	   	#type in email
	   	print('[LOGIN]', 'Writing email...')
	   	browser.find_element_by_css_selector('body > div:nth-child(7) > div > div > div.dialog.auth-dialog > div.body > div > div.auth-form > input[type=text]:nth-child(1)').send_keys(email)
	   	delay()
	   	#type in password
	   	print('[LOGIN]', 'Writing password...')
	   	browser.find_element_by_css_selector('body > div:nth-child(7) > div > div > div.dialog.auth-dialog > div.body > div > div.auth-form > input[type=password]:nth-child(2)').send_keys(pwd)
	   	#click login
	   	browser.find_element_by_css_selector('body > div:nth-child(7) > div > div > div.dialog.auth-dialog > div.body > div > div.auth-form > button').click()
	   	delay()
	   	try:
	   		#detect if there's an alert on sign-in, typically indicated by a red bar above the login screen
	   		#send back to inputCredentials if unable to login
	   		waitUntilVisible(browser, By.CSS_SELECTOR, '#main-content > div.Toastify > div > div > div.Toastify__toast-body', 10)
	   		print('[LOGIN] Unable to login...')
	   		delay()
	   		browser.quit()
	   		inputCredentials()
	   	
	   	except:
	   		#if red bar not detected, log-in successful
	   		print('[LOGIN] Logged-in successfully.')
	   		checkGamermineLogin(browser) 
	   		

#def function to get account variables
def checkGamermineLogin(browser: WebDriver):
    #access Gamermine
    browser.get('https://gamermine.com/r/freebitcoin')
    delay()
    #accept Cookies
    try:
        browser.find_element_by_id('bnp_btn_accept').click()
    except:
        pass
    delay()
    #refresh page
    browser.get('https://gamermine.com')
    delay()
    #update account name
    ACCOUNT_NAME = str(browser.find_element_by_css_selector('#main-content > div:nth-child(2)\
    	> header > div.user > div.user-dropdown-wrapper > div > a > div > span').get_attribute('innerHTML'))
    #update counter
    POINTS_COUNTER = str(browser.find_element_by_class_name('balance-counter').get_attribute('innerHTML'))
   #update Gamermine inventory notifications
    INVENTORY = str(browser.find_element_by_css_selector('#main-content > div.bottom-tray.open > div.button-container > button.inventory-button.widget-button.action-trigger > div').get_attribute('innerHTML'))
    #update daily counter
    DAILY_COUNTER = str(browser.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[7]\
    	/div[1]/button[1]/div/span').get_attribute('innerHTML'))
    #display variables
    try: 
    	print('[ACCOUNT] You are currently logged into Gamermine as ' + str(ACCOUNT_NAME) +'.' )
    	print('[GOLD] You have ' + str(POINTS_COUNTER) + ' gold on your account!')    	
    	print('[INVENTORY] You have ' + str(INVENTORY) + ' new items in your inventory!')
    except:
    	pass
    #after displaying account variables, check if daily bonus is ready
    dailyChestReadyorNot(browser, DAILY_COUNTER)

#define function to check daily chest 
def dailyChestReadyorNot(browser: WebDriver, DAILY_COUNTER: str):
	#check value of daily counter
	if DAILY_COUNTER == "READY!":
			print('[DAILY BONUS] Attempting to claim the daily bonus...')
			getDailyBonus(browser)
	else: 
		pass
	#after getting daily bonus, check Steam reward
	openSteamReward(browser)
		
#define function to get daily bonus if counter is ready
def getDailyBonus(browser: WebDriver):
	#icon on bottom right of the screen 
	chest = browser.find_element_by_css_selector('#main-content > div.bottom-tray.open > div.button-container \
		> button.daily-bonus-button.action-trigger.widget-button.ready > div > span')
	chest.click()
	delay()
	dailyFree = (browser.find_element_by_css_selector('body > div:nth-child(11) \
		> div > div > div > div.body > div > div:nth-child(2) > div > h3 > div > span').get_attribute('innerHTML'))
	#click claim
	claimButton = browser.find_element_by_css_selector('body > div:nth-child(11) > div > div > div > div.body > button')
	claimButton.click()
	print('[DAILY BONUS] Successfully claimed ' + str(dailyFree) + ' gold!')
	delay()

#define function to open the Steam reward webpage
def openSteamReward (browser: WebDriver):
	browser.get('https://gamermine.com/earn/rewards/steam')
	steamRewardReadyorNot(browser)

#define function to check if Steam reward is available to claim
def steamRewardReadyorNot(browser: WebDriver):
	STEAM_REWARD = str(browser.find_element_by_css_selector('#main-content > div:nth-child(3) > div > div.middle > div > div > div.col-md-10.reward-content > div > div.hero.small.with-button > button').get_attribute('innerText'))
	if 'CLAIM' in STEAM_REWARD:
		delay()
		print('[STEAM REWARD] Attempting to claim Steam reward...')
		getSteamReward(browser)
	else:
		print('[STEAM REWARD] Check back in ' + str(STEAM_REWARD))
		browser.close()
		print('POWERED BY PASSIVEBOT.COM')
		input()
		browser.quit()

def getSteamReward(browser: WebDriver):
	steamAmount = (browser.find_element_by_css_selector('#main-content > div:nth-child(3) > div > div.middle > div > div > div.col-md-10.reward-content > div > div.hero.small.with-button > button > div > b > div > span').get_attribute('innerHTML'))
	claimButton = browser.find_element_by_css_selector('#main-content > div:nth-child(3) > div > div.middle > div > div > div.col-md-10.reward-content > div > div.hero.small.with-button > button')
	claimButton.click()
	delay()
	print('[STEAM REWARD] Successfully claimed ' + str(steamAmount) + ' gold!')
	delay()
	browser.close()
	print('POWERED BY PASSIVEBOT.COM')
	input()
	browser.quit()


print("""
 ██████╗  █████╗ ███╗   ███╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗███████╗ 
██╔════╝ ██╔══██╗████╗ ████║██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔════╝
██║  ███╗███████║██╔████╔██║█████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║█████╗  
██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══╝  
╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║███████╗
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝
""")
print("        Powered by: Passivebot.com                version 1.0\n")

#ticker used to determine if email.txt is empty or not
ticker = is_non_zero_file('config.txt')


if ticker ==1:
    print ("[LOGIN] Retrieving credentials...")
    displayCredentials()
else:
    print ("[LOGIN] Provide input credentials...")
    inputCredentials()