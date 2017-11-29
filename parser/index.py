#!/usr/bin/python
# -*- coding: utf-8 -*-

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from selenium import webdriver
import time, json, threading

# Call function after a certain period
def setInterval(func, time):
	e = threading.Event()
	while not e.wait(time):
		func()

# Web Scraping
def parse():
	# At first we need to call a server to get information

	# Server url
	url = 'https://onfeedvkbot.herokuapp.com/getsubs' 
	# Empty post field. We need to get POST-data information from server.
	post_fields = {}    

	request = Request(url, urlencode(post_fields).encode())
	input = json.loads(urlopen(request).read().decode())

	print(input)

	# We are using PhantomJS to web scrap data from urls  
	driver = webdriver.PhantomJS()
	driver.set_window_size(1000, 700) 

	for link in input:
		# Now only VK-references are supported

		url = "https://vk.com/{}".format(group[0])
		driver.get(url)

		# We pull out the posts of the group
		posts = driver.find_elements_by_css_selector('._post_content')

		# Create output
		output = {'content': [], 'title': driver.find_element_by_css_selector('.page_name').text, 'url': group[0]}

		for post in posts:
			try:
				if post.find_element_by_css_selector('.rel_date_needs_update'):
					# Check for relevance
					time = post.find_element_by_css_selector('.rel_date_needs_update').get_attribute('time')

					# If the time of the last post was later than our last check, then we send it to the server
					if int(time) > int(group[1]):
						localOutput = {
							'time' : time,
							'url'  : "{}".format(post.find_element_by_css_selector('.post_link').get_attribute('href')),
							'text' : 0,
							'image': 0,
							}

						# Check if the text is in the post
						try:
							textInput = post.find_element_by_css_selector('.wall_post_text')
							if textInput.text:
								localOutput['text'] = textInput.text 
						except:
							pass

						# Check if the foto is in the post
						try:
							fotoInput = post.find_element_by_css_selector('.page_post_thumb_wrap.image_cover')
							if fotoInput.get_attribute('style'):
								localOutput['image'] = fotoInput.get_attribute('style')
								localOutput['image'] = localOutput['image'][localOutput['image'].find('url(')+4:len(localOutput['image'])-2]
						
						output['content'].append(localOutput)
						except:
							pass

					else:
						break
			except:
				pass

		# If output is not empty -> send output data
		if len(output['content']) > 0:
			url = 'https://onfeedvkbot.herokuapp.com/setupdates' 
			data = json.dumps(output)
			data = data.encode("utf-8")
			request = Request(url, data)
			request.add_header('Content-Type', 'application/json')
			urlopen(request)

# Start the parser, which will turn on every n = 60 seconds
setInterval(parse, 60)