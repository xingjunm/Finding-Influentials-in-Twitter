function ksc = ksc_center(mem, A, k, cur_center)
%Computes ksc centroid
a = [];
for i=1:length(mem)
    if mem(i) == k
        if sum(cur_center) == 0
            opt_a = A(i,:);
        else
            [tmp tmps opt_a] = dhat_shift(cur_center, A(i,:));
        end
        a = [a; opt_a];
    end
end
if size(a,1) == 0;
    ksc = zeros(1, size(A,2)); 
    return;
end;
b = a ./ repmat(sqrt(sum(a.^2,2)), [1 size(a,2)]);
M = b'*b - size(a, 1) * eye(size(a, 2));
[V D] = eig(M);
ksc = V(:,end);
if sum(ksc) < 0
    ksc = -ksc;
end
return
