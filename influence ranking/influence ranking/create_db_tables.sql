sudo stop mysql
sudo start mysql
**************************************************
-- data set: extract 1w users' infos from the Illinois dataset 
use twitter;

-- user profile
create table twitter_user
(
  id varchar(128) not null,
  followers_count int unsigned default 0,
  listed_count int unsigned default 0, --  	The number of public lists that this user is a member of.
  utc_offset varchar(32) not null,
  statuses_count int unsigned default 0,
  description varchar(512),
  friends_count int unsigned default 0,
  location varchar(512),
  geo_enabled boolean,
  name varchar(512),
  lang varchar(64),
  favourites_count int unsigned default 0, -- The number of tweets this user has favorited in the account's lifetime. British spelling used in the field name for historical reasons. 
  screen_name varchar(512),
  created_at datetime,
  time_zone varchar(128),
  protected boolean,
  primary key(id)
)engine=innodb default charset=utf8;
ALTER TABLE twitter_user ADD INDEX index_twitteruser (id);

-- tweets
create table twitter_tweets
(
  text varchar(2048) not null,
  source_url varchar(1024),
  id varchar(128) not null,
  favorite_count int unsigned default 0,
  source varchar(1024),
  lang varchar(64),
  user_id varchar(128) not null,
  retweeted_status varchar(128),
  created_at datetime,
  retweeted boolean,
  symbols varchar(256),
  user_mentions varchar(1024),
  hashtags varchar(1024),
  urls varchar(1024),
  in_reply_to_status_id_str varchar(128),
  retweet_count int unsigned default 0,
  in_reply_to_user_id varchar(128),
  primary key(id)
)engine=innodb default charset=utf8;
ALTER TABLE twitter_tweets ADD INDEX index_twittertweets (id);
ALTER TABLE twitter_tweets ADD INDEX index_twittertweets_userid (user_id);
ALTER TABLE twitter_tweets ADD INDEX index_twittertweets_retweetid (retweeted_status);

-- retweets
create table twitter_retweets
(
  text varchar(2048) not null,
  source_url varchar(1024),
  id varchar(128) not null,
  favorite_count int unsigned default 0,
  source varchar(1024),
  lang varchar(64),
  user_id varchar(128) not null,
  created_at datetime,
  retweeted boolean,
  symbols varchar(256),
  user_mentions varchar(1024),
  hashtags varchar(1024),
  urls varchar(1024),
  in_reply_to_status_id_str varchar(128),
  retweet_count int unsigned default 0,
  in_reply_to_user_id varchar(128),
  primary key(id)
)engine=innodb default charset=utf8;
ALTER TABLE twitter_retweets ADD INDEX index_twitterretweets (id);

-- how many days' tweets are collected refering to specific users
create table user_habit
(
  user_id varchar(128) not null,
  tweet_count int unsigned default 0,
  days float default 0,
  read_habit int unsigned default 0,
  avg_total float default 0,
  primary key(user_id)
)engine=innodb default charset=utf8;

ALTER TABLE user_days ADD INDEX index_use_days (user_id);

-- count tweets by hour and week day
create table tweet_count
(
  user_id varchar(128) not null,
  week_day int unsigned default 0,
  hour int unsigned default 0,
  total_count float default 0,
  retweet_count float default 0,
  reply_count float default 0,
  primary key(user_id,week_day,hour) 
)engine=innodb default charset=utf8;

ALTER TABLE tweet_count ADD INDEX index_tweetcount (user_id);

-- count tweets by hour and week day compute the avg
create table tweet_count_avg
(
  user_id varchar(128) not null,
  week_day int unsigned default 0,
  hour int unsigned default 0,
  total_count float default 0,
  retweet_count float default 0,
  reply_count float default 0,
  primary key(user_id,week_day,hour) 
)engine=innodb default charset=utf8;

ALTER TABLE tweet_count_avg ADD INDEX index_tweetcountavg (user_id);

-- count tweets by user
create table tweet_count_user
(
  user_id varchar(128) not null,
  total_count float default 0,
  primary key(user_id)
)engine=innodb default charset=utf8;

ALTER TABLE tweet_count_user ADD INDEX index_tweetcountuser (user_id);

-- sum all of one user's friends' tweet_count
--create table friends_tweet_count
(
  user_id varchar(128) not null,
  week_day int unsigned default 0,
  hour int unsigned default 0,
  total_count float default 0,
  retweet_count float default 0,
  reply_count float default 0,
  primary key(user_id,week_day,hour) 
)engine=innodb default charset=utf8;
ALTER TABLE friends_tweet_count ADD INDEX index_frinedstweetcount (user_id);

-- 用户的所有好友发帖的总数（twitterrank实验专用）
create table friends_tweet_num
(
  user_id varchar(128) not null,
  total_count float default 0,
  primary key(user_id) 
)engine=innodb default charset=utf8;
ALTER TABLE friends_tweet_num ADD INDEX index_frinedstweetnum (user_id);

-- count tweets by hour
create table tweet_count_hour
(
  user_id varchar(128) not null,
  hour int unsigned default 0,
  total_count float default 0,
  primary key(user_id,hour)
)engine=innodb default charset=utf8;

ALTER TABLE tweet_count_hour ADD INDEX index_tweetcounthour (user_id,hour);

create table tweet_count_hour_tmp (select user_id,max(total_count) max,min(total_count) min from tweet_count_hour group by user_id);

-- count tweets by hour and normalized
create table tweet_count_hour_normalized
(
  user_id varchar(128) not null,
  hour int unsigned default 0,
  total_count float default 0,
  primary key(user_id,hour)
)engine=innodb default charset=utf8;

ALTER TABLE tweet_count_hour_normalized ADD INDEX index_tweetcounthournormalized (user_id,hour);

-- count tweets by hour divide by the amount of hours
create table tweet_count_hour_avg
(
  user_id varchar(128) not null,
  hour int unsigned default 0,
  total_count float default 0,
  primary key(user_id,hour)
)engine=innodb default charset=utf8;

ALTER TABLE tweet_count_hour_avg ADD INDEX index_tweetcounthouravg (user_id,hour);

-- count tweets by week day
create table tweet_count_day
(
  user_id varchar(128) not null,
  day int unsigned default 0,
  total_count float default 0,
  primary key(user_id,day)
)engine=innodb default charset=utf8;

ALTER TABLE tweet_count_day ADD INDEX index_tweetcountday (user_id,day);

-- relation
create table user_friend
(
  user_id varchar(128) not null,
  friend_id varchar(128) not null,
  isCollected boolean,
  primary key(user_id,friend_id)
)engine=innodb default charset=utf8;
ALTER TABLE user_friend ADD INDEX index_userfriend (user_id,friend_id);

-- count retweets delay
create table count_retweet_delay
(
  user_id varchar(128) not null,
  friend_id varchar(128) not null,
  tweet_id varchar(128) not null,
  retweet_id varchar(128) not null,
  tweet_time datetime null,
  retweet_time datetime null,
  seconds int(11) default 0,
  tweet_count int unsigned default 0
)engine=innodb default charset=utf8;

ALTER TABLE count_retweet_delay ADD INDEX index_retweetdelay (user_id,friend_id,tweet_id,retweet_id);

-- store retweets delay information, which means friend ids must be in twitter_user
create table count_retweet_delay_valid
(
  user_id varchar(128) not null,
  friend_id varchar(128) not null,
  tweet_id varchar(128) not null,
  retweet_id varchar(128) not null,
  tweet_time datetime null,
  retweet_time datetime null,
  seconds int(11) default 0,
  tweet_count int unsigned default 0
)engine=innodb default charset=utf8;

ALTER TABLE count_retweet_delay_valid ADD INDEX index_retweetdelayvalid (user_id,friend_id,tweet_id,retweet_id);

-- count reply delay
create table count_reply_delay
(
  user_id varchar(128) not null,
  friend_id varchar(128) not null,
  tweet_id varchar(128) not null,
  reply_id varchar(128) not null,
  tweet_time datetime null,
  reply_time datetime null,
  seconds int(11) default 0,
  tweet_count int unsigned default 0
)engine=innodb default charset=utf8;

ALTER TABLE count_reply_delay ADD INDEX index_replydelay (user_id,friend_id,tweet_id,reply_id);

-- store reply delay information, which means friend ids must be in twitter_user
create table count_reply_delay_valid
(
  user_id varchar(128) not null,
  friend_id varchar(128) not null,
  tweet_id varchar(128) not null,
  reply_id varchar(128) not null,
  tweet_time datetime null,
  reply_time datetime null,
  seconds int(11) default 0,
  tweet_count int unsigned default 0
)engine=innodb default charset=utf8;

ALTER TABLE count_reply_delay_valid ADD INDEX index_replydelayvalid (user_id,friend_id,tweet_id,reply_id);

create table count_reply_delay_user
(
  user_id varchar(128) not null,
  avg_sec float default 0,
  avg_count float default 0,
  primary key(user_id)
)engine=innodb default charset=utf8;

ALTER TABLE count_reply_delay_user ADD INDEX index_replydelayuser (user_id);

-- record each tweet's user_id and created time
create table user_tweet_time
(
  user_id varchar(128) not null,
  tweet_id varchar(128) not null,
  created_at int(11) default 0,
  primary key(user_id,tweet_id)
)engine=innodb default charset=utf8;

ALTER TABLE user_tweet_time ADD INDEX index_usertweettime (user_id,tweet_id);

create table count_delay
(
  user_id varchar(128) not null,
  friend_id varchar(128) not null,
  tweet_id varchar(128) not null,
  response_id varchar(128) not null,
  seconds int(11) default 0,
  tweet_count int unsigned default 0
)engine=innodb default charset=utf8;

ALTER TABLE count_delay ADD INDEX index_replydelay (user_id,friend_id,tweet_id,response_id);

-- 记录任意两个用户之间的转发时间间隔和条数间隔
create table count_delay_user
(
  user_id varchar(128) not null,
  seconds int default 0,
  tweet_count int default 0,
  primary key(user_id)
)engine=innodb default charset=utf8;

ALTER TABLE count_delay_user ADD INDEX index_delayuser (user_id);
