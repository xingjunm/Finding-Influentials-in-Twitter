function [mem cent] = ksc_toy(A, K)
%[mem cent] = ksc_toy(A,K)
%K-SC toy implementation
%Input
%A: A set of time series. Each row vector A(i,:) corresponds to each time series
%K: The number of clusters 
%
%Output
%mem = Membership for each time series. mem(i) = the cluster index that
%time series i belongs to
%cent = A set of cluster centroids. Each row vector cent(i,:) corresponds
%to each cluster centroids
m=size(A, 1);
mem = ceil(K*rand(m, 1));
cent = zeros(K,size(A, 2));
for iter = 1:100
    prev_mem = mem;
    for k = 1:K
        cent(k,:) = ksc_center(mem, A, k, cent(k,:));
    end
    for i = 1:m
        x = A(i,:);
        for k = 1:K
            y = cent(k,:);
            dist = dhat_shift(x,y);
            D(i,k) = dist;
        end
    end
    [val mem] = min(D,[],2);
    if norm(prev_mem-mem) == 0
        break;
    end
end
return


