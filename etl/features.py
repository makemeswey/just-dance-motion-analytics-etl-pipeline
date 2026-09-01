def calc_rotational_speed(x,y,z):
    return round((x*x + y*y + z*z) ** 0.5, 4)

def calc_dynamic_linear_acc(x, y, z):
    linear_acc = (x*x + y*y + z*z) ** 0.5
    return round(abs(linear_acc - 1), 4)