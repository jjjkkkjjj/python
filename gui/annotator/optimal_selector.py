import numpy as np
from scipy import interpolate

def extrapolate(jointID, startFrame, X, Y, Z, Range):
    x = X.copy()
    y = Y.copy()
    z = Z.copy()
    # minus direction
    IDlist = [jointID]
    nowID = jointID
    prevID = jointID
    prevT = startFrame

    for i, t in enumerate(reversed(range(startFrame))):
        # if there is a datum with prevID within range
        dist = pow(x[t, nowID] - x[prevT, prevID], 2) + pow(y[t, nowID] - y[prevT, prevID], 2) + pow(z[t, nowID] - z[prevT, prevID], 2)
        if dist <= Range*Range:
            IDlist.append(nowID)
            prevT = t
        else: # nan
            if i == 0:
                raise ValueError("+-1 frame must be within range!")
            else:
                # nan

                """
                time = np.arange(i + 1)

                tmp = np.array([x[startFrame - j, IDlist[j]] for j in range(len(IDlist))])
                linearX = interpolate.interp1d(time, tmp, fill_value='extrapolate')
                x[t, prevID] = linearX(i + 1)
                print((x[t, prevID], x[t + 1, prevID]))
                tmp = np.array([y[startFrame - j, IDlist[j]] for j in range(len(IDlist))])
                linearY = interpolate.interp1d(time, tmp, fill_value='extrapolate')
                y[t, prevID] = linearY(i + 1)
                tmp = np.array([z[startFrame - j, IDlist[j]] for j in range(len(IDlist))])
                linearZ = interpolate.interp1d(time, tmp, fill_value='extrapolate')
                z[t, prevID] = linearZ(i + 1)
                """
                IDlist.append(-1)
                prevT = t

                # search ID
                if t != 0:
                    cand = np.argmin(np.square(x[t - 1, :] - x[t, prevID])
                                    + np.square(y[t - 1, :] - y[t, prevID])
                                    + np.square(z[t - 1, :] - z[t, prevID]))

                    if (pow(x[t - 1, cand] - x[t, prevID], 2)
                            + pow(y[t - 1, cand] - y[t, prevID], 2)
                            + pow(z[t - 1, cand] - z[t, prevID], 2)) < Range*Range:
                        prevID = nowID
                        nowID = cand

    IDlist = IDlist[::-1]

    nowID = jointID
    prevID = jointID
    prevT = startFrame
    # plus direction
    for i, t in enumerate(range(startFrame + 1, X.shape[0])):
        # if there is a datum with prevID within range
        dist = pow(x[t, nowID] - x[prevT, prevID], 2) + pow(y[t, nowID] - y[prevT, prevID], 2) + pow(z[t, nowID] - z[prevT, prevID], 2)
        if dist <= Range*Range:
            IDlist.append(nowID)
            prevT = t
        else: # nan
            if i == 0:
                raise ValueError("+-1 frame must be within range!")
            else:
                # nan
                time = np.arange(i + 1)

                tmp = np.array([x[startFrame + ind, IDlist[j]] for ind, j in enumerate(range(startFrame, len(IDlist)))])
                linearX = interpolate.interp1d(time, tmp, fill_value='extrapolate')
                x[t, prevID] = linearX(i + 1)
                tmp = np.array([y[startFrame + ind, IDlist[j]] for ind, j in enumerate(range(startFrame, len(IDlist)))])
                linearY = interpolate.interp1d(time, tmp, fill_value='extrapolate')
                y[t, prevID] = linearY(i + 1)
                tmp = np.array([z[startFrame + ind, IDlist[j]] for ind, j in enumerate(range(startFrame, len(IDlist)))])
                linearZ = interpolate.interp1d(time, tmp, fill_value='extrapolate')
                z[t, prevID] = linearZ(i + 1)

                IDlist.append(-1)
                prevT = t

                # search ID
                if t != X.shape[0] - 1:
                    cand = np.argmin(np.square(x[t + 1, :] - x[t, prevID])
                                     + np.square(y[t + 1, :] - y[t, prevID])
                                     + np.square(z[t + 1, :] - z[t, prevID]))
                    if (pow(x[t + 1, cand] - x[t, prevID], 2)
                        + pow(y[t + 1, cand] - y[t, prevID], 2)
                        + pow(z[t + 1, cand] - z[t, prevID], 2)) < Range * Range:
                        prevID = nowID
                        nowID = cand

    return IDlist


def extrapolate_(jointID, startFrame, X, Y, Z, Range):
    x = X.copy()
    y = Y.copy()
    z = Z.copy()
    # minus direction
    IDlist = [jointID, jointID]
    v = np.array([x[startFrame, jointID] - x[startFrame - 1, jointID],
             y[startFrame, jointID] - y[startFrame - 1, jointID],
             z[startFrame, jointID] - z[startFrame - 1, jointID]])

    for i, t in enumerate(reversed(range(startFrame - 1))):
        if IDlist[i + 1] != -1:
            prev = np.array([x[t + 1, IDlist[i + 1]], y[t + 1, IDlist[i + 1]], z[t + 1, IDlist[i + 1]]])
        else:
            prev = v
        searchini = prev + v

        if x[t, IDlist[i + 1]] == 0.0 and y[t, IDlist[i + 1]] == 0.0 and z[t, IDlist[i + 1]] == 0.0:
            IDlist.append(-1)
        else:
            pass


        now = np.array([x[t, :], y[t, :], z[t, :]])

        dist = np.linalg.norm(now - searchini[:, np.newaxis], axis=0)
        print(dist)
        ind = np.where(dist <= Range)[0]

        if ind.shape[0] != 0:
            IDlist.append(np.argmin(dist))
        else:
            # nan
            IDlist.append(-1)


    IDlist = IDlist[::-1]

    IDlist.append(jointID)
    # plus direction
    for i, t in enumerate(range(startFrame + 2, X.shape[0])):
        if IDlist[t - 1] != -1:
            prev = np.array([x[t - 1, IDlist[t - 1]], y[t - 1, IDlist[t - 1]], z[t - 1, IDlist[t - 1]]])
        else:
            prev = v
        searchini = prev + v

        now = np.array([x[t, :], y[t, :], z[t, :]])

        dist = np.linalg.norm(now - searchini[:, np.newaxis], axis=0)
        ind = np.where(dist <= Range)[0]
        if ind.shape[0] != 0:
            IDlist.append(np.argmin(dist))
        else:
            # nan
            IDlist.append(-1)

    return IDlist

def DP():

    return