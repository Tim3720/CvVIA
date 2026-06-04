import cv2
import numpy as np
from matplotlib.figure import Figure

axs = []
last_images = []
last_rois = {}

densities = {}

def setup(fig: Figure):
    last_images.clear()
    last_rois.clear()
    densities.clear()
    axs.clear()


def process_frame(frame: np.ndarray, idx: int, fig: Figure) -> np.ndarray:
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if len(last_images) == 0:
        last_images.append(img)

    # flow = cv2.calcOpticalFlowFarneback(
    #     last_images[-1],
    #     img,
    #     None,
    #     pyr_scale=0.5,
    #     levels=3,
    #     winsize=5,
    #     iterations=5,
    #     poly_n=7,
    #     poly_sigma=1.5,
    #     flags=0
    # )
    #
    # flow = (np.round(flow, 2) * 100).astype(np.uint8)
    # res = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
    # res[:, :, 0] = img
    # res[:, :, 1] = img
    # res[:, :, 2] = img
    #
    # res[:,  :, 0] += flow[:, :, 0]
    # res[:, :, 1] += flow[:, :, 1]


    return img


def process_roi(
    roi: np.ndarray,
    roi_org: np.ndarray,
    roi_processed: np.ndarray,
    roi_idx: int,
    idx: int,
    num_rois: int,
    fig: Figure,
) -> np.ndarray:
    global axs

    if len(axs) != num_rois:
        # delete old axes:
        for ax in axs:
            ax.remove()

        axs = []
        for i in range(num_rois):
            ax = fig.add_subplot(num_rois + 1, 1, i + 1)
            ax.set_axis_off()
            axs.append(ax)


    img = cv2.cvtColor(roi_org, cv2.COLOR_BGR2GRAY)

    if not roi_idx in last_rois:
        last_rois[roi_idx] = [img]

    flow = cv2.calcOpticalFlowFarneback(
        last_rois[roi_idx][-1],
        img,
        None,
        pyr_scale=0.5,
        levels=3,
        winsize=3,
        iterations=3,
        poly_n=7,
        poly_sigma=1.5,
        flags=0
    )

    last_rois[roi_idx].append(img)
    if len(last_rois[roi_idx]) > 2:
        last_rois[roi_idx].pop(0)

    # flow = (np.round(flow, 4) * 50).astype(np.uint8)

    magn,  ang =  cv2.cartToPolar(flow[..., 0], flow[..., 1])


    res = np.ones((img.shape[0], img.shape[1], 3), np.uint8) * 255
    res[..., 0] = np.round(ang * 180 / np.pi / 2).astype(np.uint8)
    res[..., 2] = cv2.normalize(magn, None, 0, 255, cv2.NORM_MINMAX)
    # res[..., 2] = (np.round(magn, 3) * 10).astype(np.uint8)

    res = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)

    if not roi_idx in densities:
        densities[roi_idx] = []

    densities[roi_idx].append(res[..., 2])

    if len(densities[roi_idx]) > 50:
        densities[roi_idx].pop(0)

    if len(densities[roi_idx]) > 2:
        # print(roi_idx)
        axs[roi_idx].imshow(np.mean(densities[roi_idx], axis=0).astype(np.uint8), cmap="inferno")





    return res


def finalize(fig: Figure) -> dict: ...
