#include <iostream>
using namespace std;
class circle{
    float r,A;
    public:
    void input(){
        cout<<"Enter radius:";
        cin>>r;
    }
    void display(){
        cout<<"Area of a circle:",3.14*r*r;
    } 
};
class rectangle{
    float l,b;
    public:
    void input(){
        cout<<"Enter length and breadth:";
        cin>>l>>b;
    }
    void display(){
        cout<<"Area of a rectangle:",l*b;
    } 
};
class triangle{
    float l,h;
    public:
    void input(){
        cout<<"Enter length and height:";
        cin>>l>>h;
    }
    void display(){
        cout<<"Area of a rectangle:",0.5*l*h;
    } 
};
class square{
    float s;
    public:
    void input(){
        cout<<"Enter side of a square:";
        cin>>s;
    }
    void display(){
        cout<<"Area of a square:",s*s;
    } 
int main(){
        circle c;
        rectangle r;   
        triangle t;
        square s;
        c.input();
        c.display();
        r.input();
        r.display();
        t.input();
        t.display();
        s.input();
        s.display();

        return 0;
    }
};