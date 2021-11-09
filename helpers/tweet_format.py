def format_tweet(dict):
    """
    the data dictionary from the Twitter API response  is as below: the structure of json_response --> ['data',
    'includes', 'meta']
    the structure of an item in json_response['data'] w/attachment --> ['text', 'id',
    'created_at', 'attachments']
    structure of json_response['includes'] is one dictionary with 'media' where each item has ['media_key', 'type', 'url']
    this method only picks the url and media_key from includes in json_response. not concerned with the tweet's text and creation date.
    -- this might pose an issue in the future --
    :param dict: full json_response from twitter
    :return: a list of dictionaries that only stores the url and media_key from the response
    """
    tweets = []
    for item in dict['includes']['media']:
        tweet = {}
        if item['type'] == 'photo':
            tweet['url'] = item['url']
            tweet['media_key'] = item['media_key']
        tweets.append(tweet)
    return tweets
