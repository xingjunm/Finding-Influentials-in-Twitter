function test_ksc(ItemType)
% test ksc and plot cluster centroids
% ItemType = 1: Memetracker phrase
% ItemType = 2: Twitter Hashtags

if ItemType == 1
    fid = fopen('MemePhr.txt');
    rand('state', 2);
elseif ItemType == 2
    fid = fopen('TwtHtag.txt');
    rand('state', 3);
else
    fid = fopen('tweets_distribution.txt');
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


b = X./repmat(max(X, [], 2),[1 size(X,2)]);
[ksc cent] = ksc_toy(X, 3);

% output the result to csv file
csvwrite('E:\workspace_matlab\ksc_toy\ksc-3.dat',ksc);
% plot the cnetroids on the plane
fid= fopen('E:\workspace_matlab\ksc_toy\ksc-3-cent.txt','w')
figure;
for i=1:3
  subplot(3,1,i);
  plot(cent(i,:));
  %disp(cent(i,:));
  for j=1:24
      fprintf(fid,'%f\t',cent(i,j))
  end
  fprintf(fid,'\n')
  title(['Cluster ' num2str(i)]);
  axis([0 24 0 1.2 * max(cent(i,:))]);
end
fclose(fid)
