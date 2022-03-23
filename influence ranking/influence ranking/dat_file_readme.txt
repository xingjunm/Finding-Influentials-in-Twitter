### edges.dat
relation file, it saves all the relations needed to generate the training data
format:
[friend_id]	[user_id]

### nodes.dat
user id list
format:
[user_id]

### i-j-cosine.dat
user i vs. j temporal cosine distance：
format:
[friend_id]	[user_id]	[cosine]

### i-j-ratio.dat
user j tweet count/user i's all friends tweet sum count
format:
[user_i]	[user_j]	[ratio]

### cosine-sim-i.dat i is the number of topics, e.g., cosine-sim-100.dat
user-user topic simmilarity
format:
[friend_id]	[user_id]	[cosine]

