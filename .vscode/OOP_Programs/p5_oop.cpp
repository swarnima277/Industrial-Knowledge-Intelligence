#include <iostream>
using namespace std;
int main(){
    char str[100];
    int count=0;
    cout<<"Enter the string:";
    cin.getline(str,100);
    for(int i=0;str[i]!='\0';i++)
    {
        count++;
    }
    cout<<"the length of the string is :"<<count;
    return 0;

}