#include <iostream>
#include <fstream>
#include <unordered_map>
#include <string>
//#include <io.h>
#include <dirent.h>
#include <vector>
#include <time.h>

using namespace std;

class GetFrequencyWords
{
public:
	void ReadAndWriteDoc(string srcDir, string desfile)
	{
		struct dirent *file=NULL;
		DIR *pdir=opendir(srcDir.c_str());
		if(pdir==NULL)
		{
			cerr<<"Wrong directory, try again!!!"<<endl;
			return;
		}
		vector<string> filesname;
		while((file=readdir(pdir))!=NULL)
		{
			if(file->d_type==8)//为文件类型
				filesname.push_back(file->d_name);
		}
		//_finddata_t fileInfo;
		//long handle = _findfirst(srcDir.c_str(), &fileInfo);
		//if(handle ==-1L)
		//{
			//cerr<<"Wrong directory, try again!!!"<<endl;
			//return;
		//}
		//do
		//{
			//filesname.push_back(fileInfo.name);
		//}while(_findnext(handle, &fileInfo==0));
		
		ifstream infile;
		string temp;
		vector<string>tempstrs;
		//unordered_map<string, int> strCount;
		for(int i=0;i<filesname.size();i++)
		{
			infile.open(srcDir+"/"+filesname[i].c_str());
			if(infile.good())
				while(getline(infile, temp, '\n'))
				{
					tempstrs=split(temp, " ");
					for(int j=0;j<tempstrs.size();j++)
					{
						if(strCount.find(tempstrs[j])==strCount.end())
							strCount[tempstrs[j]]=1;
						else
							strCount[tempstrs[j]]+=1;
					}
				}
			infile.close();
			if(i%500==0)
				cout<<i<<endl;
		}
		ofstream outfile(desfile.c_str());
		unordered_map<string, int>::iterator iter;
		for(iter=strCount.begin();iter!=strCount.end();++iter)
		{
			outfile<<iter->first<<" "<<iter->second<<endl;
			//cout<<iter->first<<" "<<iter->second<<endl;
		}
		outfile.close();
	}
	void DelLessFreWords(string srcDir, string destDir, int num)
	{
		struct dirent *file=NULL;
		DIR *pdir=opendir(srcDir.c_str());
		if(pdir==NULL)
		{
			cerr<<"Wrong directory, try again!!!"<<endl;
			return;
		}
		vector<string> filesname;
		while((file=readdir(pdir))!=NULL)
		{
			if(file->d_type==8)//为文件类型
				filesname.push_back(file->d_name);
		}
		ifstream infile;
		ofstream outfile;
		string temp;
		string outtemp;
		vector<string>tempstrs;
		//unordered_map<string, int> strCount;
		for(int i=0;i<filesname.size();i++)
		{
			infile.open(srcDir+"/"+filesname[i].c_str());
			outfile.open(destDir+"/"+filesname[i].c_str());
			//outtemp="";
			if(infile.good())
				while(getline(infile, temp, '\n'))
				{
					outtemp="";
					tempstrs=split(temp, " ");
					for(int j=0;j<tempstrs.size();j++)
					{
						if(strCount[tempstrs[j]]>num)
						{
							outtemp+=tempstrs[j]+" ";
						}
					}
					if(outtemp.length()>2)
					{
						outtemp.erase(outtemp.length()-1);//去掉最后的空格
						outfile<<outtemp<<endl;
					}
				}
			outfile.close();
			infile.close();
			if(i%500==0)
				cout<<i<<endl;
		}
	}
private:
	unordered_map<string, int> strCount;

	vector<string> split(string str, string pattern)
	{
		vector<string> result;
		for(int i=0;i<str.length();)
		{
			if(str.find(pattern, i)!=str.npos)
			{
				result.push_back(str.substr(i, str.find(pattern, i)-i));
				i=str.find(pattern, i)+pattern.length();
			}
			else
			{
				result.push_back(str.substr(i));
				break;
			}
		}
		return result;
	}
};
int main(void)
{
	clock_t start,finish;
	double totaltime;
	start=clock();
	GetFrequencyWords getFreWords;
	getFreWords.ReadAndWriteDoc("./processing-texts", "frequencyword.map");
	getFreWords.DelLessFreWords("./processing-texts", "./processed-texts", 3);
	finish=clock();
	totaltime=(double)(finish-start)/CLOCKS_PER_SEC; //得到结果单位秒，如果时间太短太短的话可能是0
	cout<<"running time: "<<totaltime<<" 秒"<<endl;
	return 0;
}
