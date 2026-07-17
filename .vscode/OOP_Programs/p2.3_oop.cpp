#include <iostream>
using namespace std;
class circle{
    public:
     float area(float r);
};
class rectangle{
    public:
     float area(float l, float b);
};
class square{
    public:
     float area(float s);
};
class triangle{
    public:
     float area(float l, float h);
};
float circle::area(float r)
{
  return 3.14*r*r;  
}
float rectangle::area(float l, float b)
{
   return l*b; 
}
float square::area(float s)
{
   return s*s;   
}
float triangle::area(float l, float h)
{
    return 0.5*l*h;
}
int main(){
    circle c;
    rectangle r;
    triangle t;
    square s;
    float radius, length, breadth, base, height, side;

    cout<<"Enter radius:";
    cin>> radius;
    cout<<"Area of a circle:"<<c.area(radius)<<endl;
    cout<<"Enter length and Breadth:";
    cin>> length>> breadth;
    cout<<"area of a rectangle:"<<r.area(length, breadth)<<endl;
    cout << "Enter base and height: ";
    cin >> base >> height;
    cout << "Area of Triangle = " << t.area(base, height) << endl;

    cout << "Enter side: ";
    cin >> side;
    cout << "Area of Square = " << s.area(side) << endl;

    return 0;

}