function [dist optshift opty] = dhat(x, y)
min_d = scale_d(x,y);
L = length(y);
range = -5:5;
for shift = range
    if shift < 0
        yshift = [y(-shift + 1:end) zeros(1, -shift)];
    else
        yshift = [zeros(1,shift) y(1:end-shift) ];
    end
    cur_d = scale_d(x,yshift);
    if cur_d <= min_d
        optshift = shift;
        opty = yshift;
        min_d = cur_d;
    end
end
dist = min_d;

return



function dist = scale_d(x,y)
alpha = x * y' / (y * y');
dist = norm(x - alpha * y) / norm(x);
return