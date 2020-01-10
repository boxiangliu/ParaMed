import re
import os
import glob
import time
from collections import defaultdict, Counter
from dateutil import parser
import pandas as pd
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktTrainer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--remote-debugging-port=9222")

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
		month = elem.text.replace("月","")
		if month != "":
			months[month] = hyperlink

	return months


def get_url_to_english_page(driver):
	try:
		href = driver.find_element_by_class_name("font-TNR.ft-red.ft_title_e")
		url = href.get_attribute("href")
	except:
		url = None

	return url


def get_english_title(article_driver, article_id):

	if "jw" in article_id: # journal watch articles
		class_ = "page-title"
	else:
		class_ = "title_default"

	timeout = 60
	en_title = ""
	try:
		WebDriverWait(article_driver, timeout).\
			until(EC.presence_of_element_located(
				(By.CLASS_NAME, class_)))

		while en_title == "":
			time.sleep(0.2)
			en_title = article_driver.\
				find_element_by_class_name(class_).text

	except:
		print("Timeout!")
		en_title = ""
	
	return en_title


class Container(dict):

	def read_from_disk(self, root_dir):

		self.clear()
		print("\n")
		print("################################")
		print("#### Reading existing files ####")
		print("################################")

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
						year = split_line[0].strip()
						month = split_line[1].strip()
						article_id = split_line[2].strip()
						zh_title = split_line[3].strip()
						en_title = split_line[4].strip()
						zh_url = split_line[5].strip()
						en_url = split_line[6].strip()
						self[year][month][article_id] = \
							(zh_title, en_title, zh_url, en_url)


	def traverse(self, driver, out_dir):

		print("\n")
		print("#################################")
		print("#### Traversing NEJM website ####")
		print("#################################")

		years = get_years(driver)
		print(f"Found a total of {len(years)} years:")
		for year in years:
			print(year)

		article_driver = webdriver.\
			Chrome(options=chrome_options)

		for year, year_url in years.items():

			print("Year: {}".format(year))
			os.makedirs(os.path.join(out_dir, year), exist_ok=True)

			if year not in self: 
				self[year] = {}
			
			driver.get(year_url)
			
			months = get_months(driver, year_url)
			print(f"Found a total of {len(months)} months:")
			for month in months:
				print(month)

			for month, month_href in months.items():

				print("Month: {}.".format(month))
				if month not in self[year]:
					self[year][month] = {}

				xpath_query = "//a[@href='{}']".format(month_href)
				month_element = driver.find_element_by_xpath(xpath_query)
				month_element.click() # redirect driver to that month.
				month_id = month_href.replace("#","") # The id and href is off by a # sign.
				xpath_query = f"//div[@id='{month_id}']//"\
							  "div[@class='weeklycover_box']"\
							  "//div[@class='box_70c']//a"
				articles = driver.find_elements_by_xpath(xpath_query)
				print(f"Found a total of {len(articles)} articles:")
				for article in articles:
					print(article.text)

				fn = "{}.txt".format(os.path.join(out_dir, year, month))
				with open(fn, "a+") as f:
					for art in articles:
						zh_title = art.text.replace("•","").strip()

						if "Vol." in zh_title and "No." in zh_title:
							print("{} is the TOC. Skip.".format(zh_title))
						
						elif zh_title != "" and zh_title != "\ue735":
							print("Article: {}".format(zh_title))
							zh_url = art.get_attribute("href")

							article_id = zh_url.split("/")[-1]
							article_id = re.sub("[yY][xX][qQ][yY]-*",\
								"", article_id) # Remove the yxqy prefix

							if article_id in self[year][month]:
								print(f"# Warning: Article already stored. Skip.")
								continue # Avoid repeating work

							article_driver.get(zh_url)
							en_url = get_url_to_english_page(article_driver).\
								split("?")[0] # Remove unnecessary suffix
							article_driver.get(en_url)
							en_title = get_english_title(
								article_driver, article_id)

							self[year][month][article_id] = \
								(zh_title, en_title, zh_url, en_url)

							if en_title != "":
								f.write("\t".join([year, month, article_id, \
									zh_title, en_title, zh_url, en_url]) + "\n")
							else:
								f.write("\t".join([year, month, article_id, \
									zh_title, "MISSING", zh_url, en_url]) + "\n")
							f.flush()

		article_driver.close()


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


	def get_all_article_paths(self, root_dir, ext):
		article_paths = []
		for year, months in self.items():
			for month, articles in months.items():
				for article, (_,_) in articles.items():
					article_paths.append("{}/{}/{}/{}.{}".format(
						root_dir, year, month, article, ext))

		print("{} Articles.".format(len(article_paths)), flush=True)
		return article_paths

def read_and_preprocess_article(path, lang):
	article = get_article_as_lowercase_string(path)
	
	if lang == "en":	
		article = article.replace("\n. opens in new tab\n", "")
	
	elif lang == "zh":
		pass
	
	else: 
		raise ValueError("Unknown language: {}".format(lang))

	return article

def get_article_as_lowercase_string(path):
	
	with open(path, "r") as f:
		article = f.read().lower()

	return article


def get_nltk_sent_tokenizer(container, lang):

	assert lang in ["zh", "en"], "Unknown language."

	trainer = PunktTrainer()
	if isinstance(container, Container):
		article_paths = container.get_all_article_paths(
			root_dir="../processed_data/crawler/nejm/articles/",
			ext=lang)
	elif isinstance(container, list):
		print("{} Articles.".format(len(container)))
		article_paths = container
	else:
		raise ValueError("Cannot parse container with class {}".\
			format(container.__class__))

	missing_count = 0
	for path in article_paths:
		try:
			article = get_article_as_lowercase_string(path)
			trainer.train(text=article, finalize=False)
		except FileNotFoundError:
			print("{} not found.".format(path))
			missing_count += 1
	print("{} articles not found.".format(missing_count))

	trainer.finalize_training()
	tokenizer = PunktSentenceTokenizer(trainer.get_params())
	return tokenizer


def translate(text, translator, src="zh-cn", dest="en"):
	return [x.text.lower() for x in \
		translator.translate(text, src=src, dest=dest)]


class RegexSentenceTokenizer():
	def __init__(self, regex):
		self.regex = regex

	def tokenize(self, text):
		sents = re.split(pattern=self.regex, string=text)
		punctuations = re.findall(pattern=self.regex, string=text)
		
		sent_len = len(sents)
		punct_len = len(punctuations)

		assert (sent_len <= (punct_len + 1)) and (punct_len <= sent_len), \
			print("Found {} sentences and {} punctuations.".\
				format(sent_len, punct_len))

		for i, p in enumerate(punctuations):
			sents[i] += p

		sents = [x.strip() for x in sents]
		
		if sents[-1] == "":
			sents.pop()

		return sents


def get_sentences(sent_tokenizers, texts):
	if sent_tokenizers[0] is None:
		return []

	if not isinstance(texts, list):
		texts = [texts]

	for tokenizer in sent_tokenizers:
		sentences = []
		for t in texts:
			s = tokenizer.tokenize(t)
			sentences += s
		texts = sentences
	
	return sentences


class AnnoStr(str):
	def __new__(cls, text, sent_tokenizers):
		return super().__new__(cls, text)

	def __init__(self, text, sent_tokenizers):
		self.detect_numbers()
		self.detect_headers()
		self.count_sentences(sent_tokenizers)

	def detect_headers(self):
		text = self.strip()
		group = 0 # default type
		exact = {"abstract": 1,
			   "摘要": 1,
			   "background": 2,
			   "背景": 2,
			   "methods": 3, 
			   "方法": 3,
			   "results": 4,
			   "结果": 4,
			   "conclusions": 5,
			   "结论": 5, 
			   "study population": 6,
			   "研究人群": 6,
			   "trial regimen": 7,
			   "trial regimens": 7,
			   "试验治疗方案": 7,
			   "trial outcomes": 8,
			   "试验结局": 8,
			   "trial populations": 9,
			   "trial population": 9,
			   "试验人群": 9,
			   "discussion": 10, 
			   "讨论": 10,
			   "trial design and oversight": 11,
			   "试验设计和监管": 11,
			   "patient population": 12,
			   "患者人群": 12,
			   "statistical analysis": 13,
			   "统计学分析": 13,
			   "patients": 14,
			   "患者": 14,
			   "trial design": 15, 
			   "试验设计": 15,
			   "疗效": 16,
			   "效果": 16, 
			   "有效性": 16,
			   "efficacy": 16
			   }

		if text in exact:
			group = exact[text]
		elif text.endswith("终点") or \
			 text.endswith("end points") or \
			 text.endswith("end point"):
			 group = 17
		elif text.endswith("评估") or \
			 text.endswith("assessment") or \
			 text.endswith("assessments"):
			 group = 18
		elif text.endswith("安全性") or \
			 text.endswith("safety"):
			 group = 19
		else:
			pass
		self.group = group


	def detect_numbers(self):
		numbers = re.findall("\d", self)
		self.number = Counter(numbers)

	def count_sentences(self, sent_tokenizers):
		sentences = get_sentences(sent_tokenizers, self)
		self.num_sents = len(sentences)
		self.sents = sentences


class Article():
	def __init__(self, path, lang, sent_tokenizers=None):
		self.path = path
		self.lang = lang
		self.sent_tokenizers = sent_tokenizers \
			if isinstance(sent_tokenizers, list) \
			else [sent_tokenizers] 

		self.article = read_and_preprocess_article(path, lang)
		self.paragraphs = [AnnoStr(x, self.sent_tokenizers) \
			for x in self.article.split("\n") if x != ""]
		self.filter_paragraphs()

		self.sentences = get_sentences(
			self.sent_tokenizers, self.kept_paragraphs)

	def is_boilerplate(self, text):

		lang = self.lang
		text = text.strip()

		def is_date(text):
			try:
				parser.parse(text)
				return True
			except ValueError:
				return False

		def is_reviewer_intro(text):
			text = text.strip()
			last_three_words = " ".join(text.split(" ")[-3:])
			last_two_words = " ".join(last_three_words.split(" ")[-2:])
			if is_date(last_three_words) or \
				is_date(last_two_words):
				if "reviewing" in text:
					return True
				if text.startswith("comments"):
					return True
			return False

		english_boilerplates = ["access provided by",
			"access provided by lane medical library, "\
			"stanford university med center",
			"lane medical library, stanford university med center",
			"subscribe", 
			"or renew",
			"institution: stanford university",
			"original article",
			"metrics",
			"editorial",
			"clinical problem-solving",
			"perspective",
			"audio interview",
			"download",
			"video",
			"focus on research",
			"history of clinical trials"
			]

		chinese_boilerplates = ["图1.", "图2.", "图3.", "图4.",
			"图5.", "表1.", "表2.", "表3.", "表4.", "表5.",
			"nothing to disclose"]

		if lang == "en":

			if is_date(text):
				return True
			elif is_reviewer_intro(text):
				return True
			elif text in english_boilerplates:
				return True
			elif re.search("\([0-9]{2}:[0-9]{2}\)", text):
				return True
			elif text.startswith("copyright ©"):
				return True
			elif text.startswith("nejm journal watch"):
				return True
			elif text.startswith("supported by"):
				return True
			elif text.startswith("the discovehr study was partially funded"):
				return True
			else:
				return False

		elif lang == "zh":

			if text in chinese_boilerplates:
				return True
			elif text.startswith("评论"):
				return True
			elif text.startswith("引文"):
				return True
			elif text.startswith("出版时的编辑声明"):
				return True
			elif text.startswith("supported by"):
				return True
			elif text.startswith("the discovehr study was partially funded"):
				return True
			else:
				return False

		else:
			raise ValueError("Unknown language: {}".format(lang))


	def filter_paragraphs(self):

		kept_paragraphs = []
		filtered_paragraphs = []
		for para in self.paragraphs:

			if para.strip() == "":
				continue

			if self.is_boilerplate(para):
				filtered_paragraphs.append(para)
			else:
				kept_paragraphs.append(para)


		self.kept_paragraphs = kept_paragraphs
		self.filtered_paragraphs = filtered_paragraphs


	def get_paragraph_lengths(self):
		if self.lang == "en":
			lengths = [len(para.split(" ")) \
				for para in self.paragraphs \
				if len(para) != 0]

		elif self.lang == "zh":
			lengths = []
			for para in self.paragraphs:
				para = re.sub("[a-z]", "", para)
				length = len(para)
				if length != 0: 
					lengths.append(len(para))

		else:
			raise ValueError("Language not supported: {}".\
				format(self.lang))

		return lengths


	def write_to_disk(self, out_fn, level):
		if level == "sentence":
			with open(out_fn, "w") as f:
				for sent in self.sentences:
					f.write(sent + "\n")
		elif level == "article":
			with open(out_fn, "w") as f:
				f.write(self.article)
		elif level == "paragraph":
			with open(out_fn, "w") as f:
				for para in self.paragrahs:
					f.write(para + "\n")
		else:
			raise ValueError("Unknown level: {}".format(level))

