import requests

def scrapingtool(url:str):
	response= requests.get(url)
	return(response.text)

if __name__ =='__main__':
	result=scrapingtool('http://13.36.65.25:32784/')
	print(result)
	