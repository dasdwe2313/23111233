from youtubesearchpython import VideosSearch

def search_youtube(query):
    videosSearch = VideosSearch(query, limit=1)
    result = videosSearch.result()
    if result['result']:
        return result['result'][0]['link']
    return None
