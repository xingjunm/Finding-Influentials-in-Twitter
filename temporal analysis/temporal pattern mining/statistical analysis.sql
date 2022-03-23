1. hour-based analaysis
mysql> select hour,sum(total_count) as total from tweet_count_hour_avg group by hour;
24 rows in set (0.08 sec)

2. day-based analysis
mysql> select day,sum(total_count) as total from tweet_count_day group by day;
7 rows in set (0.08 sec)
