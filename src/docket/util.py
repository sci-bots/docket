# coding: utf-8
import matplotlib as mpl
import matplotlib.pyplot
import numpy as np


__all__ = ['plot_surface']


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
    dims = {key_i: getattr(surface, 'get_%s' % key_i)()
            for key_i in ('width', 'height', 'stride')}
    data = (np.fromstring(surface.get_data(), dtype='uint8')
            .reshape(dims['height'], dims['width'], -1)[:, :, 2::-1])

    if axis is None:
        fig, axis = mpl.pyplot.subplots()
    axis.imshow(data)
    return axis
