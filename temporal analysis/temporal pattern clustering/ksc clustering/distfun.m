function D = distfun(x, X)
%UNTITLED Summary of this function goes here
%   X0 is a 1-by-p point, X is an n-by-p matrix of points. 
% The function distfun returns an n-by-1 vector d of distances between X0 and each point (row) in X.
m=size(X, 1);
for i=1:m
    y = X(i,:);
    D(i,1) = dhat_shift(x,y);
end
return

