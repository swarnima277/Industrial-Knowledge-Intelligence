#include <iostream>
#include <string>
using namespace std;
int main(){
    char str[100];
    int count=0;
    cout<<"enter string:";
    cin.getline(str,100);
    cout<<"the vowels are:";
    for(i=0;str[i]!='/0',i++)
    {
        if(str[i]=='a'||str[i]=='e'||str[i]=='i'||str[i]=='o'||str[i]=='u'||str[i]== 'A' || str[i] == 'E' || str[i] == 'I' || str[i] == 'O' || str[i]== 'U')
          cout<<''<<str[i];
          count++;
    }
    cout<<"the total number of vowels are:"<<count;
    return 0;
}