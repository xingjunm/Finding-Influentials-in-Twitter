***********************************
simple statistical analysis
store tweets into database: store_tweets_to_db.py
preprocessing-1：delete invalid users
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
# total number of users:
mysql> select count(*) from twitter_user;
7247
# total number of tweets (including reply and retweet)
mysql> select count(*) from twitter_tweets;
3541214
# total number of retweets
mysql> select count(*) from twitter_tweets where retweeted_status != 'null';
600943
mysql> select count(*) from twitter_retweets;
569863 (in fact there are only 600943 retweets, meaning there are 31080 duplicate tweeets)
mysql> select sum(retweet_count) from tweet_count;
600943
# total number of replies
mysql> select sum(reply_count) from tweet_count;
787688
***********************************
user activity analysis
***********************************
# create a new table: user_tweet_time to record the user_id and tweet time for tweets
# this is becaue working on twitter_tweets is too time-consuming
mysql> insert ignore into user_tweet_time (select user_id, id as tweet_id, UNIX_TIMESTAMP(created_at) as created_at from twitter_tweets);
mysql> 
# create an assistant script
# compute homeline and display line: extract_user_home_display_line.py
# compute user/s collection time interval and number of tweets collected during the intervel: count_user_habit.py
## averaging tweet_count table and store into table: tweet_count_avg
## 	for uers with < 3200 tweets:
## 	mysql> insert ignore into tweet_count_avg (select * from tweet_count);
## 	mysql> update tweet_count_avg set total_count=total_count/4.0,retweet_count=retweet_count/4.0,reply_count=reply_count/4.0 where user_id in (select user_id from user_habit where tweet_count<3200);

## 	for uers = 3200 tweets:
## 	mysql> UPDATE tweet_count_avg INNER JOIN user_habit ON tweet_count_avg.user_id=user_habit.user_id SET total_count=total_count/days*7.0,retweet_count=retweet_count/days*7.0,reply_count=reply_count/days*7.0 WHERE user_habit.tweet_count=3200;

--(1)9541 users with 3560513 tweets, with each user post 373.2tweets/30days=12.44tweet/day
	##mysql> select count(*) from (select user_id,sum(total_count) count from tweet_count group by user_id) tmp where count=3200;
	##user with the most tweets: 131 users have 3200 tweets (this number is the upper limit of twitter API)
	##mysql> select user_id,sum(total_count) count from tweet_count group by user_id order by count;
	##mysql> select count(*) from (select user_id,sum(total_count) count from tweet_count group by user_id) tmp where count=1;
	##user with the least tweets: 131 users have only 1 tweet
(2)hourly/daily analysis - preprocessing:
	hourly tweets number (then save to new table):
	mysql> insert into tweet_count_hour (select user_id,hour,sum(total_count) as total_count from tweet_count group by user_id,hour);
	mysql> insert into tweet_count_hour_avg (select * from tweet_count_hour);
	preprocessing-2: taking average
# for uers = 3200 tweets:
mysql> update tweet_count_hour_avg set total_count=total_count/30.0 where user_id in (select distinct user_id from user_habit where tweet_count<3200);
mysql> UPDATE tweet_count_hour_avg INNER JOIN user_habit ON tweet_count_hour_avg.user_id=user_habit.user_id SET total_count=total_count*1.0/days WHERE user_habit.tweet_count=3200;
	
# normalization based on users
mysql> create table tweet_count_hour_tmp (select user_id,max(total_count) max,min(total_count) min from tweet_count_hour group by user_id);
mysql> insert into tweet_count_hour_normalized (select * from tweet_count_hour);(这个地方用tweet_count_hour_avg也可以)
mysql> UPDATE tweet_count_hour_normalized LEFT JOIN tweet_count_hour_tmp ON tweet_count_hour_normalized.user_id=tweet_count_hour_tmp.user_id SET total_count=total_count/max;
	
## 	Monday - Sunday: the numbe of tweets (then save to a new table):
## 	mysql> insert ignore into tweet_count_day (select user_id,week_day,sum(total_count) as total_count from tweet_count group by user_id,week_day);
#for uers with < 3200 tweets:
mysql> update tweet_count_day set total_count=total_count/4.0 where user_id in (select distinct user_id from user_habit where tweet_count<3200);
mysql> UPDATE tweet_count_day INNER JOIN user_habit ON tweet_count_day.user_id=user_habit.user_id SET total_count=total_count*1.0/days*7.0 WHERE user_habit.tweet_count=3200;
(3)hourly，average tweet number：
sum of all users（not average, but has the same effect):
mysql> select hour,sum(total_count) as total from tweet_count_hour_avg group by hour;
+------+--------------------+
| hour | total              |
+------+--------------------+
|    0 |  7313.294067233801 |
|    1 |   7538.63975404948 |

24 rows in set (0.08 sec)

# (4) week day analysis
mysql> select day,sum(total_count) as total from tweet_count_day group by day;

+-----+--------------------+
| day | total              |
+-----+--------------------+
|   0 | 138474.47848510742 |
|   1 | 159518.15475463867 |
|   2 | 161019.51110839844 |
|   3 | 141512.39572143555 |
|   4 | 128811.78109359741 |
|   5 | 106577.09986114502 |
|   6 | 112438.70467853546 |
+-----+--------------------+

(5) users with min/max difference (hourly)：
mysql> create table tweet_count_hour_tmp (select user_id,max(total_count) max,min(total_count) min from tweet_count_hour_avg group by user_id);
mysql> select max(max-min) from tweet_count_hour_tmp;
65.07137298583984
mysql> select * from tweet_count_hour_tmp where max-min=65.07137298583984;
	+----------+---------+-----------+
	| user_id  | max     | min       |
	+----------+---------+-----------+
	| 94140566 | 65.0714 | 0         |
	+----------+---------+-----------+

# user activity curve:
mysql> select * from tweet_count_hour_avg where user_id='85342396';
+----------+------+-------------+
| user_id  | hour | total_count |
+----------+------+-------------+
| 94140566 |    1 |   0.0351927 |
| 94140566 |    2 |    0.211156 |
| 94140566 |   11 |     2.25234 |
| 94140566 |   12 |     37.7618 |
| 94140566 |   13 |     65.0714 |
| 94140566 |   14 |     1.37252 |
| 94140566 |   22 |     2.95619 |
| 94140566 |   23 |     2.95619 |
+----------+------+-------------+

mysql> select name,screen_name from twitter_user where id='94140566';
+------------------+-------------+
| name             | screen_name |
+------------------+-------------+
| Eric B. Thomasma | seams16     |
+------------------+-------------+

mysql> select min(max-min) from tweet_count_hour_tmp;
0
mysql> select count(*) from tweet_count_hour_tmp where max-min=0;
351个用户在每个小时的发帖数相等(这些用户大都是在部分小时都发了0条tweet)

(6) users with min/max difference(daily)：
mysql> create table tweet_count_day_tmp (select user_id,max(total_count) max,min(total_count) min from tweet_count_day group by user_id);
mysql> select max(max-min) from tweet_count_day_tmp;
818.4181537628174
mysql> select * from tweet_count_day_tmp where max-min=818.4181537628174;
+----------+---------+---------+
| user_id  | max     | min     |
+----------+---------+---------+
| 61661638 | 827.445 | 9.02667 |
+----------+---------+---------+
这个用户的曲线图：
mysql> select * from tweet_count_day where user_id='61661638';
+----------+-----+-------------+
| user_id  | day | total_count |
+----------+-----+-------------+
| 61661638 |   0 |     410.212 |
| 61661638 |   1 |     827.445 |
| 61661638 |   2 |     817.415 |
| 61661638 |   3 |     718.122 |
| 61661638 |   4 |     149.442 |
| 61661638 |   5 |     277.821 |
| 61661638 |   6 |     9.02667 |
+----------+-----+-------------+
7 rows in set (0.00 sec)

mysql> select min(max-min) from tweet_count_day_tmp;
0
mysql> select count(*) from tweet_count_day_tmp where max-min=0;
301个用户在一周的每一天里发帖没有差别,主要是他们发帖的数量很少，而且仅仅集中在某一天,如：
mysql> select *  from tweet_count_day where user_id='101573945';
+-----------+-----+-------------+
| user_id   | day | total_count |
+-----------+-----+-------------+
| 101573945 |   3 |         0.5 |
+-----------+-----+-------------+
1 row in set (0.00 sec)
用户101573945平均每周3发帖0.5条，实际上他在一个月的时间里只是在某周3发了两条微博
(7)用户间的这种规律，对用户之间消息共享影响大么？
	(7.1)变化最大的用户(按小时)：94140566
	此用户的好友中发帖最多的是：
	预处理：每个人平均每天发帖总数（将数据保存到新的数据库表中哦～～）：
	mysql> select user_id,max(count) from (select user_id,sum(total_count) as count from tweet_count_hour group by user_id) A;
	+----------+------------------+
	| user_id  | max(count)       |
	+----------+------------------+
	| 10003492 | 567.066333770752 |
	+----------+------------------+

	mysql> select user_id,friend_id from user_friend where user_id='10003492'
+----------+-----------+
| user_id  | friend_id |
+----------+-----------+
| 10003492 | 1035491   |
| 10003492 | 10419     |
| 10003492 | 12241152  |
| 10003492 | 12522     |
| 10003492 | 12536272  |
| 10003492 | 12611642  |
| 10003492 | 13520532  |
| 10003492 | 14502070  |
| 10003492 | 14551761  |
| 10003492 | 14589191  |
| 10003492 | 14702746  |

随便选择一个好友查询此好友的发帖规律：1035491
这个用户的曲线图：
mysql> select * from tweet_count_hour where user_id='1035491';
+---------+------+-------------+
| user_id | hour | total_count |
+---------+------+-------------+
| 1035491 |    0 |    0.392857 |
| 1035491 |    1 |    0.321429 |
| 1035491 |    2 |    0.607143 |
| 1035491 |    3 |    0.678571 |
| 1035491 |    4 |    0.178571 |
| 1035491 |    5 |    0.214286 |
| 1035491 |    6 |    0.285714 |
| 1035491 |   10 |   0.0714286 |
| 1035491 |   11 |    0.107143 |
| 1035491 |   12 |    0.214286 |
| 1035491 |   13 |    0.357143 |
| 1035491 |   14 |    0.357143 |
| 1035491 |   15 |     1.14286 |
| 1035491 |   16 |    0.785714 |
| 1035491 |   17 |     1.35714 |
| 1035491 |   18 |    0.928571 |
| 1035491 |   19 |    0.964286 |
| 1035491 |   20 |     1.14286 |
| 1035491 |   21 |    0.714286 |
| 1035491 |   22 |     1.21429 |
| 1035491 |   23 |    0.535714 |
+---------+------+-------------+

与用户 10003492 的发帖规律进行比较：
+----------+------+-------------+
| user_id  | hour | total_count |
+----------+------+-------------+
| 10003492 |    2 |   0.0357143 |
| 10003492 |    3 |        0.25 |
| 10003492 |    4 |   0.0357143 |
| 10003492 |   14 |    0.428571 |
| 10003492 |   15 |    0.357143 |
| 10003492 |   16 |    0.321429 |
| 10003492 |   17 |    0.357143 |
| 10003492 |   18 |   0.0714286 |
| 10003492 |   19 |    0.142857 |
| 10003492 |   20 |        0.25 |
| 10003492 |   21 |    0.142857 |
+----------+------+-------------+
曲线图比较略...
***********************************
延迟和回溯统计分析
***********************************
retweet时间间隔统计
mysql> insert into count_retweet_delay (select t.user_id as user_id, rt.user_id as friend_id, t.id as tweet_id, rt.id as retweet_id, t.created_at as tweet_time, rt.created_at as retweet_time, UNIX_TIMESTAMP(t.created_at)-UNIX_TIMESTAMP(rt.created_at) as seconds, 0 from twitter_tweets t, twitter_retweets rt where t.retweeted_status=rt.id);
Query OK, 600943 rows affected (55 min 16.53 sec)
Records: 600943  Duplicates: 0  Warnings: 0

好友的id也要在twitter_user中的（retweet预测专用）：
mysql> insert into count_retweet_delay_valid (select * from count_retweet_delay where friend_id in (select id from twitter_user));
查看回复关系中有哪些不在user_friend中：
mysql> insert ignore into user_friend (select user_id, friend_id, 1 from count_retweet_delay);

tweet_count字段的值需要执行：count_reply_delay.py來单独计算并且入库

***********************************
转发微博数（理论上跟‘简单统计’中的数量一致）：
mysql> select count(*) from count_retweet_delay;
603590
	最大时间间隔： 
	mysql> select max(seconds) from count_retweet_delay;
	246045843
	最大条数间隔：
	mysql> select max(tweet_count) from count_retweet_delay;
	441100
经差此用户在2014年转发了一条2006年的tweet，这两个帐号可能属于同一个人:
mysql> select * from count_retweet_delay where seconds=246045843;
+----------+-----------+--------------------+------------+---------------------+---------------------+-----------+-------------+
| user_id  | friend_id | tweet_id           | retweet_id | tweet_time          | retweet_time        | seconds   | tweet_count |
+----------+-----------+--------------------+------------+---------------------+---------------------+-----------+-------------+
| 14433841 | 24        | 420214119116333056 | 42         | 2014-01-06 15:23:47 | 2006-03-21 21:19:44 | 246045843 |      170504 |
+----------+-----------+--------------------+------------+---------------------+---------------------+-----------+-------------+

mysql> select * from count_retweet_delay where tweet_count=441100;
+----------+-----------+--------------------+--------------------+---------------------+---------------------+---------+-------------+
| user_id  | friend_id | tweet_id           | retweet_id         | tweet_time          | retweet_time        | seconds | tweet_count |
+----------+-----------+--------------------+--------------------+---------------------+---------------------+---------+-------------+
| 20192882 | 104580839 | 423949539930673152 | 414970414264115200 | 2014-01-16 22:47:01 | 2013-12-23 04:07:11 | 2140790 |      441100 |
+----------+-----------+--------------------+--------------------+---------------------+---------------------+---------+-------------+


最小时间间隔：
mysql> select min(seconds) as min_s,min(tweet_count) as min_t from count_retweet_delay;
+-------+-------+
| min_s | min_t |
+-------+-------+
|     0 |     0 |
+-------+-------+
1 row in set (0.34 sec)

转发间隔超过1天的数量：
mysql> select count(*) from count_retweet_delay where seconds>=86400;
+----------+
| count(*) |
+----------+
|    38717 |
+----------+
所占比例为：38717/603590=6.4% 这个比例有点大，不能忽略不考虑。

转发条数间隔超过200条的数量：
mysql> select count(*) from count_retweet_delay where tweet_count<200;
508260
508260/603590=84.2%

参与转发的用户总数：
mysql> select count(distinct user_id) from count_retweet_delay ;
6426
平均时间,条数间隔：
mysql> select sum(seconds)/603590 as sec, sum(tweet_count)/603590 as num from count_retweet_delay;
+-------------+----------+
| sec         | num      |
+-------------+----------+
| 154493.5779 | 663.8068 |
+-------------+----------+

154493 = 42小时（可参考性并不高）,21522.5746条（可参考性也不高）

80%时间间隔：平均时间很大（因为某些用户会在14年转发06年的tweet，初步猜测这是同一个用户）
mysql> select seconds from count_retweet_delay order by seconds limit 482872,1;
+---------+
| seconds |
+---------+
|    9140 |
+---------+
80%的用户在2.5个小时内完成转发
80%条数间隔
mysql> select tweet_count from count_retweet_delay order by tweet_count limit 482872,1;
+-------------+
| tweet_count |
+-------------+
|         104 |
+-------------+

80%的用户在界面上刷新过104条微博之前完成转发

由此可见用户平均在534秒=8.9分钟转发他所关注用户的微博。每个用户平均转发微博和原微博期间收到4条微博。整体的分布很值得做个曲线图分析一下看看属于什么分布：推测是长尾分布。

按照retweet时间间隔排序，作出分布曲线图：
--mysql> select count(*) from count_retweet_delay_valid where seconds<=10;
--mysql> select count(*) from count_retweet_delay_valid where seconds>10 and seconds<=100;
mysql> select count(*) from count_retweet_delay where seconds<=10;
mysql> select count(*) from count_retweet_delay where seconds>10 and seconds<=100;
1	10		100		1000	10000	100000	1000000		>1000000

15	9696	137072	205238	132790	81630	26600		7902

按照retweet条数间隔排序，作出分布曲线图：
mysql> select count(*) from count_retweet_delay where tweet_count<=10;
mysql> select count(*) from count_retweet_delay where tweet_count>10 and tweet_count<=100;
10		100		1000	10000	100000	1000000		>1000000

367243	114240	76931	37218	7650	308		0

计算每个用户的平均转发时间：
mysql> create table count_retweet_delay_user (select user_id, sum(seconds)/count(*) as avg_sec, sum(tweet_count)/count(*) as avg_count from count_retweet_delay group by user_id);
mysql> alter table count_retweet_delay_user add index index_retweetdelayuser(user_id);
mysql> select count(*) from count_retweet_delay_user where avg_sec<=3600;
1474
mysql> select count(*) from count_retweet_delay_user where avg_count<=200;
1426
平均转发间隔在24小时内的用户数：
mysql> select count(*) from count_retweet_delay_user where sum/count<=3600*24;
+----------+
| count(*) |
+----------+
|     5026 |
+----------+
5026/6426 = 78.2%
结论：对每个用户来说，能很快对每个用户作出反映是不可能的。每个用户对其他某一个特定用户都有一个平均转发间隔。计算每个用户对他所有关注者的转发求平均是没有意义的。
于是计算：A --- B 的转发间隔(同时用户A和B都在我们的数据集中)：
mysql> create table count_retweet_delay_AB (select user_id as user_id,tu.id as friend_id,count(*) as count,sum(seconds)as sum, sum(tweet_count) as tweet_count,sum(seconds)/count(*) as avg,sum(tweet_count)/count(*) as avg_count from count_retweet_delay crd, twitter_user tu where crd.friend_id=tu.id group by user_id,tu.id);
mysql> select count(*) from count_retweet_delay_AB;
+----------+
| count(*) |
+----------+
|     8170 |
+----------+

按照平均retweet间隔排序，作出分布曲线图：
mysql> select count(*) from count_retweet_delay_AB where avg<=10;
mysql> select count(*) from count_retweet_delay_AB where avg>10 and avg<=100;

时间间隔按照10^n进行统计（s）：
10	100		1000	10000	100000	1000000	>1000000

66	1734	3073	1917	1040	278		62

下面分析一个特定的用户（寻找转发最多的用户）：
mysql> select max(count) from (select user_id,count(friend_id) as count from count_retweet_delay_AB group by user_id) A;
42
mysql> select user_id from (select user_id,count(friend_id) as count from count_retweet_delay_AB group by user_id) A where count=42;
18038429

mysql> select * from count_retweet_delay_AB where user_id=18038429;
查看用户100042133对不同的friend转发间隔分布情况：
+----------+-----------+-------+--------+------------+
| user_id  | friend_id | count | sum    | avg        |
+----------+-----------+-------+--------+------------+
| 18038429 | 10252962  |     3 |   2190 |   730.0000 |
| 18038429 | 108764706 |     1 |    108 |   108.0000 |
| 18038429 | 125695974 |     5 |   4417 |   883.4000 |
| 18038429 | 14085040  |     2 |  25426 | 12713.0000 |
| 18038429 | 14173315  |     6 |    440 |    73.3333 |
| 18038429 | 1429761   |     2 |     80 |    40.0000 |
| 18038429 | 14956372  |     2 |    930 |   465.0000 |
| 18038429 | 14957318  |     2 |   1263 |   631.5000 |
| 18038429 | 15391102  |    19 |  23514 |  1237.5789 |
| 18038429 | 15535860  |     4 |    809 |   202.2500 |
| 18038429 | 15651634  |     5 |    350 |    70.0000 |
| 18038429 | 15652540  |     8 |  10629 |  1328.6250 |
| 18038429 | 15694286  |     2 |    167 |    83.5000 |
| 18038429 | 15791186  |     7 |   2541 |   363.0000 |
| 18038429 | 15933690  |     2 |    163 |    81.5000 |
| 18038429 | 16061631  |     1 |    290 |   290.0000 |
| 18038429 | 16247383  |     2 |     78 |    39.0000 |
| 18038429 | 16425419  |     1 |     54 |    54.0000 |
| 18038429 | 16664681  |     2 |     90 |    45.0000 |
| 18038429 | 16960812  |     3 | 182442 | 60814.0000 |
| 18038429 | 17028405  |     1 |     87 |    87.0000 |
| 18038429 | 17387823  |    11 |   2957 |   268.8182 |
| 18038429 | 18375327  |    11 |   1897 |   172.4545 |
| 18038429 | 18999261  |     1 |    365 |   365.0000 |
| 18038429 | 19151000  |    26 |  24175 |   929.8077 |
| 18038429 | 1917731   |     2 |    371 |   185.5000 |
| 18038429 | 21094888  |     3 |    277 |    92.3333 |
| 18038429 | 220086346 |     1 |     21 |    21.0000 |
| 18038429 | 22214972  |     3 |     93 |    31.0000 |
| 18038429 | 23407415  |     4 |    745 |   186.2500 |
| 18038429 | 25969442  |     1 |  11326 | 11326.0000 |
| 18038429 | 26514376  |     1 |    173 |   173.0000 |
| 18038429 | 274260620 |     3 |    203 |    67.6667 |
| 18038429 | 28785486  |    11 | 107691 |  9790.0909 |
| 18038429 | 29268287  |     2 |  21746 | 10873.0000 |
| 18038429 | 39091563  |     1 |   6356 |  6356.0000 |
| 18038429 | 41501555  |     1 |  18573 | 18573.0000 |
| 18038429 | 4170491   |     2 |     96 |    48.0000 |
| 18038429 | 47751940  |     6 |   1585 |   264.1667 |
| 18038429 | 5392522   |     2 |    834 |   417.0000 |
| 18038429 | 8940342   |     2 |   3247 |  1623.5000 |
| 18038429 | 9648652   |     2 |    659 |   329.5000 |
+----------+-----------+-------+--------+------------+

mysql> select count(*) from count_retweet_delay_AB where user_id=18038429 and avg <=3600;
+----------+
| count(*) |
+----------+
|       35 |
+----------+
该用户对42个人的转发间隔中对其中35人的平均转发间隔小于3600秒（1小时）
**********************************************************************
reply时间间隔统计
**********************************************************************
在采集到的数据集中，reply的数量：
mysql> select count(*) from twitter_tweets where in_reply_to_status_id_str != 'null';
+----------+
| count(*) |
+----------+
|   792390 |
+----------+
mysql> insert ignore into count_reply_delay (select tt1.user_id as user_id, tt2.user_id as friend_id, tt1.id as tweet_id, tt2.id as reply_id, tt1.created_at as tweet_time, tt2.created_at as reply_time,UNIX_TIMESTAMP(tt1.created_at)-UNIX_TIMESTAMP(tt2.created_at) as seconds,0 from twitter_tweets tt1, twitter_tweets tt2 where tt1.in_reply_to_status_id_str=tt2.id);

好友的id也要在twitter_user中的（reply预测专用）：
mysql> insert into count_reply_delay_valid (select * from count_reply_delay where friend_id in (select id from twitter_user));

查看回复关系中有哪些不在user_friend中：
mysql> insert ignore into user_friend (select user_id, friend_id, 1 from count_reply_delay);

tweet_count字段的值需要执行：count_reply_delay.py來单独计算并且入库


回复微博数（理论上跟‘简单统计’中的数量一致）：
mysql> select count(*) from count_reply_delay;
27145
按照reply时间间隔排序，作出分布曲线图：
mysql> select count(*) from count_reply_delay where seconds<=10;
mysql> select count(*) from count_reply_delay where seconds>10 and seconds<=100;
1	10		100		1000	10000	100000	1000000		>1000000
0	74		8327	10973	4758	2335	575			25
按照reply条数间隔排序，作出分布曲线图：
mysql> select count(*) from count_reply_delay where tweet_count<=10;
mysql> select count(*) from count_reply_delay where tweet_count>10 and tweet_count<=100;
10		100		1000	10000	100000	1000000		>1000000
17983	5154	2584	1224	199		1			0

最大时间间隔： 
mysql> select max(seconds) as max_sec from count_reply_delay;
+-------------------+
| max(seconds)      |
+-------------------+
| 1637125           |
+-------------------+
mysql> select * from count_reply_delay where seconds=1637125;
+----------+-----------+--------------------+--------------------+---------+
| user_id  | friend_id | tweet_id           | reply_id           | seconds |
+----------+-----------+--------------------+--------------------+---------+
| 16403671 | 16552513  | 425723021492359169 | 418856421032460288 | 1637125 |
+----------+-----------+--------------------+--------------------+---------+
最大条数间隔：
mysql> select max(tweet_count) as max_count from count_reply_delay;
+-----------+
| max_count |
+-----------+
|    181096 |
+-----------+
mysql> select * from count_reply_delay where tweet_count=181096;
+---------+-----------+--------------------+--------------------+---------------------+---------------------+---------+-------------+
| user_id | friend_id | tweet_id           | reply_id           | tweet_time          | reply_time          | seconds | tweet_count |
+---------+-----------+--------------------+--------------------+---------------------+---------------------+---------+-------------+
| 6446772 | 6446772   | 424251999278755840 | 418082196109688832 | 2014-01-17 18:48:53 | 2013-12-31 18:12:17 | 1470996 |      181096 |
+---------+-----------+--------------------+--------------------+---------------------+---------------------+---------+-------------+

最小时间间隔：
mysql> select min(seconds) from count_reply_delay;
4
最小条数间隔：
mysql> select min(tweet_count) from count_reply_delay;
0
reply间隔超过1天的数量：
mysql> select count(*) from count_reply_delay where seconds>=86400;
732
所占比例为：732/27145=2.7% 这个比例说明很多人都会及时的回复，大部分人对超过1天前的tweet很少回复。
reply条数间隔超过1天的数量：
mysql> select count(*) from count_reply_delay where tweet_count>=1000;
1425
所占比例为：1425/27145=5.25%

参与回复的用户总数：
mysql> select count(distinct user_id) from count_reply_delay ;
3424

平均时间间隔：
mysql> select sum(seconds)/27145 as avg from count_reply_delay;
+------------+
| avg        |
+------------+
| 11082.4665 |
+------------+
11082.4665 = 3小时
平均条数间隔：
mysql> select sum(tweet_count)/27145 as avg_count from count_reply_delay;
+-----------+
| avg_count |
+-----------+
|  362.1879 |
+-----------+

80%时间间隔：
mysql> select seconds from count_reply_delay order by seconds limit 21716,1;
+---------+
| seconds |
+---------+
|    2424 |
+---------+
由此可见用户平均在236秒=3.9分钟reply他所关注用户的微博。整体的分布很值得做个曲线图分析一下看看属于什么分布：推测是长尾分布。
80%时间间隔：
mysql> select tweet_count from count_reply_delay order by tweet_count limit 21716,1;
+-------------+
| tweet_count |
+-------------+
|          43 |
+-------------+
大部分用户回复的速度是很快的，上下相差43条微博
计算每个用户的平均reply时间：
mysql> insert ignore into count_reply_delay_user (select user_id,sum(seconds)/count(*) as avg_sec,sum(tweet_count)/count(*) as avg_count from count_reply_delay group by user_id);
mysql> select count(*) from count_reply_delay_user where avg_sec<=3600;
+----------+
| count(*) |
+----------+
|    2314  |
+----------+
2314/3424=67.58%
平均reply间隔在24小时内的用户数：
mysql> select count(*) from count_reply_delay_user where avg_sec<=3600*24;
+----------+
| count(*) |
+----------+
|     3290 |
+----------+
3290/3424 = 96.09%
结论：对每个用户来说，能很快对每个用户作出反映是不可能的，但他们大部分都会在1天内对他们感兴趣的话题作出回复。每个用户对其他某一个特定用户都有一个平均reply间隔。计算每个用户对他所有关注者的reply求平均是没有意义的。

mysql> select count(*) from count_reply_delay_user where avg_count<=100;
+----------+
| count(*) |
+----------+
|     2621 |
+----------+
2621/3424=76.55% 大多数的转发是在很短的间隔内完成的

于是计算：A --- B 的reply间隔(同时用户A和B都在我们的数据集中)：
mysql> create table count_reply_delay_AB (select user_id as user_id,tu.id as friend_id,count(*) as count, sum(seconds)as sum,sum(tweet_count) as tweet_count, sum(seconds)/count(*) as avg,sum(tweet_count)/count(*) as avg_count from count_reply_delay crd, twitter_user tu where crd.friend_id=tu.id group by user_id,tu.id);
mysql> select count(*) from count_reply_delay_AB;
+----------+
| count(*) |
+----------+
|  10778   |
+----------+
按照平均reply间隔排序，作出分布曲线图：
mysql> select count(*) from count_reply_delay_AB where avg<=10;
mysql> select count(*) from count_reply_delay_AB where avg>10 and avg<=100;
时间间隔按照10^n进行统计（s）：

10	100		1000	10000	100000	1000000	>1000000

10	2245	4633	2512	1170	207		1

下面分析一个特定的用户（寻找reply最多的用户）：
mysql> select max(count) from (select user_id,count(friend_id) as count from count_reply_delay_AB group by user_id) A;
42
mysql> select user_id from (select user_id,count(friend_id) as count from count_reply_delay_AB group by user_id) A where count=42;
21672825

mysql> select * from count_reply_delay_AB where user_id=21672825;
查看用户100042133对不同的friend reply间隔分布情况：
+----------+-----------+-------+-------+-----------+
| user_id  | friend_id | count | sum   | avg       |
+----------+-----------+-------+-------+-----------+
| 21672825 | 1035491   |     1 |   281 |  281.0000 |
| 21672825 | 11776682  |     1 |    76 |   76.0000 |
| 21672825 | 12349942  |     1 |    91 |   91.0000 |
| 21672825 | 12522     |     1 |   256 |  256.0000 |
| 21672825 | 12536272  |     1 |    62 |   62.0000 |
| 21672825 | 14316355  |     4 |  1217 |  304.2500 |
| 21672825 | 15162187  |     1 |  2727 | 2727.0000 |
| 21672825 | 15195706  |     1 |    53 |   53.0000 |
| 21672825 | 15202741  |     7 | 10029 | 1432.7143 |
| 21672825 | 15208271  |     3 |  2229 |  743.0000 |
| 21672825 | 15295503  |     2 |   629 |  314.5000 |
| 21672825 | 15730837  |     2 |   393 |  196.5000 |
| 21672825 | 15814841  |     1 |   119 |  119.0000 |
| 21672825 | 15866929  |     2 |   738 |  369.0000 |
| 21672825 | 16012310  |     1 |    82 |   82.0000 |
| 21672825 | 16353944  |     1 |   117 |  117.0000 |
| 21672825 | 16801492  |     1 |    75 |   75.0000 |
| 21672825 | 17379314  |     4 |  1171 |  292.7500 |
| 21672825 | 17925141  |     1 |   604 |  604.0000 |
| 21672825 | 18031568  |     1 |    20 |   20.0000 |
| 21672825 | 18448279  |     3 |   593 |  197.6667 |
| 21672825 | 18460854  |     1 |  3382 | 3382.0000 |
| 21672825 | 18689505  |     2 |   353 |  176.5000 |
| 21672825 | 19520336  |     4 |  3795 |  948.7500 |
| 21672825 | 19803702  |     1 |   155 |  155.0000 |
| 21672825 | 20093357  |     1 |    84 |   84.0000 |
| 21672825 | 21089214  |     2 |    62 |   31.0000 |
| 21672825 | 21574752  |     8 |  1666 |  208.2500 |
| 21672825 | 22447454  |     2 |  8838 | 4419.0000 |
| 21672825 | 23795752  |     2 |    99 |   49.5000 |
| 21672825 | 24101967  |     7 |  4110 |  587.1429 |
| 21672825 | 24386848  |     1 |    58 |   58.0000 |
| 21672825 | 25001856  |     1 |  1316 | 1316.0000 |
| 21672825 | 5738952   |     1 |  6521 | 6521.0000 |
| 21672825 | 65801845  |     1 |    52 |   52.0000 |
| 21672825 | 7871702   |     1 |  1098 | 1098.0000 |
| 21672825 | 8181362   |     3 |   188 |   62.6667 |
| 21672825 | 8769212   |    19 |  5119 |  269.4211 |
| 21672825 | 9131442   |     2 |   124 |   62.0000 |
| 21672825 | 9358042   |     3 |   626 |  208.6667 |
| 21672825 | 93730653  |     2 |   467 |  233.5000 |
| 21672825 | 95568270  |     2 |  6132 | 3066.0000 |
+----------+-----------+-------+-------+-----------+

mysql> select count(*) from count_reply_delay_AB where user_id=21672825 and avg <=3600;
+----------+
| count(*) |
+----------+
|       40 |
+----------+
该用户对42个人的转发间隔中对其中40人的平均reply间隔小于3600秒（1小时）
***********************************
用户转发微博之间的差异&用户对内容相同的微博的关注程度变化
***********************************
待续...

***********************************
计算任意两用户间的交流（转发或者回复）时间间隔
***********************************
转发和回复都要考虑到反映时间中去。所以需要看看这两个表重复的关系有多少，然后将它们合并到一起去。
count_reply_delay 中的user_id&friend_id都属于我们的数据集
mysql> select count(*) from count_reply_delay A, count_retweet_delay B where A.user_id=B.user_id and A.friend_id=B.friend_id;
+----------+
| count(*) |
+----------+
|    23064 |
+----------+

##############################################################################################################################
合并统一考虑retweet和reply
mysql> insert ignore into count_delay (select user_id,friend_id, tweet_id, retweet_id as response_id,seconds,tweet_count from count_retweet_delay);
mysql> insert ignore into count_delay (select user_id,friend_id, tweet_id, reply_id as response_id,seconds,tweet_count from count_reply_delay);
630735
80%#################:
mysql> select seconds from count_delay order by seconds limit 504588,1;
8708s
mysql> select tweet_count from count_delay order by tweet_count limit 504588,1;
100

将剩下的20%的数据update成为0：(如果想查看原来的数据，可以创建count_delay_tmp重新生成数据去看)
mysql> update count_delay set tweet_count=0 where tweet_count>100;
mysql> update count_delay set seconds=0 where seconds>8708;

计算任意两个用户间的response 上限：最大的时间间隔和条数间隔
mysql> insert into count_delay_user (select user_id, max(seconds) as seconds, max(tweet_count) as tweet_count from count_delay group by user_id);

将这个 user habit update 到表user_habit中：
mysql> UPDATE user_habit A INNER JOIN count_delay_user B ON A.user_id=B.user_id SET A.read_habit=B.tweet_count;
##mysql> UPDATE user_habit A INNER JOIN tweet_count B ON A.user_id=B.user_id SET A.avg_total=sum(B.total_count) group by B.user_id;
create table user_habit_tmp(select user_id,sum(total_count) as avg_count from tweet_count group by user_id);
 UPDATE user_habit A INNER JOIN user_habit_tmp B ON A.user_id=B.user_id SET A.avg_total=B.avg_count;
##############################################################################################################################
从count_retweet_delay_AB A, count_reply_delay_AB这两个表中抽取重复的记录，将转发和回复的总数求和，总时间间隔求和。
将count_retweet_delay_AB, count_reply_delay_AB两表中不重复的部分也添加到count_delay中：
mysql> insert ignore into count_delay select A.user_id,A.friend_id,A.count,A.sum,A.tweet_count from count_retweet_delay_AB A;

mysql> insert ignore into count_delay select A.user_id,A.friend_id,A.count,A.sum,B.tweet_count from count_reply_delay_AB A;

mysql> select count(*) from count_delay;
+----------+
| count(*) |
+----------+
|    31561 |
+----------+
count_delay ---> count_delay_user ##########################################需要按照用户进行单独统计每个用户的最大容忍度
user_id, limit
计算平均反映（转发或者回复）时间间隔：
mysql> alter table count_delay add column avg float default 0;
mysql> update count_delay set avg=sum/(count*3600);
mysql> alter table count_delay add column avg_count float default 0;
mysql> update count_delay set avg_count=sum/tweet_count;
mysql> select count(*) from count_delay where avg<1;
+----------+
| count(*) |
+----------+
|    24408 |
+----------+
24408/31561=77.33%
有77.33%的用户间的反映时间小于1小时
mysql> select count(*) from count_delay where avg>23;
+----------+
| count(*) |
+----------+
|     1011 |
+----------+
1011/31561=3.2%
只有3.2%的用户间的反应时间大于1天以上。这说明对于绝大部分用户来说一天以前的消息他们从来不关心。

***********************************
计算每个用户的所有好友的发帖的总数（如果按小时细分的话请操作表friends_tweet_count）:
mysql> insert into friends_tweet_num (SELECT A.user_id, sum(B.total_count) as total_count FROM user_friend A LEFT JOIN tweet_count_hour_avg B ON A.friend_id=B.user_id GROUP BY A.user_id);
求子公式：i ---> j: j----> i
mysql> select A.user_id, A.friend_id, B.avg_total/C.total_count as ratio from user_friend A, user_habit B, friends_tweet_num C where A.user_id = C.user_id and A.friend_id = B.user_id; 
***********************************
任意两个用户之间在时间维度上的可见概率计算N*N metrix
编程实现？使用数据库表实现？
***********************************
构造学习转发的数据集：
mysql> select user_id, sum(retweet_count) as retweet_count from tweet_count group by user_id where retweet_count>10 order by user_id limit 0,100; 

构造学习转发的数据集：
mysql> select user_id, sum(retweet_count) as retweet_count from tweet_count group by user_id where retweet_count>10 order by user_id limit 0,100;

# search ResponseRank:
select B.screen_name from (select friend_id,count(*) as count from count_delay group by friend_id) A, twitter_user B where A.friend_id=B.id order by A.count desc into outfile '/tmp/RR.txt';
3683

-- solution
create table response_rank (select friend_id as user_id,count(*) as count from count_delay group by friend_id);
ALTER TABLE response_rank ADD PRIMARY KEY(user_id);
insert ignore into response_rank (select id as user_id,0 from twitter_user)

select B.screen_name from response_rank A, twitter_user B where A.user_id=B.id order by A.count desc into outfile '/tmp/RR.txt'; 
查找FollowerRank:
create table follower_rank (select friend_id as user_id,count(*) as count from user_friend group by friend_id);
ALTER TABLE follower_rank ADD PRIMARY KEY(user_id);
insert ignore into follower_rank (select id as user_id,0 from twitter_user)
select B.screen_name from follower_rank A , twitter_user B where A.user_id = B.id order by A.count desc into outfile '/tmp/FR.txt';
7177
