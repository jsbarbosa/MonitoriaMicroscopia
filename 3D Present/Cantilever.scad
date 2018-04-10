module Cantilever()
{
    scale([2, 1, 1])
    union()
    {
        difference()
        {
            cylinder(d = 10, h = 2, $fn = 3);
            cylinder(d = 8, h = 4, $fn = 3);
        }
        
        translate([3, 0, 0])
        cylinder(d = 3, h = 2, $fn = 3);
        
        translate([-4, 0, 1])
        cube([3, 10, 2], center = true);
    }
    
    translate([6, 0, 2])
    rotate([0, 0, 45]) 
    cylinder(d1=sqrt(pow(1.5,2)*2), d2=0, h=3, $fn=4);
}

Cantilever();