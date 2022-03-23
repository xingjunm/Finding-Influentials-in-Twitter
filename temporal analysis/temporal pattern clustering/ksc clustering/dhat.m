function dist = dhat(x, y)
alpha = x*y' /(y*y');
dist = norm(x - alpha * y)/norm(x);
return