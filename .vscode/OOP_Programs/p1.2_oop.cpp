#include <iostream>
using namespace std;
class Student{
    private:
    string name;
    int marks;

    public:
    void input();
    void display();
};
void Student::input(){
    cout<<"Enter name:";
    cin>>name;
    cout<<"Enter marks:";
    cin>>marks;
}
void Student::display(){
    cout<<"Name:"<<name<<endl;
    cout<<"Marks"<<marks<<endl;
}
int main(){
    Student s;
    s.input();
    s.display();
    
};
