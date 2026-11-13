import numpy as np


def im2col(input_data, filter_h, filter_w, stride=1, pad=0):
    """把 NCHW 输入中的卷积窗口展开为二维数组。"""
    n, channels, height, width = input_data.shape

    out_h = (height + 2 * pad - filter_h) // stride + 1
    out_w = (width + 2 * pad - filter_w) // stride + 1

    padded = np.pad(
        input_data,
        ((0, 0), (0, 0), (pad, pad), (pad, pad)),
        mode="constant",
    )
    windows = np.empty(
        (n, channels, filter_h, filter_w, out_h, out_w),
        dtype=input_data.dtype,
    )

    for fh in range(filter_h):
        for fw in range(filter_w):
            windows[:, :, fh, fw, :, :] = padded[
                :,
                :,
                fh : fh + stride * out_h : stride,
                fw : fw + stride * out_w : stride,
            ]

    return windows.transpose(0, 4, 5, 1, 2, 3).reshape(
        n * out_h * out_w, -1
    )


def col2im(col, input_shape, filter_h, filter_w, stride=1, pad=0):
    """把展开后的窗口梯度累加回 NCHW 输入形状。"""
    n, channels, height, width = input_shape

    out_h = (height + 2 * pad - filter_h) // stride + 1
    out_w = (width + 2 * pad - filter_w) // stride + 1

    windows = np.asarray(col).reshape(
        n, out_h, out_w, channels, filter_h, filter_w
    )
    windows = windows.transpose(0, 3, 4, 5, 1, 2)

    padded = np.zeros(
        (n, channels, height + 2 * pad, width + 2 * pad),
        dtype=windows.dtype,
    )

    for fh in range(filter_h):
        for fw in range(filter_w):
            padded[
                :,
                :,
                fh : fh + stride * out_h : stride,
                fw : fw + stride * out_w : stride,
            ] += windows[:, :, fh, fw, :, :]

    return padded[:, :, pad : pad + height, pad : pad + width]