translate([0, -1, 0])
cube([9 * 5, 12, 0.3]);

linear_extrude(height = 5)
{
    text(text = "Horario");
}

translate([0, -15, 0])
cube([9 * 5, 12, 0.3]);

translate([0, -14, 0])
linear_extrude(height = 5)
{
    text(text = "Timbre");
}