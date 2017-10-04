# coding: utf-8
import io

from PIL import Image
import docket
import nose.tools
import numpy as np
import pandas as pd


def test_render_font_size():
    shape, surface = docket.render_text('hello, world!', font='Serif 12')

    with io.BytesIO() as image_output:
        surface.write_to_png(image_output)
        image_output.seek(0)
        with Image.open(image_output) as image:
            pass

    np.testing.assert_array_equal(shape, image.size)


def test_render_frame():
    width = 600  # Explicit width in pixels

    df_data = pd.DataFrame([['Callie', 'Ernst'],
                            ['Polly', 'Guerrero'],
                            ['Mildred', 'Jones'],
                            ['Tomasa', 'Rivera']],
                           columns=['first_name', 'last_name'])

    shape, surface = docket.render_frame_text(df_data, 600, font='Serif')

    with io.BytesIO() as image_output:
        surface.write_to_png(image_output)
        image_output.seek(0)
        with Image.open(image_output) as image:
            pass

    # Verify output image (integer) size matches surface size.
    np.testing.assert_array_almost_equal(shape, image.size, decimal=0)
    nose.tools.assert_less_equal(shape[0].magnitude, width)


def test_render_width_pixels():
    width = 600  # Explicit width in pixels

    shape, surface = docket.render_text('hello, world!', width=width)

    with io.BytesIO() as image_output:
        surface.write_to_png(image_output)
        image_output.seek(0)
        with Image.open(image_output) as image:
            pass

    np.testing.assert_array_equal(shape, image.size)
    nose.tools.assert_less_equal(shape[0].magnitude, width)


def test_render_multiple_lines():
    width = 600  # Explicit width in pixels

    shape, surface = docket.render_text(['hello, world!'], width=width)
    shape_multi, surface_multi = docket.render_text(['hello, world!'] * 4,
                                                    width=width)

    # Verify height of 4 lines output is roughly 4 times the height of a single
    # line rendered.
    np.testing.assert_almost_equal(shape[1] * 4 / docket.UREG.pixel,
                                   shape_multi[1] / docket.UREG.pixel)


def test_render_width_mm():
    # Fit to width of 20 mm (assuming 300 pixels per inch).
    width = 20 * docket.UREG.millimeter * 300 * docket.UREG.PPI

    shape, surface = docket.render_text('hello, world!', width=width)

    with io.BytesIO() as image_output:
        surface.write_to_png(image_output)
        image_output.seek(0)
        with Image.open(image_output) as image:
            pass

    # Verify output image (integer) size matches surface size.
    np.testing.assert_array_almost_equal(shape, image.size, decimal=0)

    # Verify rendered surface width is no greater than the target width.
    nose.tools.assert_less_equal(shape[0], width.to('pixel'))


def test_render_width_inch():
    # Fit to width of 20 mm (assuming 300 pixels per inch).
    width = 2.5 * docket.UREG.inch * 300 * docket.UREG.PPI

    shape, surface = docket.render_text('hello, world!', width=width)

    with io.BytesIO() as image_output:
        surface.write_to_png(image_output)
        image_output.seek(0)
        with Image.open(image_output) as image:
            pass

    # Verify output image (integer) size matches surface size.
    np.testing.assert_array_almost_equal(shape, image.size, decimal=0)

    # Verify rendered surface width is no greater than the target width.
    nose.tools.assert_less_equal(shape[0], width.to('pixel'))
