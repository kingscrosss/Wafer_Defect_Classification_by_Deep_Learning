from skimage import measure
from skimage.transform import radon
from scipy import interpolate, stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy
import sys
import warnings

warnings.filterwarnings("ignore")  # 경고문 출력 제거
np.set_printoptions(threshold=sys.maxsize)  # 배열 전체 출력
pd.set_option('display.max_columns', None)

df = pd.read_pickle("./datasets/LSWMD_CleanData.pickle")
df.info()
print(df)

# failureType label 별 index 찾기
x = []
labels = ['Normal', 'Center', 'Donut', 'Edge-Loc', 'Edge-Ring', 'Loc', 'Random', 'Scratch', 'Near-full']
for label in labels:
    idx = df[df['failureType'] == label].index
    x.append(idx[0])
print(x)  # x = [0, 43, 6492, 35, 97, 19, 541, 130, 814]


def cal_den(x):
    return 100 * (np.sum(x == 2) / np.size(x))


def find_regions(x):
    rows = np.size(x, axis=0)
    cols = np.size(x, axis=1)

    ind1 = np.arange(0, rows, rows // 5)
    ind2 = np.arange(0, cols, cols // 5)

    reg1 = x[ind1[0]:ind1[1], :]
    reg3 = x[ind1[4]:, :]
    reg4 = x[:, ind2[0]:ind2[1]]
    reg2 = x[:, ind2[4]:]

    reg5 = x[ind1[1]:ind1[2], ind2[1]:ind2[2]]
    reg6 = x[ind1[1]:ind1[2], ind2[2]:ind2[3]]
    reg7 = x[ind1[1]:ind1[2], ind2[3]:ind2[4]]
    reg8 = x[ind1[2]:ind1[3], ind2[1]:ind2[2]]
    reg9 = x[ind1[2]:ind1[3], ind2[2]:ind2[3]]
    reg10 = x[ind1[2]:ind1[3], ind2[3]:ind2[4]]
    reg11 = x[ind1[3]:ind1[4], ind2[1]:ind2[2]]
    reg12 = x[ind1[3]:ind1[4], ind2[2]:ind2[3]]
    reg13 = x[ind1[3]:ind1[4], ind2[3]:ind2[4]]

    fea_reg_den = [cal_den(reg1), cal_den(reg2), cal_den(reg3), cal_den(reg4), cal_den(reg5), cal_den(reg6),
                   cal_den(reg7), cal_den(reg8), cal_den(reg9), cal_den(reg10), cal_den(reg11), cal_den(reg12),
                   cal_den(reg13)]
    return fea_reg_den


df['fea_reg'] = df.waferMap.apply(find_regions)
print(df.head())

fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(15, 15))
ax = ax.ravel(order='C')
for i in range(9):
    ax[i].bar(np.linspace(1, 13, 13), df.fea_reg[x[i]])
    ax[i].set_title(df.failureType[x[i]], fontsize=15)
    ax[i].set_xticklabels(labels)
    ax[i].set_xticks([])
    ax[i].set_yticks([])
# plt.tight_layout()
plt.show()


def change_val(img):
    img[img == 1] = 0
    return img


df_copy = df.copy()
df_copy['new_waferMap'] = df['waferMap'].apply(lambda img: change_val(copy.deepcopy(img)))
print(df.waferMap[0])
exit()


fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(15, 15))
ax = ax.ravel(order='C')
for i in range(9):
    img = df_copy.new_waferMap[x[i]]
    theta = np.linspace(0., 180., max(img.shape), endpoint=False)
    sinogram = radon(img, theta=theta)

    ax[i].imshow(sinogram, cmap=plt.cm.Greys_r, extent=(0, 180, 0, sinogram.shape[0]), aspect='auto')
    ax[i].set_title(df_copy.failureType[x[i]], fontsize=15)
    ax[i].set_xticks([])
plt.tight_layout()

plt.show()


def cubic_inter_mean(img):
    theta = np.linspace(0., 180., max(img.shape), endpoint=False)
    sinogram = radon(img, theta=theta, preserve_range=True)
    xMean_Row = np.mean(sinogram, axis=1)
    # xMean_Row = np.mean(img, axis=1)
    x = np.linspace(1, xMean_Row.size, xMean_Row.size)
    y = xMean_Row
    f = interpolate.interp1d(x, y, kind='cubic')
    xnew = np.linspace(1, xMean_Row.size, 20)
    ynew = f(xnew) / 100  # use interpolation function returned by `interp1d`
    return ynew


def cubic_inter_std(img):
    theta = np.linspace(0., 180., max(img.shape), endpoint=False)
    sinogram = radon(img, theta=theta, preserve_range=True)
    xStd_Row = np.std(sinogram, axis=1)
    # xStd_Row = np.std(img, axis=1)
    x = np.linspace(1, xStd_Row.size, xStd_Row.size)
    y = xStd_Row
    f = interpolate.interp1d(x, y, kind='cubic')
    xnew = np.linspace(1, xStd_Row.size, 20)
    ynew = f(xnew) / 100  # use interpolation function returned by `interp1d`
    return ynew


df_copy['fea_cub_mean'] = df_copy.new_waferMap.apply(cubic_inter_mean)
df_copy['fea_cub_std'] = df_copy.new_waferMap.apply(cubic_inter_std)

print(df_copy.fea_cub_mean.head())

fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(15, 15))
ax = ax.ravel(order='C')
for i in range(9):
    ax[i].bar(np.linspace(1, 20, 20), df_copy.fea_cub_mean[x[i]])
    ax[i].set_title(df_copy.failureType[x[i]], fontsize=10)
    ax[i].set_xticks([])
    ax[i].set_xlim([0, 21])
    ax[i].set_ylim([0, 1])
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(15, 15))
ax = ax.ravel(order='C')
for i in range(9):
    ax[i].bar(np.linspace(1, 20, 20), df_copy.fea_cub_std[x[i]])
    ax[i].set_title(df_copy.failureType[x[i]], fontsize=10)
    ax[i].set_xticks([])
    ax[i].set_xlim([0, 21])
    ax[i].set_ylim([0, 0.3])
plt.tight_layout()
plt.show()

fig, ax = plt.subplots(nrows=3, ncols=3, figsize=(15, 15))
ax = ax.ravel(order='C')
for i in range(9):
    img = df_copy.new_waferMap[x[i]]
    zero_img = np.zeros(img.shape)
    img_labels = measure.label(img, connectivity=1, background=0)
    img_labels = img_labels - 1
    if img_labels.max() == 0:
        no_region = 0
    else:
        info_region = stats.mode(img_labels[img_labels > -1], axis=None)
        no_region = info_region[0]

    zero_img[np.where(img_labels == no_region)] = 2
    ax[i].imshow(zero_img)
    ax[i].set_title(df_copy.failureType[x[i]], fontsize=10)
    ax[i].set_xticks([])
plt.tight_layout()
plt.show()


def cal_dist(img, x, y):
    dim0 = np.size(img, axis=0)
    dim1 = np.size(img, axis=1)
    dist = np.sqrt((x - dim0 / 2) ** 2 + (y - dim1 / 2) ** 2)
    return dist


def fea_geom(img):
    norm_area = img.shape[0] * img.shape[1]
    norm_perimeter = np.sqrt((img.shape[0]) ** 2 + (img.shape[1]) ** 2)

    img_labels = measure.label(img, connectivity=1, background=0)

    if img_labels.max() == 0:
        img_labels[img_labels == 0] = 1
        no_region = 0
    else:
        info_region = stats.mode(img_labels[img_labels > 0], axis=None)
        no_region = info_region[0][0] - 1

    prop = measure.regionprops(img_labels)
    prop_area = prop[no_region].area / norm_area
    prop_perimeter = prop[no_region].perimeter / norm_perimeter

    prop_cent = prop[no_region].local_centroid
    prop_cent = cal_dist(img, prop_cent[0], prop_cent[1])

    prop_majaxis = prop[no_region].major_axis_length / norm_perimeter
    prop_minaxis = prop[no_region].minor_axis_length / norm_perimeter
    prop_ecc = prop[no_region].eccentricity
    prop_solidity = prop[no_region].solidity

    return prop_area, prop_perimeter, prop_majaxis, prop_minaxis, prop_ecc, prop_solidity


df_copy['fea_geom'] = df_copy.new_waferMap.apply(fea_geom)
print(df_copy.fea_geom[20256])

df_all = copy.deepcopy(df_copy)
a = [df_all.fea_reg[i] for i in range(df_all.shape[0])]  # 13
b = [df_all.fea_cub_mean[i] for i in range(df_all.shape[0])]  # 20
c = [df_all.fea_cub_std[i] for i in range(df_all.shape[0])]  # 20
d = [df_all.fea_geom[i] for i in range(df_all.shape[0])]  # 6
fea_all = np.concatenate((np.array(a), np.array(b), np.array(c), np.array(d)), axis=1)  # 59 in total

label = [df_all.failureNum[i] for i in range(df_all.shape[0])]
label = np.array(label)

df_all.info()

df_all.drop('waferMap', axis=1, inplace=True)
df_all['waferMap'] = df['waferMap']
print(df_all.waferMap[0])
