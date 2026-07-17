#include <iostream>
using namespace std;
class circle{
    public:
    void display(float r){
        cout<<"Area of a circle:"<<3.14*r*r<<endl;
    }
};
class rectangle{
    public:
    void display(float l,float b){
        cout<<"Area of a rectangle:"<<l*b<<endl;
    }
};
class square{
    public:
    void display(float s){
        cout<<"Area of a square:"<<s*s<<endl;
    }
};
class triangle{
    public:
    void display(float l,float h){
        cout<<"Area of a triangle:"<<0.5*l*h<<endl;
    }
};
int main(){
    circle c;
    rectangle r;
    square s;
    triangle t;
    float radius, length, breadth, height, side;
    cout<<"Enter radius:";
    cin>> radius;
    c.display(radius); 
    cout<<"Enter length and breadth:";
    cin>> length >> breadth;
    r.display(length, breadth);
    cout<<"Enter side:";
    cin>> side;
    s.display(side);
    cout<<"Enter length and Height:";
    cin>> length>> height;
    t.display(length, height);
    return 0;

}
