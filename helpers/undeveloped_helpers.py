def tweet_format(dict):
    tweets = []
    tweet = {}
    for item in dict['includes']['media']:
        if item['type'] == 'photo':
            tweet['url'] = item['url']
            tweet['media_key'] = item['media_key']
        tweets.append(tweet)

    for item in dict['data']:
        if 'attachments' in item.keys():
            for tweet in tweets:
                if tweet['media_key'] in item['attachments']['media_keys']:
                    print(item['text'])