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
main_url = "https://www.nejmqianyan.cn/index.php?c=week&m=year"
out_dir = "../processed_data/crawler/nejm/urls/"
article_dir = "../processed_data/crawler/nejm/articles/"

traverse = False # Whether to get the article urls.
crawl = True # Whether to get the article content.
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


def zh_unwanted(x):
	if re.match("表[0-9]{1,2}\.", x) or \
		re.match("图[0-9]{1,2}\.", x) or \
		x.startswith("译者：") or \
		x.startswith("校对：") or \
		x.startswith("统计学校对：") or x == "":
		return False
	else:
		return True


def crawl_zh_page(driver, article_id, zh_url, out_prefix, verbose=False):
	driver.get(zh_url)
	print_and_log(f"Crawling Chinese article: {article_id}.")

	full_article = driver.find_element_by_id("nejm-article-content")
	full_text = [x.strip() for x in full_article.text.split("\n")]

	contents = full_article.find_elements_by_class_name("font-size-content")
	content_text = [x.text.strip() for x in contents]

	titles = full_article.find_elements_by_class_name("font-size-title")
	title_text = [x.text.strip() for x in titles]

	content_filtered = [x for x in filter(zh_unwanted, content_text)]
	title_filtered = [x for x in filter(zh_unwanted, title_text)]

	title_content_set = set(content_filtered + title_filtered)
	filtered_text = [x for x in full_text if x in title_content_set]

	with open(f"{out_prefix}.full.zh", "w") as f:
		for i in full_text:
			f.write(i + "\n")

	with open(f"{out_prefix}.filt.zh", "w") as f:
		for i in filtered_text:
			f.write(i + "\n")


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
		sleep(2)

	except:
		print("Already logged in!")
		logged_in = True


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


def en_unwanted(x):
	if x.text == "" or \
		x.get_attribute("class") == "m-media-item" or \
		x.text == "Author Affiliations" or \
		x.text == "Supplementary Material" or \
		re.match("References \([0-9]+\)", x.text) or \
		re.match("Citing Articles \([0-9]+\)", x.text) or \
		x.text == "Letters":
		return False
	else:
		return True


def remove_text_after_disclosure(l):
	index = len(l)
	for i, x in enumerate(l):
		if re.match("Disclosure", x):
			index = i
	return l[:index]


def crawl_en_page(driver, article_id, en_url, out_prefix, verbose=False):
	driver.get(en_url)
	if detect_dialog_window(driver):
		close_dialog_window(driver)

	if detect_paywall(driver):
		raise RuntimeError("Paywall detected.")

	print_and_log(f"Crawling English article: {article_id}.")
	article_type = re.sub("[0-9]+", "", article_id)
	print_and_log(f"Article type: {article_type}.")

	if article_type != "jw.na":
		full_article = driver.find_element_by_id("full")
		full_text = [x.strip() for x in full_article.text.split("\n")]

		paragraph = full_article.find_elements_by_tag_name("p")
		h2 = full_article.find_elements_by_tag_name("h2")
		h3 = full_article.find_elements_by_tag_name("h3")

		paragraph_filtered = [x.text for x in filter(en_unwanted, paragraph)]
		h2_filtered = [x.text for x in filter(en_unwanted, h2)]
		h3_filtered = [x.text for x in filter(en_unwanted, h3)]

		paragraph_h2_h3_set = set(paragraph_filtered + h2_filtered + h3_filtered)
		filtered_text = [x for x in full_text if x in paragraph_h2_h3_set]
		filtered_text = remove_text_after_disclosure(filtered_text)
	else:
		pass # Put Journal Watch code here:

	with open(f"{out_prefix}.full.en", "w") as f:
		for i in full_text:
			f.write(i + "\n")

	with open(f"{out_prefix}.filt.en", "w") as f:
		for i in filtered_text:
			f.write(i + "\n")

en_url = "http://www.nejm.org/doi/full/10.1056/NEJMoa1602074"
article_id = "oa1602074"
out_prefix = "test"
crawl_en_page(driver, article_id, en_url, out_prefix)


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
		print_and_log(f"# Year {year} #")
		print_and_log("#############")

		for month, article_dict in month_dict.items():
			os.makedirs(os.path.join(article_dir, year, month), exist_ok=True)

			print_and_log("######################")
			print_and_log(f"# Crawling {year}/{month} #")
			print_and_log("######################")

			for article_id, (zh_title, en_title, zh_url, en_url) in article_dict.items():

				if n % 100 == 0:
					message = f"### Progress: {n}/{total} Articles ###"
					print_and_log(message)

				message = f"Article: {zh_title}/{en_title}"
				print_and_log(message)

				out_prefix = f"{article_dir}/{year}/{month}/{article_id}"
				zh_out = out_prefix + ".zh"
				en_out = out_prefix + ".en"

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
					
					# Crawl Chinese article:
					crawl_zh_page(driver, article_id, zh_url, out_prefix)

					# Crawl English article:
					driver.get(en_url)
					_type = "journal_watch" if "jw" in article_id else "nejm"
					if _type == "nejm":
						crawl_en_nejm(driver, en_out)

					elif _type == "journal_watch":
						crawl_en_journal_watch(driver, en_out)
					
				n += 1


def main():

	# Initialize Chrome driver:
	chrome_options = Options()
	# chrome_options.add_argument("--no-sandbox")
	# chrome_options.add_argument("--headless")
	# chrome_options.add_argument("--disable-gpu")
	# chrome_options.add_argument("--remote-debugging-port=9222")
	driver = webdriver.Chrome(options=chrome_options)
	driver.get(main_url)
	login(driver)

	# Initialize container:
	container = Container()
	container.read_from_disk(out_dir)

	# Uncomment the following lines if re-traversing the NEJM website.
	if traverse:
		container.traverse(driver, out_dir)

	# Logging:
	if crawl:
		log_fn = "{}/article.log".format(article_dir)
		logging.basicConfig(filename=log_fn, format="%(message)s")
		crawl_all_urls(container)


if __name__ == "__main__":
	main()