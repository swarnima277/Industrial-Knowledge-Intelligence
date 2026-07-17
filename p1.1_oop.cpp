#include <iostream>
using namespace std;
class Student{
    string name;
    int marks;
    public:
    void input(){
        cout<<"Enter name:";
        cin>>name;
        cout<<"Enter marks:";
        cin>>marks;
    }
    void Display(){
        cout<<"Name:"<<name<<endl;
        cout<<"Marks:"<<marks<<endl;
    }
};
int main(){
    Student s;
    s.input();
    s.Display();
};    
