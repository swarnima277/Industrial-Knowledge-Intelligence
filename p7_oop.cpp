#include <iostream>
using namespace std;
int main(){
    int rev, n, digit, rev=0;
    cout<<"Enter the number to be checked:";
    cin>>n;
    for(i=0;i<=n;i++);
    {
    digit=n%10;
    rev=rev*10+digit;
    }
    if(n=rev)
    cout<<"The number is a palindrome number";
    else
    cout<<"It is not a palindrone number";
    return 0;


}