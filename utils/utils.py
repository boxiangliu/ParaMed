import os
import glob
from collections import defaultdict
import pandas as pd

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


def get_url_to_english_page(driver):
	try:
		href = driver.find_element_by_class_name("font-TNR.ft-red.ft_title_e")
		url = href.get_attribute("href")
	except:
		url = None

	return url	


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
