import requests

def scrapingtool(url:str):
	response= requests.get(url)
	return(response.text)