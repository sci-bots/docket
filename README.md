<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Docket](#docket)
  - [Usage](#usage)
    - [Render single string to PNG](#render-single-string-to-png)
    - [Copy resulting surface image to system clipboard](#copy-resulting-surface-image-to-system-clipboard)
    - [Render list of strings](#render-list-of-strings)
    - [Render data table](#render-data-table)
    - [Specify width as `pint` quantity](#specify-width-as-pint-quantity)
  - [Install](#install)
  - [License](#license)
  - [Contributors](#contributors)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Docket #

Render text for stickers, labels, etc.

[**Docket** (*noun*)][0]:

> A writing on a letter or document stating its contents; any statement of
> particulars attached to a package, envelope, etc.; a label or ticket.

-------------------------------------------------------------------------------

Usage
-----

### Render single string to PNG

```python
>>> import docket
>>>
>>> width = 600  # Explicit width in pixels
>>>
>>> shape, surface = docket.render_text('hello, world!', width=width, font='Serif')
>>>
>>> with open('output.png', 'wb') as image_file:
>>>     surface.write_to_png(image_file)
```

The code above results in the following output:  
![Single string](docs/images/single-string.png)

**Note: Any system font name may be specified, e.g., `font='Arial'`.**

The optional **`fill` and `stroke` arguments** (as RGB color tuples) may be used to
change the **background** fill color and **text stroke** color, respectively.

For example:

```python
>>> shape, surface = docket.render_text('hello, world!', width=600,
...                                     fill=(1, 0, 0), stroke=(0, 0, 1))
```

results in the following output:  
![Fill and stroke options](docs/images/fill-stroke-options.png)

### Copy resulting surface image to system clipboard

```python
>>> import docket.util
>>>
>>> docket.util.to_clipboard(surface)
```

### Render list of strings

```python
>>> import docket
>>>
>>> shape, surface = docket.render_text(['hello, world!', 'goodbye!'])
```

### Render data table

```python
>>> import docket
>>> import pandas as pd
>>>
>>>
>>> width = 250  # Explicit width in pixels
>>>
>>> df_data = pd.DataFrame([['Callie', 'Ernst'],
...                         ['Polly', 'Guerrero'],
...                         ['Mildred', 'Jones'],
...                         ['Tomasa', 'Rivera']],
...                         columns=['first_name', 'last_name'])
>>>
>>> shape, surface = docket.render_frame_text(df_data, width)
```

The code above results in the following output:  
![Data table](docs/images/data-table.png)

### Specify width as `pint` quantity

Width/height may be specified as [`pint`][pint] quantities.

For example:

```python
>>> import docket
>>>
>>> # Fit to width of 20 mm (assuming 300 pixels per inch).
>>> width = 20 * docket.UREG.millimeter * 300 * docket.UREG.PPI
>>>
>>> shape, surface = docket.render_text('hello, world!', width=width)
>>> shape
<Quantity([ 236.22047244   72.        ], 'pixel')>
>>> shape.magnitude
array([ 236.22047244,   72.        ])
```

-------------------------------------------------------------------------------

Install
-------

The latest [`docket` release][3] is available as a
[Conda][2] package from the [`sci-bots`][4] channel.

To install `docket` in an **activated Conda environment**, run:

    conda install -c sci-bots -c conda-forge docket

-------------------------------------------------------------------------------

License
-------

This project is licensed under the terms of the [BSD license](/LICENSE.md)

-------------------------------------------------------------------------------

Contributors
------------

 - Christian Fobel ([@sci-bots](https://github.com/sci-bots))


[0]: http://www.dictionary.com/browse/docket
[1]: https://www.arduino.cc/en/Reference/HomePage
[2]: http://www.scons.org/
[3]: https://github.com/sci-bots/docket
[4]: https://anaconda.org/sci-bots
[pint]: https://pint.readthedocs.io/en/latest/
