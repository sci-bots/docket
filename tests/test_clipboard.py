import nose.tools
import platform
import docket
import docket.util


def test_clipboard():
    shape, surface = docket.render_text('hello, world!')

    if platform.system() == 'Windows':
        docket.util.to_clipboard(surface)
    else:
        nose.tools.assert_raises(RuntimeError, docket.util.to_clipboard,
                                 surface)
