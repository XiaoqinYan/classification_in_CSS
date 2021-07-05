bearer_token = "**************** INSERT YOUR BEARER TOKEN HERE ****************"

tweet_fields = ["text", "public_metrics", "created_at", "author_id", "geo"]

def get_user_tweets(users, 
                    bt=bearer_token,
                    tweet_fields = tweet_fields,
                    expansions = None,
                    expansion_fields = None,
                    start_time = None, 
                    end_time = None):
  
  #create a receptacle for the API's responses
  responses = []

  for user in users:

    url = "https://api.twitter.com/2/users/{}/tweets".format(user)

    #Store one's bearer token in a way legible to the Twitter API
    header = {"Authorization": "Bearer {}".format(bt)}

    #Encode the desired tweet fields in a way legible to the Twitter API
    params = {"tweet.fields": ','.join(tweet_fields)}

    #If you passed expansions, include these in the API request
    if expansions:
      params['expansions'] = ','.join(expansions)
      for exp in expansion_fields:
        params[exp] = ','.join(expansion_fields[exp])

    #If you defined a start and/or end time, add them to the API request
    if start_time:
      params['start_time'] = start_time
    if end_time:
      params['end_time'] = end_time

    #Make the actual call to the Twitter API
    response = requests.request("GET", url, headers=header, params=params)

    #If there's an error, be sure to print it out so we know what's going on
    if response.status_code != 200:
      print("Got the following error for user {0}: {1}".format(user, response.text))

    #Add the user's tweets to our receptacle
    responses.append(response.json())

  return responses

#The user IDs of my, Professor Bail's, and Professor Salginik's Twitter accounts, respectively
users = ["491278138","964635660","4509741"]

results = get_user_tweets(users, start_time="2021-06-01T00:00:01Z",
                          expansions=["author_id"],
                          expansion_fields={"user.fields": ["description"]})

#Print the most recent tweet from my account
results[0]['data'][0]
#Print my user information
results[0]['includes']
#Print the most recent tweet from Professor Bail's account
results[1]['data'][0]
#Print Professor Bail's user information
results[1]['includes']
#Print the most recent tweet from Professor Salganik's account
results[2]['data'][0]

def tweet_stream(url, header, params):
  '''
  A helper function that connects to the Twitter API's sampled stream endpoint.

  Returns a generator that yields tweets from the unfiltered spritzer stream.
  '''

  #Open the ongoing connection to the spritzer stream
  with requests.request("GET", url, headers=header, 
                        params=params, stream=True) as response:
  
    #If there was an error, print it so we know what's going on
    if response.status_code != 200:
        print("Got the following error: {}".format(response.text))

    else:

      #For each tweet that gets returned...
      for response_item in response.iter_lines():
        if response_item:
          tweet = json.loads(response_item)

          #...Pass along the tweet
          if 'includes' in tweet:
            yield {**tweet['data'], **tweet['includes']}
          else:
            yield tweet['data']


def get_streaming_tweets(bt=bearer_token,
                         tweet_fields = tweet_fields,
                         expansions = None,
                         expansion_fields = None,
                         t = None,
                         n = 100):

  #This is the base url for the sampled stream endpoint
  url = "https://api.twitter.com/2/tweets/sample/stream"

  #Store one's bearer token in a way legible to the Twitter API
  header = {"Authorization": "Bearer {}".format(bt)}

  #Encode the desired tweet fields in a way legible to the Twitter API
  params = {'tweet.fields': ','.join(tweet_fields)}

  #If you passed expansions, include these in the API request
  if expansions:
    params['expansions'] = ','.join(expansions)
    for exp in expansion_fields:
      params[exp] = ','.join(expansion_fields[exp])

  #Create a receptacle for the API's responses
  results = []

  #If you passed a time for which to be pulling from the spritzer continuously...
  if t:

    #Define the time at which you began connecting to the stream
    start = time.time()
    end = time.time()

    #Connect to the stream
    stream = tweet_stream(url, header, params)

    #Until time runs out, keep pulling tweets and append them to our receptacle
    while end-start < t:
      results.append(next(stream))
      end = time.time()
    stream.close()

  #If you passed a number of tweets to pull from the spritzer...
  elif n:

    #Connect to the stream
    stream = tweet_stream(url, header, params)

    while len(results) < n:
      results.append(next(stream))
    stream.close()
  
  else:
    raise Exception("Must define either t or n")

  return results
