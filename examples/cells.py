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

    # if len(axs) != 2 * num_rois:
    #     # delete old axes:
    #     for ax in axs:
    #         ax.remove()
    #
    #     axs = []
    #     for i in range(2 * num_rois):
    #         ax = fig.add_subplot(num_rois + 1, 2, i + 1)
    #         if i % 2 == 0:
    #             ax.set_axis_off()
    #         axs.append(ax)

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

    magn, ang =  cv2.cartToPolar(flow[..., 0], flow[..., 1])


    res = np.ones((img.shape[0], img.shape[1], 3), np.uint8) * 255
    res[..., 0] = np.round(ang * 180 / np.pi / 2).astype(np.uint8)
    res[..., 2] = cv2.normalize(magn, None, 0, 255, cv2.NORM_MINMAX)
    # res[..., 2] = (np.round(magn, 3) * 10).astype(np.uint8)


    res = cv2.cvtColor(res, cv2.COLOR_HSV2BGR)

    if not roi_idx in densities:
        densities[roi_idx] = []

    # median_ang = np.median(ang)
    # res[np.abs(ang - median_ang) < 1.0, 2] = 0
    densities[roi_idx].append(res[..., 2])

    if len(densities[roi_idx]) > 50:
        densities[roi_idx].pop(0)

    if len(densities[roi_idx]) > 2:
        axs[2 * roi_idx].imshow(np.mean(densities[roi_idx], axis=0).astype(np.uint8), cmap="inferno")


    binary = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    binary = cv2.normalize(binary, None, 0, 255, cv2.NORM_MINMAX)
    binary = cv2.threshold(binary, 2, 255, cv2.THRESH_TRIANGLE)[1]
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, np.ones((19, 19), np.uint8))

    contours = list(cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0])
    contours.sort(key=cv2.contourArea, reverse=True)

    # try:
    #     ellipse = cv2.fitEllipse(contours[0])
    #
    #     ellipse_center_x = ellipse[0][0]
    #     ellipse_center_y = ellipse[0][1]
    #
    #     distances = []
    #     magnitudes = []
    #     mean_magnitude = np.mean(densities[roi_idx], axis=0)
    #     for x in range(roi_org.shape[0]):
    #         for y in range(roi_org.shape[1]):
    #             d = np.sqrt((x - ellipse_center_x) ** 2 + (y - ellipse_center_y) ** 2) 
    #             distances.append(d / (2 * ellipse[0][1]))
    #             magnitudes.append(mean_magnitude[x, y])
    #
    #     axs[2 * roi_idx + 1].clear()
    #     axs[2 * roi_idx + 1].scatter(distances, magnitudes, marker=".")
    #
    # except Exception as e:
    #     print(e)


    return res


def finalize(fig: Figure) -> dict: ...
