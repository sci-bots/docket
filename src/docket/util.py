# coding: utf-8
import io
import platform

from PIL import Image
import numpy as np


__all__ = ['plot_surface']


def to_array(surface):
    '''
    Convert Pango image surface to numpy array.

    Parameters
    ----------
    surface : pango.ImageSurface
        Pango image surface.

    Returns
    -------
    numpy.array
        Image RGB array.
    '''
    dims = {key_i: getattr(surface, 'get_%s' % key_i)()
            for key_i in ('width', 'height', 'stride')}
    return (np.fromstring(surface.get_data(), dtype='uint8')
            .reshape(dims['height'], dims['width'], -1)[:, :, 2::-1])


def plot_surface(surface, axis=None):
    '''
    Draw Pango image surface to Matplotlib axis.

    Parameters
    ----------
    surface : pango.ImageSurface
        Pango image surface to draw.

    Returns
    -------
    matplotlib.axes._subplots.AxesSubplot
        Matplotlib axis containing drawn image.
    '''
    import matplotlib as mpl
    import matplotlib.pyplot

    data = to_array(surface)
    if axis is None:
        fig, axis = mpl.pyplot.subplots()
    axis.imshow(data)
    return axis
