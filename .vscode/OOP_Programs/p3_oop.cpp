#include <iostream>
using namespace std;
int main(){
    char ch;
    cout<<"Enter the character";
    cin>> ch;
    if ((ch>='A'&& ch<='Z')||(ch>='a'&& ch<='z'))
    cout<<"it is a character"<<endl;
    else 
    cout<<"it is not a character"<<endl;
    return 0;
}