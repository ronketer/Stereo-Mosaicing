import cv2

ST_PARAMS = dict(
    maxCorners=500,
    qualityLevel=0.03,
    minDistance=30,
    blockSize=7,
)

LK_PARAMS = dict(
    winSize=(15, 15),
    maxLevel=3,
    criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
)

MOSAIC_CONFIG = {
    "MIN_TRACKING_POINTS": 150,
    "STAB_PADDING_H": 20,
    "STAB_OFFSET_Y": 10,
    "STRIP_OVERLAP": 4,
    "SLIT_START_RATIO": 0.1,
    "SLIT_WIDTH_RATIO": 0.8,
}
