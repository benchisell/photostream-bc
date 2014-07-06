from bs4 import BeautifulSoup
import urllib
import io

"""  garconjon  
garconjon_scraper("http://www.garconjon.com/")

"""
"http://www.garconjon.com/"

def garconjon_scraper(url):
	f = urllib.urlopen(url)
	html = f.read()
	soup = BeautifulSoup(html)

	with io.open('log.txt', 'a', encoding='utf8') as logfile:
		for tag in soup.findAll('a', attrs={"imageanchor" : "1"}): 
	   		image = tag['href']
	   		print(image)
	   		logfile.write(u"%s\n" % (image))




"""backyard bill

def backyard_bill_scraper(url):
	f = urllib.urlopen(url)
	html = f.read()
	soup = BeautifulSoup(html)

	for tag in soup.findAll('img', alt=True): 
	    print(tag['src'])

backyard_bill_scraper("http://www.backyardbill.com/pictures/eric-degenhard-larchmont-ny/")

"""




