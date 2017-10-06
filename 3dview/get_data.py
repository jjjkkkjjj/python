import numpy as np
import math

"""
"head", "R_ear", "L_ear", "sternum", "C7", "R_rib","L_rib", "R_ASIS", "L_ASIS", "R_PSIS", "L_PSIS",
"R_frontshoulder", "R_backshoulder", "R_in_elbow", "R_out_elbow", "R_in_wrist", "R_out_wrist", "R_hand",
"L_frontshoulder", "L_backshoulder", "L_in_elbow", "L_out_elbow", "D_UA?", "L_in_wrist", "L_out_wrist", "L_hand"
"""
Points = {"head":0, "R_ear":1, "L_ear":2, "sternum":3, "C7":4, "R_rib":5, "L_rib":6, "R_ASIS":7, "L_ASIS":8, "R_PSIS":9, "L_PSIS":10,
          "R_frontshoulder":11, "R_backshoulder":12, "R_in_elbow":13, "R_out_elbow":14, "R_in_wrist":15, "R_out_wrist":16, "R_hand":17,
          "L_frontshoulder":18, "L_backshoulder":19, "L_in_elbow":20, "L_out_elbow":21, "D_UA?":22, "L_in_wrist":23, "L_out_wrist":24,
          "L_hand":25}

# calculate velocity(unit is km/h)
def calc_velocity(x, y, z, i, point):
    vx = (x[i + 1][point] - x[i][point])*1.8
    vy = (y[i + 1][point] - y[i][point])*1.8
    vz = (z[i + 1][point] - z[i][point])*1.8

    return math.sqrt(vx*vx + vy*vy + vz*vz)

def get_data(x, y, z, joints_height, joints_velocity):
    # data
    Return_height_data = []
    Return_velocity_data = []

    tmp_h = []
    tmp_v = []

    for i in range(len(x) - 1):
        height_data = {}
        for key in joints_height:
            height_data[key] = -1
        velocity_data = {}
        for key in joints_velocity:
            velocity_data[key] = -1
        # height (extract z value simply) (mm times 0.001 -> m
        for key in height_data.keys():
            height_data[key] = z[i][Points[key]]*0.001
        Return_height_data.append(height_data)

        # velocity
        for key in velocity_data.keys():
            velocity_data[key] = calc_velocity(x, y, z, i, Points[key])
        Return_velocity_data.append(velocity_data)

    tmp_h = [[h[key] for h in Return_height_data] for key in height_data.keys()]
    tmp_v = [[v[key] for v in Return_velocity_data] for key in velocity_data.keys()]

    Return_height_max = {}
    for i, key in enumerate(height_data.keys()):
        Return_height_max[key] = max(tmp_h[i])
    Return_velocity_max = {}
    for i, key in enumerate(velocity_data.keys()):
        Return_velocity_max[key] = max(tmp_v[i])

    return Return_height_data, Return_velocity_data, Return_height_max, Return_velocity_max