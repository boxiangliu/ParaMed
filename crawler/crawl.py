import sys
import re
import os
import glob
from collections import defaultdict
from copy import deepcopy
import logging
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

sys.path.append(".")
from utils.utils import Container


# Global variables:
out_dir = "../processed_data/crawler/nejm/urls/"
article_dir = "../processed_data/crawler/nejm/articles/"

traverse = False # Whether to get the article urls.
crawl = True # Whether to get the article content.
os.makedirs(out_dir, exist_ok=True)
os.makedirs(article_dir, exist_ok=True)


#####################
# Utility Functions #
#####################
def print_and_log(message):
	print(message, flush=True)
	logging.info(message)


def detect_dialog_window(driver):

	window = driver.find_elements_by_xpath(\
		"//div[@class='featherlight-content']")
	if window != []:
		return True
	else:
		return False


def close_dialog_window(driver):
	close_button = driver.find_element_by_xpath(
		"//button[@class='featherlight-close-icon featherlight-close']")
	close_button.click()


def nejm_signin(driver):
	driver.get("https://www.nejm.org/")

	xpath_query = "//a[@data-interactiontype='sign_in_click']"
	sign_in_click = driver.find_element_by_xpath(xpath_query)
	sign_in_click.click()

	login = driver.find_element_by_id("login")
	login.send_keys("svail-admin@baidu.com")

	password = driver.find_element_by_id("password")
	password.send_keys("Baidu2020")

	driver.find_element_by_id("btnSignIn").click()
	print("Signed in to NEJM.")


def detect_paywall(driver):
	xpath_query = "//a[@class='o-gateway__button o-gateway__button--secondary'" \
				  " and @data-interactiontype='subscribe_click']"

	paywall = driver.find_elements_by_xpath(xpath_query)
	if paywall != []:
		nejm_signin(driver)


def nejm_signout(driver):
	xpath_query = "//a[@data-interactiontype='sign_out_click']"
	driver.find_elements_by_xpath(xpath_query)[0].click()


def yxqy_login(driver):

	driver.get("https://www.nejmqianyan.cn/index.php?c=week&m=year")
	try:
		xpath_query = "//a[@href='javascript:;' and @class='dropdown-toggle']"
		dropdown = driver.find_element_by_xpath(xpath_query)
		dropdown.click()
		membername = driver.find_element_by_name("membername")
		membername.clear()
		membername.send_keys("publicuser")

		password = driver.find_element_by_name("password")
		password.clear()
		password.send_keys("publicuser")

		login = driver.find_element_by_class_name(\
			"btn.btn-default.fastLoginBtn.login-top")
		login.click()
		sleep(2)

	except:
		print("Already logged in to YXQY!")
		logged_in = True


def jw_login(driver):
	try:
		email = driver.find_element_by_xpath(\
			"//article-page//input[@id='email_text']")
		email.clear()
		email.send_keys("bliuforgit@gmail.com")
		password = driver.find_element_by_xpath(\
			"//article-page//input[@id='pwd_text']")
		password.clear()
		password.send_keys("password")
		login = driver.find_element_by_xpath(\
			"//article-page//button")
		login.click()
		sleep(3)

	except:
		print("Already logged into Journal Watch!")
		logged_in = True


######################
# Crawling Functions #
######################
def crawl_zh_page(driver, article_id, zh_url, out_prefix, verbose=False):
	driver.get(zh_url)
	print_and_log(f"Crawling Chinese article: {article_id}.")

	full_article = driver.find_element_by_id("nejm-article-content").text
	full_text = [x.strip() for x in full_article.split("\n")]

	with open(f"{out_prefix}.full.zh", "w") as f:
		for i in full_text:
			f.write(i + "\n")


def crawl_en_page(driver, article_id, en_url, out_prefix, verbose=False):

	driver.get(en_url)
	if detect_dialog_window(driver):
		close_dialog_window(driver)

	# Sign in if paywalled.
	detect_paywall(driver)

	print_and_log(f"Crawling English article: {article_id}.")
	article_type = re.sub("[0-9]+", "", article_id).replace("%", "")
	print_and_log(f"Article type: {article_type}.")

	# Crawl article from NEJM website
	if article_type != "jw.na":
		sleep(1)
		full_article = driver.find_element_by_id("full").text
		full_text = [x.strip() for x in full_article.split("\n")]

		try:
			boxed_text = driver.find_element_by_class_name("m-boxed-text").text
			full_text_no_box = [x.strip() for x in \
				full_article.replace(boxed_text, "").split("\n")]
			print("Found boxed text.")
		except:
			full_text_no_box = full_text
			print("No boxed text.")

	# Crawl article from Journal Watch website
	else:
		try:
			WebDriverWait(driver, timeout=60).\
				until(EC.presence_of_element_located(\
					(By.CLASS_NAME, "article-detail")))
			sleep(1)
		except:
			print("Timeout!")
			return

		jw_login(driver)
		full_article = driver.find_element_by_class_name("article-detail").text
		full_text = [x.strip() for x in full_article.split("\n")]
		full_text_no_box = full_text

	with open(f"{out_prefix}.full.en", "w") as f:
		for i in full_text:
			f.write(i + "\n")

	with open(f"{out_prefix}.nobox.en", "w") as f:
		for i in full_text_no_box:
			f.write(i + "\n")


def compare_zh_and_en(zh_fn, en_fn, epsilon = 2):
	with open(zh_fn, "r") as f_zh, \
		open(en_fn, "r") as f_en:
		zh = f_zh.readlines()
		en = f_en.readlines()

	zh = [x for x in zh if x.strip() != ""]
	en = [x for x in en if x.strip() != ""]
	zh_len, en_len = len(zh), len(en)
	
	if en_len == 0 or zh_len == 0:
		comparison = "empty_article"

	else:
		if en_len / zh_len > epsilon:
			comparison = "en_too_long"
		elif zh_len / en_len > epsilon:
			comparison = "zh_too_long"
		else:
			comparison = "equal"

	return comparison, zh_len, en_len 


def crawl_all_urls(driver, container):

	total = len([_ for i in container.values() \
		for j in i.values() for k in j.values()])

	n = 0
	for year, month_dict in container.items():
		
		print_and_log("#############")
		print_and_log(f"# Year {year} #")
		print_and_log("#############")

		for month, article_dict in month_dict.items():
			os.makedirs(os.path.join(article_dir, year, month), exist_ok=True)

			print_and_log("####################")
			print_and_log(f"# Crawling {year}/{month} #")
			print_and_log("####################")

			for article_id, (zh_title, en_title, zh_url, en_url) in article_dict.items():

				if n % 100 == 0:
					message = f"### Progress: {n}/{total} Articles ###"
					print_and_log(message)

				message = f"Article: {zh_title}/{en_title}"
				print_and_log(message)

				out_prefix = f"{article_dir}/{year}/{month}/{article_id}"
				zh_out = f"{out_prefix}.full.zh"
				en_out = f"{out_prefix}.nobox.en"

				# Crawl articles:
				if not os.path.exists(zh_out):
					crawl_zh_page(driver, article_id, zh_url, out_prefix)
				if not os.path.exists(en_out):
					crawl_en_page(driver, article_id, en_url, out_prefix)

				n += 1


def main():
	# Initialize Chrome driver:
	chrome_options = Options()
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument("--remote-debugging-port=9222")
	driver = webdriver.Chrome(options=chrome_options)
	
	yxqy_login(driver)
	nejm_signin(driver)

	# Initialize container:
	container = Container()
	container.read_from_disk(out_dir)

	# Traversing the NEJM website.
	if traverse:
		container.traverse(driver, out_dir)

	# Logging:
	if crawl:
		log_fn = "{}/article.log".format(article_dir)
		logging.basicConfig(filename=log_fn, \
			format="%(message)s", level=logging.DEBUG)
		crawl_all_urls(driver, container)

	nejm_signout(driver)


if __name__ == "__main__":
	main()