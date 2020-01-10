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

from utils.utils import Container


# Global variables:
main_url = "https://www.nejmqianyan.cn/index.php?c=week&m=year"
out_dir = "../processed_data/crawler/nejm/urls/"
article_dir = "../processed_data/crawler/nejm/articles/"
os.makedirs(out_dir, exist_ok=True)
os.makedirs(article_dir, exist_ok=True)


# Functions:
def to_include(element):
	include = True
	text = element.text


	table = re.match("表[0-9]{1,2}\.", text)
	figure = re.match("图[0-9]{1,2}\.", text)
	if text == "":
		include = False

	if table or figure:
		include = False

	if element.get_attribute("label") == "图片说明":
		include = False

	if "译者：" in text:
		include = False

	if "校对：" in text:
		include = False

	return include


def stop_crawling(element):
	stop_crawl = False

	if element.text.strip().startswith("Disclosure forms provided"):
		stop_crawl = True

	if element.text.strip().startswith("Disclosures for") \
		and element.text.strip().endswith("at time of publication"):
		stop_crawl = True

	return stop_crawl


def start_crawling(element):
	crawl = False
	if element.get_attribute("class") == \
		"f-body f-body--w-dropcap":
		crawl = True
	if element.get_attribute("class") == \
		"o-article-body__section-title a-article-h1 a-article-h1--underline f-h3" \
		and element.text == "Abstract":
		crawl = True
	return crawl


def crawl_zh_page(driver, output, verbose=False):

	print_and_log("Crawling Chinese website.")
	paragraphs = driver.find_elements_by_tag_name("p")

	with open(output, "w") as f:	

		for i, para in enumerate(paragraphs):
			if verbose: 
				print("Parsing paragraph {}".format(i), flush=True)

			spans = para.find_elements_by_tag_name("span")

			for span in spans:

				if stop_crawling(span):
					print("Stopped crawling at paragraph {}.".format(i))
					return

				if to_include(span):
					f.write(span.text)

			f.write("\n")

def login(driver):

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

	except:
		print("Already logged in!")
		logged_in = True


def get_zh_article_type(driver):
	journal_watch_icon = "https://nejmqianyan.cn/data/upload/20160929/1475128688604994.png"
	nejm_icon = "https://nejmqianyan.cn/data/upload/20160929/1475128654268409.png"

	xpath_query = "//img[@class='article_type_icon']"
	try:
		element = driver.find_element_by_xpath(xpath_query)
		link = element.get_attribute("src")
	except:
		link = ""

	if link == journal_watch_icon:
		_type = "journal_watch"
	elif link == nejm_icon:
		_type = "nejm"
	else:
		_type = "misc"

	return(_type)
	

def print_and_log(message):
	print(message, flush=True)
	logging.info(message)


def detect_dialog_window(driver):

	window = driver.find_elements_by_xpath("//div[@class='featherlight-content']")
	if window != []:
		return True
	else:
		return False


def close_dialog_window(driver):

	close_button = driver.find_element_by_xpath(
		"//button[@class='featherlight-close-icon featherlight-close']")
	close_button.click()


def detect_paywall(driver):
	xpath_query = "//a[@class='o-gateway__button o-gateway__button--secondary'" \
				  " and @data-interactiontype='subscribe_click']"

	paywall = driver.find_elements_by_xpath(xpath_query)
	if paywall != []:
		return True
	else:
		return False


def crawl_en_nejm(driver, output, verbose=False):
	
	print_and_log("Crawling English page.")
	crawl = False

	if detect_dialog_window(driver):
		close_dialog_window(driver)

	if detect_paywall(driver):
		raise RuntimeError("Paywall detected.")

	xpath_query = "//div[@class='m-inline-tabs__tab s-active']"
	body = driver.find_element_by_xpath(xpath_query)

	xpath_query = "//*[self::h2 or self::h3 or self::p]"
	elements = body.find_elements_by_xpath(xpath_query)

	with open(output, "w") as f:	

		for i, elem in enumerate(elements):

			if stop_crawling(elem):
				message = "Stopped crawling at paragraph {}.".format(i)
				print_and_log(message)
				return 

			if verbose: 
				print("Parsing paragraph {}".format(i), flush=True)
				
			if to_include(elem):
				f.write(elem.text)
				f.write("\n")


def crawl_en_journal_watch(driver, output, timeout=60, verbose=False):

	print_and_log("Crawling English Journal Watch.")

	try: 
		WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Comment') or contains(text(), 'Disclosures for')]")))
	except:
		print("Timeout.")
		return

	with open(output, "w") as f:

		sleep(4)
		
		xpath_query = "//*[self::h3 or self::p]"
		paragraphs = driver.find_elements_by_xpath(xpath_query)

		for i, p in enumerate(paragraphs):

			if verbose: 
				print("Parsing paragraph {}".format(i), flush=True)

			if stop_crawling(p):
				print("Stopped crawling at paragraph {}.".format(i))
				return

			if to_include(p):
				f.write(p.text)

			f.write("\n")


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
			comparison = "en_long"
		elif zh_len / en_len > epsilon:
			comparison = "zh_long"
		else:
			comparison = "equal"

	return comparison, zh_len, en_len 


def crawl_all_urls(container):

	total = len([_ for i in container.values() \
		for j in i.values() for k in j.values()])

	n = 0
	for year, month_dict in container.items():
		
		print_and_log("#############")
		print_and_log("# Year {} #".format(year))
		print_and_log("#############")

		for month, article_dict in month_dict.items():
			os.makedirs(os.path.join(article_dir, year, month), exist_ok=True)

			message = "# Crawling {}/{} #".format(year, month)
			print_and_log("######################")
			print_and_log(message)
			print_and_log("######################")

			for article, urls in article_dict.items():

				if n % 100 == 0:
					message = "### Progress: {}/{} Articles ###".format(n, total)
					print_and_log(message)

				article = article.replace("/","-").replace(" ", "").replace("•", "")
				message = "Article: {}".format(article)
				print_and_log(message)

				zh_out = "{}/{}/{}/{}.zh".format(
					article_dir, year, month, article)
				en_out = "{}/{}/{}/{}.en".format(
					article_dir, year, month, article)

				to_run = True
				if os.path.exists(zh_out) and os.path.exists(en_out):
					comparison, zh_len, en_len = \
						compare_zh_and_en(zh_out, en_out)

					print_and_log("Found articles on disk.")
					print_and_log("No. paragraphs (zh): {}".format(zh_len))
					print_and_log("No. paragraphs (en): {}".format(en_len))
					
					if comparison == "equal":
						print_and_log("zh and en articles are equivalent.")
						to_run = False
					else: 
						print_and_log("zh and en articles differ - rerunning.")

				if to_run:
					zh_url, en_url = urls
				
					driver.get(zh_url)
					_type = get_zh_article_type(driver)
					if _type == "misc":
						print_and_log("Unknown article type.")

					else:
						crawl_zh_page(driver, zh_out)
						driver.get(en_url)

					 	if _type == "nejm":
							crawl_en_nejm(driver, en_out)

						elif _type == "journal_watch":
							crawl_en_journal_watch(driver, en_out)
					
				n += 1


def main():

	# Initialize Chrome driver:
	chrome_options = Options()
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--disable-gpu")
	chrome_options.add_argument("--remote-debugging-port=9222")
	driver = webdriver.Chrome(options=chrome_options)
	driver.get(main_url)
	login(driver)

	# Initialize container:
	container = Container()
	container.read_from_disk(out_dir)

	# Uncomment the following lines if re-traversing the NEJM website.
	container.traverse(driver, out_dir)

	# Logging:
	log_fn = "{}/article.log".format(article_dir)
	logging.basicConfig(filename=log_fn, format="%(message)s")
	crawl_all_urls(container)


if __name__ == "__main__":
	main()