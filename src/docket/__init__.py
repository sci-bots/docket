# coding: utf-8
import types

import cairo
import numpy as np
import pandas as pd
import pango
import pangocairo
import pint

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


UREG = pint.UnitRegistry()


def text_size(text, font='Serif 12'):
    '''
    Parameters
    ----------
    text : str or list-like
        Text to render and calculate size of.

        If a list is provided, calculate the rendered size of each entry in the
        list.

    Returns
    -------
    pd.Series or pd.DataFrame
        If :data:`text` is a string, return Pandas series containing ``width``
        and ``height`` (in pixels).

        If :data:`text` is list-like, return Pandas data frame containing
        ``width`` and ``height`` columns, with each row indexed by the
        corresponding text string.
    '''
    if isinstance(font, types.StringTypes):
        font = pango.FontDescription(font)

    if isinstance(text, types.StringTypes):
        singleton = True
        text = [text]
    else:
        singleton = False

    # Create temporary cairo surface (required for Pango to draw to).
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 1000)
    context = cairo.Context(surface)
    pangocairo_context = pangocairo.CairoContext(context)
    pangocairo_context.set_antialias(cairo.ANTIALIAS_DEFAULT)

    def _get_text_layout(text):
        layout = pangocairo_context.create_layout()
        layout.set_font_description(font)
        layout.set_text(text)
        return layout

    def _get_text_size(text):
        layout = _get_text_layout(text)
        return np.array(layout.get_size(), dtype=float) / pango.SCALE

    df_text_sizes = pd.DataFrame(map(_get_text_size, text),
                                 columns=['width', 'height'], index=text)
    if singleton:
        return df_text_sizes.iloc[0]
    else:
        return df_text_sizes


def pixel_to_pt_scale(text, font='Serif'):
    '''
    Estimate the number of pixels/pt for width and height.

    Parameters
    ----------
    text : str or list-like
        Text to use to compute the pixel to pt scale

    Returns
    -------
    pd.Series
        Pandas series containing ``width`` and ``height`` ratios from pixels to
        pt.
    '''
    if isinstance(font, types.StringTypes):
        font = pango.FontDescription(font)
    else:
        font = font.copy()

    if isinstance(text, types.StringTypes):
        text = [text]

    # Test with a nominal font size to compute relative scale of rendered text
    # of UUID.
    # XXX If this test font size is too small (e.g., 1 or 2), it can lead to
    # scaling errors.  Here we use 12.
    test_size = 12
    font.set_size(test_size * pango.SCALE)
    df_sizes = text_size(text, font)
    dpixel_dpt = df_sizes.max() / test_size
    return dpixel_dpt


def fit_text(text, font='Serif 12', width=None, height=None,
             line_spacing=1.5):
    '''
    Fit the specified text based on the specified font, width, and height.

    Parameters
    ----------
    text : str or list-like
        Text to fit into width/height.
    font : pango.FontDescription or str, optional
        Pango font description or string, e.g., ``"Serif", "Arial 14"``, etc.
    width : float, optional
        Width to fit text into.
    height : float, optional
        Height to fit text into.
    line_spacing : float, optional
        Line height relative to maximum text height.

    Returns
    -------
    pango.FontDescription, pandas.DataFrame
        The font description (including font size) and a Pandas data frame
        containing ``width`` and ``height`` columns of the fitted text
        dimensions, where each row is indexed by the corresponding text string.
    '''
    if isinstance(text, types.StringTypes):
        text = [text]

    font = (pango.FontDescription(font)
            if isinstance(font, types.StringTypes)
            else font.copy())

    dpixel_dpt = pixel_to_pt_scale(text, font=font)

    font_size = None

    def _width():
        return dpixel_dpt.width * font_size

    def _height():
        return dpixel_dpt.height * len(text) * line_spacing * font_size

    if width is None and height is None:
        if font.get_size() == 0:
            raise ValueError('Font size must be given if neither `width` nor '
                             '`height` is specified.')
        font_size = font.get_size() / pango.SCALE
        width = _width()
        height = _height()
    elif width is not None and height is not None:
        font_size = int((width / dpixel_dpt).width)
        if _height() > height:
            font_size = np.ceil(height / (dpixel_dpt.height * len(text)
                                          * line_spacing))
    elif width is not None:
        font_size = int((width / dpixel_dpt).width)
        height = _height()
    elif height is not None:
        font_size = int((height / (len(text) * line_spacing
                                   * dpixel_dpt.height)))
        width = _width()

    font.set_size(int(font_size * pango.SCALE))
    df_sizes = text_size(text, font=font)

    while ((df_sizes.max().width / width) > 1 or
           (len(text) * line_spacing * df_sizes.max().height / height) > 1):
        font_size = 0.99 * font_size
        font.set_size(int(font_size * pango.SCALE))
        df_sizes = text_size(text, font=font)
    return font, df_sizes


def render_text(text, align='left', surface=None, stroke=(0, 0, 0),
                fill=(1, 1, 1), offset=None, **kwargs):
    '''
    Render the specified text.

    Parameters
    ----------
    text : str or list-like
        Text to render.
    align : str, optional
        Text alignment.  One of `left`, `center`, `right`.

        Default: `left`
    surface : pango.Surface, optional
        Pango surface to render on to.

        If not specified, create a :class:`pango.ImageSurface` and
        automatically size to fitted text.
    stroke : float or tuple, optional
        Stroke color, either as grayscale between ``0-1.0``, or RGB tuple.

        Default: ``(0, 0, 0)``, i.e., black.
    fill : float or tuple, optional
        Stroke color, either as grayscale between ``0-1.0``, or RGB tuple.

        Default: ``(1, 1, 1)``, i.e., white.
    offset : tuple, optional
        Translate rendered text by x/y offset.
    width : float or UREG.Quantity, optional
        Width to fit text into.

        If specified as a :class:`UREG.Quantity`, automatically translate to
        pixel units.
    height : float or UREG.Quantity, optional
        Height to fit text into.

        If specified as a :class:`UREG.Quantity`, automatically translate to
        pixel units.
    **kwargs
        Additional keyword arguments passed to :func:`fit_text`.

    Returns
    -------
    shape, surface : UREG.Quantity array-like, pango.Surface
        Shape (i.e., width and height) and surface with rendered text drawn.

        Shape is in units of "pixel", but can be converted to absolute
        dimensions for a given pixels per inch, e.g., for 600 PPI:

            (shape / (600 * docket.UREG.PPI)).to('mm')

        Pango surface can, for example, be written to a `png` file:

            with open('output.png', 'wb') as image_file:
                surface.write_to_png(image_file)

    See also
    --------
    :func:`fit_text`, :func:`render_frame_text`
    '''
    if isinstance(text, types.StringTypes):
        lines = [text]
    else:
        lines = text

    if fill is not None:
        try:
            iter(fill)
        except TypeError:
            fill = 3 * (fill, )
    try:
        iter(stroke)
    except TypeError:
        stroke = 3 * (stroke, )

    font_size = None

    # Extract magnitude of width/height kwargs (if necessary).
    for key_i in ('width', 'height'):
        if key_i in kwargs and isinstance(kwargs[key_i], UREG.Quantity):
            kwargs[key_i] = kwargs[key_i].to('pixel') / UREG.pixel

    if 'font' in kwargs:
        font = kwargs['font']
        if hasattr(font, 'get_size') and font.get_size():
            font_size = font.get_size() * pango.SCALE

    font, df_sizes = fit_text(lines, **kwargs)
    fitted_font_size = font.get_size() * pango.SCALE
    if font_size is None or fitted_font_size < font_size:
        font_size = fitted_font_size

    line_spacing = kwargs.pop('line_spacing', 1.5)
    line_height = int(line_spacing * df_sizes.height.max())

    width = kwargs.pop('width', df_sizes.width.max())
    height = kwargs.pop('height', line_height * len(lines))

    if surface is None:
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, int(np.ceil(width)),
                                     int(height))
    else:
        if hasattr(surface, 'set_height'):
            surface.set_height(height)
            print 'set_height', height
        if hasattr(surface, 'set_width'):
            surface.set_width(width)
            print 'set_width', width

    context = cairo.Context(surface)

    pangocairo_context = pangocairo.CairoContext(context)
    pangocairo_context.set_antialias(cairo.ANTIALIAS_DEFAULT)

    def _get_text_layout(text):
        layout = pangocairo_context.create_layout()
        layout.set_font_description(font)
        layout.set_text(text)
        return layout

    if fill is not None:
        context.set_source_rgb(*fill)
        context.paint()
    context.save()

    if offset is not None:
        context.translate(*offset)

    for line_i, row_i in df_sizes.iterrows():
        context.save()
        if align == 'center':
            context.translate(.5 * (width - row_i.width), 0)
        elif align == 'right':
            context.translate((width - row_i.width), 0)
        layout = _get_text_layout(line_i)
        context.set_source_rgb(*stroke)
        pangocairo_context.update_layout(layout)
        pangocairo_context.show_layout(layout)
        context.restore()
        context.translate(0, line_height)

    context.restore()
    shape = np.array([width, height]) * UREG.pixel
    return shape, surface


def render_frame_text(df_data, width, font='Serif 12', column_padding=.1,
                      surface=None, **kwargs):
    '''
    Parameters
    ----------
    text : pandas.DataFrame
        Table of value to render (as text).
    width : float or UREG.Quantity
        Width to fit text into.

        If specified as a :class:`UREG.Quantity`, automatically translate to
        pixel units.
    font : pango.FontDescription or str, optional
        Pango font description or string, e.g., ``"Serif", "Arial 14"``, etc.
    column_padding : float, optional
        Fraction of total surface width to reserve for padding between columns.

        Default: 0.1, i.e., 10%
    surface : pango.Surface, optional
        Pango surface to render on to.

        If not specified, create a :class:`pango.ImageSurface` and
        automatically size to fitted text.
    **kwargs
        Additional keyword arguments passed to :func:`render_text`.

    Returns
    -------
    shape, surface : UREG.Quantity array-like, pango.Surface
        Shape (i.e., width and height) and surface with rendered text drawn.

        Shape is in units of "pixel", but can be converted to absolute
        dimensions for a given pixels per inch, e.g., for 600 PPI:

            (shape / (600 * docket.UREG.PPI)).to('mm')

        Pango surface can, for example, be written to a `png` file:

            with open('output.png', 'wb') as image_file:
                surface.write_to_png(image_file)

    See also
    --------
    :func:`fit_text`, :func:`render_text`
    '''
    align = kwargs.get('align', 'left')
    line_spacing = kwargs.get('line_spacing', 1.5)

    if isinstance(width, UREG.Quantity):
        width = width.to('pixel') / UREG.pixel

    # Convert table to string representations.
    df_data = df_data.applymap(str)

    columns = df_data.columns
    column_widths = pd.Series({column_i: fit_text(df_data[column_i],
                                                  font=font)[1]
                               .width.max() for column_i in columns})
    column_widths *= width / ((1 + column_padding) * column_widths.sum())
    column_widths = column_widths[columns]

    font = None
    height = None

    for column_i, width_i in column_widths.iteritems():
        lines_i = df_data[column_i]

        font_i, df_sizes_i = fit_text(lines_i, width=width_i,
                                      line_spacing=line_spacing)

        if font is None or font_i.get_size() < font.get_size():
            font = font_i
        height_i = df_sizes_i.height.max() * df_sizes_i.shape[0] * line_spacing
        if height is None or height_i > height:
            height = height_i

    column_widths *= (1 + column_padding)
    column_offsets = column_widths.cumsum()
    column_offsets.values[:] = np.roll(column_offsets.values, 1)
    column_offsets[0] = 0

    if surface is None:
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, int(width),
                                     int(height))

    for column_i, offset_i in column_offsets.iteritems():
        lines_i = df_data[column_i]

        font_i, df_sizes_i = fit_text(lines_i, font=font)

        slack_i = column_widths[column_i] - df_sizes_i.width.max()

        if align == 'center':
            offset_i += .5 * (slack_i)
        elif align == 'right':
            offset_i += slack_i

        # Write text for "i"th column to the common surface.
        shape_i, surface_i = render_text(lines_i, font=font,
                                         offset=(offset_i, 0), align=align,
                                         stroke=1, fill=None,
                                         surface=surface)
    shape = np.array([width, height]) * UREG.pixel
    return shape, surface
