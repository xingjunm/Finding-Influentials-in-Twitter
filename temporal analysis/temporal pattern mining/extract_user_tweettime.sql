## user_tweet_time 
-- record each tweet's user_id and created time
create table user_tweet_time
(
  user_id varchar(128) not null,
  tweet_id varchar(128) not null,
  created_at int(11) default 0,
  primary key(user_id,tweet_id)
)engine=innodb default charset=utf8;

ALTER TABLE user_tweet_time ADD INDEX index_usertweettime (user_id,tweet_id);

mysql> insert ignore into user_tweet_time (select user_id, id as tweet_id, UNIX_TIMESTAMP(created_at) as created_at from twitter_tweets);
