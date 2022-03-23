###### delete users whose does have a 'following' relationship with the other users
mysql> select distinct A.id  from twitter_user A where id not in (select distinct user_id as id from user_friend) and id not in (select distinct friend_id as id from user_friend);
mysql> delete from twitter_user where id not in (select distinct user_id as id from user_friend) and id not in (select distinct friend_id as id from user_friend);
###### delete users who have ever published less than 20 tweets

insert ignore into tweet_count_user (select user_id, sum(total_count) as total_count from tweet_count group by user_id)
mysql> select distinct user_id from tweet_count where user_id not in (select distinct(id) as id from twitter_user)
459

	###### delete users whose profile is not collected successfully
	mysql> delete from tweet_count where user_id not in (select distinct(id) as id from twitter_user);
	mysql> delete from tweet_count_user where user_id not in (select distinct(id) as id from twitter_user);

mysql> select count(*) from tweet_count_user where total_count>20;
+----------+
| count(*) |
+----------+
|     7230 |
+----------+
1 row in set (0.00 sec)
mysql> delete from tweet_count_user where total_count <20;
mysql> delete from tweet_count where user_id not in (select distinct(user_id) as id from tweet_count_user);

###### ..............
delete from twitter_user where id not in (select distinct(user_id) as id from tweet_count_user);
delete from user_friend where user_id not in (select distinct(id) as id from twitter_user) or friend_id not in (select distinct(id) as id from twitter_user);
delete from twitter_tweets where user_id not in (select distinct(id) as id from twitter_user);
delete from twitter_retweets where user_id not in (select distinct(id) as id from twitter_user);
***********************************
##### check the remaining users and tweets
***********************************
mysql> select count(*) from twitter_user;

7247

mysql> select count(*) from twitter_tweets;

3541214

mysql> select count(*) from twitter_tweets where retweeted_status != 'null';

600943

mysql> select count(*) from twitter_retweets;

569863

mysql> select sum(retweet_count) from tweet_count;

600943

mysql> select sum(reply_count) from tweet_count;

787688
