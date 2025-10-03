import os
import json
import logging


from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .window_position import WindowPosition


WINDOW_CACHE_FILE = "jps_window_geometry.json"


def restore_window_geometry(main_window):
    cache = _get_cache()

    if cache:
        WindowPosition.restore(main_window, cache)

    if not cache or window_is_almost_out_of_screen(main_window):
        _set_default_window_position(main_window)


def save_window_geometry(main_window):
    if window_is_almost_out_of_screen(main_window):
        return

    window_geometry_cache_filepath = _get_window_geometry_cache_filepath()

    os.makedirs(os.path.dirname(window_geometry_cache_filepath), exist_ok=True)

    try:
        # ensure serializable geometry_cache data can be found
        geometry_cache = {
            'window': WindowPosition.save(main_window)
        }
        json.dumps(geometry_cache)
    except Exception as exc:
        # Type Error is raised if object is not serializable.
        logging.error("Fail to get json serializable geomtry_cache data.  exc: {}".format(exc))
        return

    try:
        with open(window_geometry_cache_filepath, 'w') as cache_file:
            json.dump(geometry_cache, cache_file)
    except OSError:
        logging.error("JPS UI: Can't write window geometry in cache file.")


def window_is_almost_out_of_screen(main_window):
    """ Check if the window is almost out of the screen.

    Args:
        main_window (QMainWindow): The main window.

    Returns:
        bool: True if the window is almost out of the screen, False otherwise.
    """
    screen = QApplication.primaryScreen()
    window_geometry = main_window.geometry()
    window_center = window_geometry.center()

    for screen in QApplication.screens():
        screen_geometry = screen.geometry()
        if screen_geometry.contains(window_center):
            return False

    return True


def _get_cache():
    window_geometry_cache_filepath = _get_window_geometry_cache_filepath()
    logging.info("searching window_cache from pref: {}".format(window_geometry_cache_filepath))

    if not os.path.isfile(window_geometry_cache_filepath):
        return None

    try:
        with open(window_geometry_cache_filepath, 'r') as cache_file:
            cache = json.load(cache_file)
            if not cache.get('window'):
                return None

            return cache['window']

    except json.decoder.JSONDecodeError:
        logging.error("JPS UI: Can't decode geometry cache file.")

        try:
            # If the file is empty, json can't decode it and raise a JSONDecodeError
            #    by ignoring the error, JPS starts, but the file may remain unwritable.
            # Try to remove it to avoid this issue.
            os.remove(window_geometry_cache_filepath)
        except Exception:
            logging.error("Can't delete corrupted geometry cache file")

        return None

    except OSError as exc:
        logging.error("JPS UI: Can't read window geometry cache file.  exc: {}".format(exc))
        return None

    except Exception as exc:
        # anyway, the geometry cache loading shouldn't stop JPS from starting
        logging.error("JPS UI: Fail to get geometry cache.  exc: {}".format(exc))
        return None



def _set_default_window_position(main_window):
    frame_geometry = main_window.frameGeometry()
    center_point = QApplication.primaryScreen().availableGeometry().center()
    frame_geometry.moveCenter(center_point)
    main_window.move(frame_geometry.topLeft())


def _get_window_geometry_cache_filepath():
    return os.path.join(
        os.path.expanduser('~/.jeanpaulstart'),
        WINDOW_CACHE_FILE
    ).replace('\\', '/')
