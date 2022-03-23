***********************************
delay and trace-back analysis
***********************************
create new tables: count_retweet_delay、count_retweet_delay_valid、count_reply_delay、count_reply_delay_valid
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
***********************************
1:retweet internal analysis
**********************************************************************
mysql> insert into count_retweet_delay (select t.user_id as user_id, rt.user_id as friend_id, t.id as tweet_id, rt.id as retweet_id, t.created_at as tweet_time, rt.created_at as retweet_time, UNIX_TIMESTAMP(t.created_at)-UNIX_TIMESTAMP(rt.created_at) as seconds, 0 from twitter_tweets t, twitter_retweets rt where t.retweeted_status=rt.id);

Query OK, 600943 rows affected (55 min 16.53 sec)
Records: 600943  Duplicates: 0  Warnings: 0

# friend's id must in twitter_user(extract valid users for response study):
mysql> insert into count_retweet_delay_valid (select * from count_retweet_delay where friend_id in (select id from twitter_user));

# check reply users are not in user_friend (supplement these users to friends):
mysql> insert ignore into user_friend (select user_id, friend_id, 1 from count_retweet_delay);

Note" tweet_count column need to execute: count_reply_delay.py to calculate and insert into the table
***********************************

# an example of count_retweet_delay:
mysql> select * from count_retweet_delay where tweet_count=441100;
+----------+-----------+--------------------+--------------------+---------------------+---------------------+---------+-------------+
| user_id  | friend_id | tweet_id           | retweet_id         | tweet_time          | retweet_time        | seconds | tweet_count |
+----------+-----------+--------------------+--------------------+---------------------+---------------------+---------+-------------+
| 20192882 | 104580839 | 423949539930673152 | 414970414264115200 | 2014-01-16 22:47:01 | 2013-12-23 04:07:11 | 2140790 |      441100 |
+----------+-----------+--------------------+--------------------+---------------------+---------------------+---------+-------------+

**********************************************************************
2:reply internal analysis
**********************************************************************
the number of replies in the dataset:
mysql> select count(*) from twitter_tweets where in_reply_to_status_id_str != 'null';
+----------+
| count(*) |
+----------+
|   792390 |
+----------+
mysql> insert ignore into count_reply_delay (select tt1.user_id as user_id, tt2.user_id as friend_id, tt1.id as tweet_id, tt2.id as reply_id, tt1.created_at as tweet_time, tt2.created_at as reply_time,UNIX_TIMESTAMP(tt1.created_at)-UNIX_TIMESTAMP(tt2.created_at) as seconds,0 from twitter_tweets tt1, twitter_tweets tt2 where tt1.in_reply_to_status_id_str=tt2.id);

# friend's id needs to be in twitter_user (for reply prediction study）：
mysql> insert into count_reply_delay_valid (select * from count_reply_delay where friend_id in (select id from twitter_user));

# check what uers are not in user_friend:
mysql> insert ignore into user_friend (select user_id, friend_id, 1 from count_reply_delay);

Note: tweet_count column needs to run count_reply_delay.py to calculate and insert
***********************************
