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

def get_years(driver):
	elements = driver.find_elements_by_class_name("field_video_a")
	
	years = {}
	for elem in elements:
		a = elem.find_element_by_tag_name("a")
		hyperlink = a.get_attribute("href") 
		years[a.text] = hyperlink

	return years

def get_months(driver, year_url):
	elements = driver.find_elements_by_xpath("//a[@role='tab']")

	months = {}
	for elem in elements:
		hyperlink = elem.get_attribute("href")
		hyperlink = hyperlink.replace(year_url, "")
		if elem.text != "":
			months[elem.text] = hyperlink

	return months

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


def get_url_to_english_page(driver):
	try:
		href = driver.find_element_by_class_name("font-TNR.ft-red.ft_title_e")
		url = href.get_attribute("href")
	except:
		url = None

	return url	


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

				article = article.replace("/","-")
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


class Container(dict):

	def read_from_disk(self, root_dir):

		self.clear()
		years = glob.glob(root_dir + "*")
		years = [os.path.basename(x) for x in years]

		for year in years:
		
			print("Year: {}".format(year))
			sub_dir = "{}/{}/".format(root_dir, year)
			months = glob.glob(sub_dir + "*.txt")
			months = [os.path.basename(x).replace(".txt", "") \
				for x in months]

			self[year] = {}
			for month in months:
		
				print("Month: {}".format(month))
				self[year][month] = {}
				fn = "{}/{}.txt".format(sub_dir, month)
				with open(fn, "r") as f:
					for line in f:
						split_line = line.split("\t")
						title = split_line[0].strip()
						zh_url = split_line[1].strip()
						en_url = split_line[2].strip()
						self[year][month][title] = (zh_url, en_url)


	def traverse(self, driver, out_dir):

		years = get_years(driver)
		print("Found the following years:")
		for year in years:
			print(year)

		for year, year_url in years.items():

			print("Year: {}".format(year))
			os.makedirs(os.path.join(out_dir, year), exist_ok=True)

			if year not in self: 
				self[year] = {}
			
			driver.get(year_url)
			
			months = get_months(driver, year_url)
			print("Found the following months:")
			for month in months:
				print(month)

			for month, month_href in months.items():

				print("Month: {}.".format(month))
				if month not in self[year]:
					self[year][month] = {}

				xpath_query = "//a[@href='{}']".format(month_href)
				month_element = driver.find_element_by_xpath(xpath_query)
				month_element.click() # redirect driver to that month.
				xpath_query = "//div[@class='weeklycover_box']" \
							  "/div[@class='box_70c']//a"
				articles = driver.find_elements_by_xpath(xpath_query)

				fn = "{}.txt".format(os.path.join(out_dir, year, month))
				with open(fn, "a+") as f:
					for art in articles:
						text = art.text

						# Check if article already in self. 
						if text in self[year][month]:
							print("{} already in self.".format(text))
						
						elif "Vol." in text and "No." in text:
							print("{} is the TOC".format(text))
						
						elif text != "" and text != "\ue735":
							print("Article: {}".format(text))
							zh_url = art.get_attribute("href")
							article_driver = webdriver.Chrome()
							article_driver.get(zh_url)

							en_url = get_url_to_english_page(article_driver)
							article_driver.close()
							if en_url is not None:
								self[year][month][text] = (zh_url, en_url)
								f.write("\t".join([text, zh_url, en_url]) + "\n")
								f.flush()


	def write_to_disk(self, out_dir):

		for year, months in self.items():
			os.makedirs(os.path.join(out_dir, year), exist_ok=True)

			for month, articles in months.items():
				fn = "{}.txt".format(os.path.join(out_dir, year, month))

				with open(fn, "w") as f:
					for title, (zh_url, en_url) in articles.items():
						f.write("\t".join([title, zh_url, en_url]) + "\n")
						f.flush()


	def count_articles(self):
		proto_df = defaultdict(list)
		for year, months in self.items():
			for month, articles in months.items():
				proto_df["year"].append(year)
				proto_df["month"].append(month)
				proto_df["articles"].append(len(articles))
		df = pd.DataFrame(proto_df)
		df.sort_values(by=["year", "month"], inplace=True)
		return df

# Constants:
main_url = "https://www.nejmqianyan.cn/index.php?c=week&m=year"
out_dir = "../processed_data/crawler/nejm/urls/"
article_dir = "../processed_data/crawler/nejm/articles/"
os.makedirs(out_dir, exist_ok=True)
os.makedirs(article_dir, exist_ok=True)

# Construct urls.
# chrome_options = Options()
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--remote-debugging-port=9222")
# driver = webdriver.Chrome(options=chrome_options)
driver = webdriver.Chrome()
driver.get(main_url)
login(driver)

# container = Container()
# container.read_from_disk(out_dir)
# container.traverse(driver, out_dir)
# container.write_to_disk(out_dir)

# Logging:
# log_fn = "{}/article.log".format(article_dir)
# logging.basicConfig(filename=log_fn, format="%(message)s")
crawl_all_urls(container)


# Testing
# zh_url = "https://www.nejmqianyan.cn/article/YXQYcpc1208154"
en_url = "https://www.jwatch.org/na43336/2017/01/24/yet-long-way-go-fib-guidelines?query=nejmyxqy"
# zh_out = "test.zh"
en_out = "test.en"


# driver.get(zh_url)
# crawl_zh_page(driver, zh_out)
driver.get(en_url)
crawl_en_journal_watch(driver, en_out, verbose=True)


