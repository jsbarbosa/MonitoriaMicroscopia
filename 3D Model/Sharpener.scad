$fn = 50;

module GraphiteBar()
{
    rotate([90, 0, 0])
    cylinder(d = 4.0, h = 20, center = true);
}

module SandSupport()
{   
    d = 20;
    w = 3.0;
    l = 4.0;
    
    difference()
    {
        cube([20, l, w], center = true);
        
        translate([-8, 0, 0])
        cube([2, 3, w*1.1], center = true);
        
        translate([8, 0, 0])
        cube([2, 3, w*1.1], center = true);
    }
}

module Sharpener()
{
    d = 15;
    h = 25;
    
    new_width = 1.5;
    
    difference()
    {
        translate([0, h/2, 0])
        difference()
        {
            
            rotate([90, 0, 0])
            cylinder(d = d, h = h, center = true);
            
            w = 3.5;
            l = 5;
            translate([0, l/2 - 8, (w + new_width)/2])
            cube([d*1.1, l, w], center = true);
            
            translate([0, l/2 - 8, -(w + new_width)/2 ])
            cube([d*1.1, l, w], center = true);
            
        }
        translate([0, 1, 0])
        GraphiteBar();
        
        translate([0, 5/2 + 25 - 7, 0])
        rotate([90, 0, 0])
        #cylinder(d = 3.5, h = 10, center = true);
    }
}

SandSupport();

//GraphiteBar();
//Sharpener();