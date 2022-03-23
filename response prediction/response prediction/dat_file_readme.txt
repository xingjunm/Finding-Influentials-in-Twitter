### user_info.dat
user features
format:
[user_id]	[followers_count]	[friends_count]	[followers_count/friends_count]	[listed_count]	[favourites_count]	[statuses_count]

### links.dat
link file, saves all relations used to generate the training dataset
format:
[friend_id]	[user_id]

### user_tweets.dat
tweets retweeted at least once
format:
[user_id]	[tweet_id]	[hour]
Note: hour is the tweet published hour (hour of the time)

### retweets.dat
rewteeted tweets, difference to user_tweets.dat: this file saves all the retweet relationship
if a tweet from user_tweets.dat is retweeted by two users, then there will be two records
format:
[user_id]	[friend_id]	[tweet_id]	[retweet_id]	[tweet_hour]	[retweet_hour]
Note: the hour in tweet_hour,retweet_hour和user_tweets.dat share the same meaning

### i-j-cosine.dat
user i vs. j temporal cosine distance
format:
[friend_id]	[user_id]	[cosine]

### i-j-ratio.dat
tweet count of user j/user i's all friends tweet sum count
format:
[user_i]	[user_j]	[ratio]

### timeSeries.dat
normalized variation of user's tweets number across hours
format:
[user_i]	[0 1 2 ... 23]

### cosine-sim.dat
user-user topic consine similarity
format:
[friend_id]	[user_id]	[cosine]
