function test_silhouette(ItemType)
%UNTITLED6 Summary of this function goes here
%   Detailed explanation goes here
if ItemType == 1
    fid = fopen('MemePhr.txt');
    rand('state', 2);
elseif ItemType == 2
    fid = fopen('TwtHtag.txt');
    rand('state', 3);
else
    fid = fopen('user_distribution.txt');
    rand('state', 4);
end
    
% rand('state',0    
% close all;


X = [];
while 1
    tline = fgetl(fid);
    if(tline == -1) break; end;
    a = str2num(tline);
    if length(a)>0
        %disp(tline);
        X = [X;a];
    end
end
fclose(fid);
ksc = csvread('ksc-24.dat');

% compute Average Silhouette
% s = silhouette(X,ksc,'cosine');
s = silhouette(X,ksc,@distfun);
fid = fopen('avg_silhouette.dat','a');
avg = mean(s);
fprintf(fid,'%6.2f\n',avg);
fclose(fid);
disp(avg);


