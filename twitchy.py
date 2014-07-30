import praw, HTMLParser, json, requests, re, time
from config import username, password, subreddit, twitchgame, streamnum
from PIL import Image
from StringIO import StringIO

def get_stream_list(subreddit, twitchgame, streamnum):
	# meta-request, channel data are ranked by the amount of cur. viewers
	livestreams = []
	api_link = "http://api.justin.tv/api/stream/list.json?meta_game=" + twitchgame
	livestreams = get_stream_info(api_link, livestreams)
	results, preview_images = parse_stream_info(livestreams, streamnum)
	return results, preview_images


def get_stream_info(api_link,livestreams):
	# This checks that there was any data received in the chunk, and if there was, it appends it to livestreams list.
	try:
		data = requests.get(api_link).json()
		if len(data):
			livestreams.append(data)
	except ValueError:
		pass
	# Get the JSON data from our api request.
	return livestreams


def parse_stream_info(livestreams, streamnum):
	# Formats the stream info (if there was any received) to be posted to the reddit sidebar. 
	# Also prepares the thumbnail urls to be put into a spritesheet. 
	results, n, thumbnail_urls, preview_images= [], 0, [], []

	# If it doesn't contain anything (meaning there are no current live streams), 
	# append results with the no streams are live string. 
	if not len(livestreams) or streamnum == 0:
		results.append(">No streams are currently live.\n") 
	else:
		for streamer_list in livestreams: 
		# Looping through the JSON structure 
			for streamer_info_dict in streamer_list:
					if n == streamnum:
						break
				# Set title to the stream title 
					title = streamer_info_dict["title"]
				# Removing characters that can break reddit formatting
					title = re.sub(r'[*)(>/#\[\]]', '', title)
					title = title.replace("\n", "")
				# If the title's length is  more than 30 chars, only use the first 30 for the title on reddit, 
				# then add on some elipises or whatever the fuck they're called
					name = streamer_info_dict["channel"]["login"]
					if (len(title) >= 33):
						title = title[0:30] + "..." 
				# Formats the viewercount to add commas like: 1,000 
					viewercount = "{:,}".format(streamer_info_dict["channel_count"])
				# Appending the thumbnail url to a list to use later 
					thumbnail_urls.append(streamer_info_dict["channel"]["screen_cap_url_huge"]) # can be small, medium, larger or huge
				# Constructing the final string we'll post to the reddit sidebar
					results.append("> " + "\n" + str(n) + ". " + "**[" + title + "](http://twitch.tv/" + name + ")**" + "[" + "\n" + ">" + name + "](http://twitch.tv/" + name + ")" + "\n")
					# org. results.append("> " + "\n" + "> " + "\n" + str(n) + ". " + "**[" + name + "](http://twitch.tv/" + name + ")**" + "\n" + "[" + " \- " + title + "](http://twitch.tv/" + name + ")" + "\n") 
					n += 1
				# n is used above in the final string to make it an ordered list 1. 2. 3., etc.

	for url in thumbnail_urls:
		preview_data = requests.get(url).content
		# Download image
		preview_img = Image.open(StringIO(preview_data))
		# Convert to PIL Image
		preview_images.append(preview_img)
		# Add image to preview_images list
	return results, preview_images
	# Return the results (the list of strings we'll post to the sidebar), and the preview_images which are the thumbnail images

def create_spritesheet(thumblist):
	# Puts the thumbnail images into a spritesheet.
	w, h = 255, 143 * (len(thumblist) or 1)
	spritesheet = Image.new("RGB", (w, h))
	xpos = 0
	ypos = 0
	res = (255,143)
	for img in thumblist:
		bbox = (xpos, ypos)
		img = img.resize(res, Image.ANTIALIAS) #shrinks image and changes the aspect ratio to 16:9
		spritesheet.paste(img,bbox)
		ypos = ypos + 143 
		# Increase ypos by 143 pixels (move down the image by 143px)
		# so we can place the image in the right position next time this loops.)
	spritesheet.save("thumbnails/img.png") 
	# Save it as img.png in thumbnails folder

if __name__ == "__main__":
	reddit = praw.Reddit("Twitch.tv sidebar bot for " + subreddit + " by /u/andygmb") #log into reddit
	reddit.login(username=username, password=password)
	subreddit = reddit.get_subreddit(subreddit)
	results, preview_images = get_stream_list(subreddit, twitchgame=twitchgame, streamnum=streamnum)

	if results != ['**No streams are currently live.**\n']:
		create_spritesheet(preview_images)
		subreddit.upload_image("thumbnails/img.png", "img", False)
		stylesheet = reddit.get_stylesheet(subreddit)
		stylesheet = HTMLParser.HTMLParser().unescape(stylesheet["stylesheet"])
		subreddit.set_stylesheet(stylesheet, prevstyle=None) 
		# set the stylesheet as the stylesheet we just copied. We have to do this because otherwise the thumbnail images we just uploaded 
		# would not refresh on reddit's server side, because for some reason they are cached untill you save the stylesheet.
		sidebar = reddit.get_settings(subreddit)
		desc = HTMLParser.HTMLParser().unescape(sidebar['description'])
		try:
			startmarker, endmarker = desc.index("[](#TwitchStartMarker)"), desc.index("[](#TwitchEndMarker)") + len("[](#TwitchEndMarker)")
			stringresults = "".join(results)
			desc = desc.replace(desc[startmarker:endmarker], "[](#TwitchStartMarker)" + "\n \n" + stringresults + "\n \n" + "[](#TwitchEndMarker)")
			subreddit.update_settings(description=desc.encode('utf8'))
		except:
			pass
	else:
		sidebar = reddit.get_settings(subreddit)
		desc = HTMLParser.HTMLParser().unescape(sidebar['description'])
		try:
			startmarker, endmarker = desc.index("[](#TwitchStartMarker)"), desc.index("[](#TwitchEndMarker)") + len("[](#TwitchEndMarker)")
			stringresults = "".join(results)
			desc = desc.replace(desc[startmarker:endmarker], "[](#TwitchStartMarker)" + "\n \n" + stringresults + "\n \n" + "[](#TwitchEndMarker)")
			subreddit.update_settings(description=desc.encode('utf8'))
		except:
			pass
