translate([0, -1, 0])
cube([9 * 4, 12, 0.3]);

translate([9, -13, 0])
cube([9 * 4, 12, 0.3]);

translate([9, -(12*2 + 1), 0])
cube([9 * 4, 12, 0.3]);

translate([0, -(12*3 + 1), 0])
cube([9 * 4, 12, 0.3]);

linear_extrude(height = 5)
{
    text(text = "08:00");
    translate([10, -12, 0])
    text(text = "12:00");
    
    translate([10, -12*2, 0])
    text(text = "13:00");
    
    translate([0, -12*3, 0])
    text(text = "17:00");
}