difference()
{
    union()
    {
        cylinder(d = 13, h = 5, $fn=100);
        translate([0, 0, 7])
        cube([6, 11, 10], center = true);
    }
    
    cylinder(d = 10, h = 3, $fn=6);
    
    cylinder(d = 4, h = 20, $fn=100);
}