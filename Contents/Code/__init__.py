YOUTUBE_VIDEO_DETAILS = 'https://www.googleapis.com/youtube/v3/videos/?id=%s&part=snippet&key=%s'
RE_YT_ID = Regex('[a-z0-9\-_]{11}', Regex.IGNORECASE)

def Start():
	HTTP.CacheTime = CACHE_1MONTH
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36'

class YouTubeAgent(Agent.Movies):
	name = 'YouTube'
	languages = [Locale.Language.NoLanguage]
	primary_provider = True

	def search(self, results, media, lang):
		filename = String.Unquote(media.filename)

		if Prefs['yt_pattern'] != '':
			try:
				yt_id = Regex(Prefs['yt_pattern']).search(filename).group('id')
			except:
				Log('Regex failed: %s\nFilename: %s' % (Prefs['yt_pattern'], filename))
				yt_id = None

			if yt_id and RE_YT_ID.search(yt_id):
				results.Append(
					MetadataSearchResult(
						id = yt_id,
						name = media.name,
						year = None,
						score = 99,
						lang = lang
					)
				)

	def update(self, metadata, media, lang):
		try:
			json_obj = JSON.ObjectFromURL(YOUTUBE_VIDEO_DETAILS % (metadata.id, Prefs['yt_apikey']))['items'][0]['snippet']
		except:
			Log('Could not retrieve data from YouTube for: %s' % metadata.id)
			json_obj = None

		if json_obj:
			metadata.originally_available_at = Datetime.ParseDate(json_obj['publishedAt']).date()

			if Prefs['yt_prependdate']:
				metadata.title = metadata.originally_available_at . ' - ' . metadata.json_obj['title']
			else:
				metadata.title = json_obj['title']

			metadata.studio = json_obj['channelTitle']
			metadata.summary = json_obj['description']

			thumb = None
			if 'high' in json_obj['thumbnails']:
				thumb = json_obj['thumbnails']['high']['url']
			elif 'standard' in json_obj['thumbnails']:
				thumb = json_obj['thumbnails']['standard']['url']

			if thumb:
				poster = HTTP.Request(thumb)
				metadata.posters[thumb] = Proxy.Preview(poster, sort_order=1)
