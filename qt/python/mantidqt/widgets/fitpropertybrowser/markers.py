# Mantid Repository : https://github.com/mantidproject/mantid
#
# Copyright &copy; 2018 ISIS Rutherford Appleton Laboratory UKRI,
#     NScD Oak Ridge National Laboratory, European Spallation Source
#     & Institut Laue - Langevin
# SPDX - License - Identifier: GPL - 3.0 +
from qtpy.QtCore import Qt, QObject, Signal
from qtpy.QtGui import QCursor

from matplotlib.path import Path
from matplotlib.patches import PathPatch


class VerticalMarker(QObject):
    """
    An interactive marker displayed as a vertical line.
    """

    x_moved = Signal(float)

    def __init__(self, canvas, color, x, y0=None, y1=None, line_width=1.0, picker_width=5, line_style='-'):
        """
        Init the marker.
        :param canvas: A MPL canvas.
        :param color: An MPL colour value
        :param x: The x coordinate (data) of the marker.
        :param y0: The y coordinate (data) of the bottom end of the marker. Default is None which means dynamically
            set it to the current lowest y value displayed.
        :param y1: The y coordinate (data) of the top end of the marker. Default is None which means dynamically
            set it to the current highest y value displayed.
        :param line_width: The line width (pixels).
        :param picker_width: The picker sensitivity (pixels).
        :param line_style: An MPL line style value.
        """
        super(VerticalMarker, self).__init__()
        self.ax = canvas.figure.get_axes()[0]
        self.x = x
        self.y0 = y0
        self.y1 = y1
        y0, y1 = self._get_y0_y1()
        path = Path([(x, y0), (x, y1)], [Path.MOVETO, Path.LINETO])
        self.patch = PathPatch(path, facecolor='None', edgecolor=color, picker=picker_width,
                               linewidth=line_width, linestyle=line_style, animated=True)
        self.ax.add_patch(self.patch)
        self.is_moving = False

    def _get_y0_y1(self):
        """
        Calculate the current y coordinates of the line ends.
        :return: Tuple y0, y1.
        """
        if self.y0 is None or self.y1 is None:
            y0, y1 = self.ax.get_ylim()
        if self.y0 is not None:
            y0 = self.y0
        if self.y1 is not None:
            y1 = self.y1
        return y0, y1

    def remove(self):
        """
        Remove this marker from the canvas.
        """
        self.patch.remove()

    def redraw(self):
        """
        Redraw this marker.
        """
        y0, y1 = self._get_y0_y1()
        vertices = self.patch.get_path().vertices
        vertices[0] = self.x, y0
        vertices[1] = self.x, y1
        self.ax.draw_artist(self.patch)

    def get_x_in_pixels(self):
        """
        Get the x coordinate in screen pixels.
        """
        x_pixels, _ = self.patch.get_transform().transform((self.x, 0))
        return x_pixels

    def is_above(self, x, y):
        """
        Check if a mouse positioned at (x, y) is over this marker.
        :param x: An x mouse coordinate.
        :param y: An y mouse coordinate.
        :return: True or False.
        """
        x_pixels, y_pixels = self.patch.get_transform().transform((x, y))
        if self.y0 is not None and y < self.y0:
            return False
        if self.y1 is not None and y > self.y1:
            return False
        return abs(self.get_x_in_pixels() - x_pixels) < 3

    def mouse_move_start(self, x, y):
        """
        Start moving this marker if (x, y) is above it. Ignore otherwise.
        :param x: An x mouse coordinate.
        :param y: An y mouse coordinate.
        """
        self.is_moving = self.is_above(x, y)

    def mouse_move_stop(self):
        """
        Stop moving.
        """
        self.is_moving = False

    def mouse_move(self, x, y=None):
        """
        Move this marker to a new position if movement had been started earlier by a call to mouse_move_start(x, y)
        :param x: An x mouse coordinate.
        :param y: An y mouse coordinate.
        :return: True if moved or False if stayed at the old position.
        """
        if self.is_moving and x is not None:
            self.x = x
            self.x_moved.emit(x)
            return True
        return False

    def get_cursor_at_y(self, y):
        """
        Get an override cursor for an y coordinate given that the x == self.x
        :param y: A y coordinate.
        :return: QCursor or None.
        """
        return QCursor(Qt.SizeHorCursor)

    def override_cursor(self, x, y):
        """
        Get the override cursor for mouse position (x, y)
        :param x: An x mouse coordinate.
        :param y: An y mouse coordinate.
        :return: QCursor or None.
        """
        if self.y0 is not None and y < self.y0:
            return None
        if self.y1 is not None and y > self.y1:
            return None
        if self.is_moving or self.is_above(x, y):
            return self.get_cursor_at_y(y)
        return None


class CentreMarker(VerticalMarker):
    """
    A marker for a peak centre.
    """

    selected_color = 'red'
    deselected_color = 'grey'

    def __init__(self, canvas, x, y0, y1):
        """
        Init the marker.
        :param canvas: A MPL canvas.
        :param x: The x coordinate (data) of the marker.
        :param y0: The y coordinate (data) of the bottom end of the marker.
        :param y1: The y coordinate (data) of the top end of the marker.
        """
        VerticalMarker.__init__(self, canvas, self.deselected_color, x, y0, y1)
        self.is_at_top = False

    def _is_at_top(self, y):
        """
        Check if the mouse at position (self.x, y) points to the top end of the marker. There is some tolerance.
        :param y: A y coordinate.
        :return: True or False.
        """
        _, y1_pixels = self.patch.get_transform().transform((0, self.y1))
        _, y_pixels = self.patch.get_transform().transform((0, y))
        return abs(y1_pixels - y_pixels) < 10

    def get_cursor_at_y(self, y):
        """
        Get an override cursor for an y coordinate given that the x == self.x
        :param y: A y coordinate.
        :return: QCursor or None.
        """
        is_at_top = self.is_at_top if self.is_moving else self._is_at_top(y)
        return QCursor(Qt.SizeAllCursor) if is_at_top else VerticalMarker.get_cursor_at_y(self, y)

    def mouse_move_start(self, x, y):
        """
        Start moving marker.
        """
        VerticalMarker.mouse_move_start(self, x, y)
        self.is_at_top = self._is_at_top(y)

    def mouse_move_stop(self):
        """
        Stop moving marker.
        """
        VerticalMarker.mouse_move_stop(self)
        self.is_at_top = False

    def mouse_move(self, x, y=None):
        """
        Move marker.
        :return: True if it was actually moved.
        """
        if not self.is_moving:
            return False
        if self.is_at_top:
            self.y1 = y
        self.x = x
        return True

    def height(self):
        """
        Get the height of the marker (== peak height).
        """
        return self.y1 - self.y0

    def set_height(self, height):
        """
        Set height - change the top end y coordinate only.
        :param height: A new height.
        """
        self.y1 = self.y0 + height

    def select(self):
        """
        Mark as selected.
        """
        self.patch.set_edgecolor(self.selected_color)

    def deselect(self):
        """
        Remove selection.
        """
        self.patch.set_edgecolor(self.deselected_color)


class WidthMarker(VerticalMarker):
    """
    A peak width marker (left or right).
    """

    def __init__(self, canvas, x):
        VerticalMarker.__init__(self, canvas, 'red', x, line_style='--')


class PeakMarker(QObject):
    """
    A peak marker. Consists of a CentreMarker and two WidthMarkers placed at half width at half peak maximum on either
    side of the centre line.
    """

    peak_moved = Signal(int, float, float)
    fwhm_changed = Signal(int, float)

    def __init__(self, canvas, peak_id, x, y_top, y_bottom, fwhm):
        """
        Init the marker.
        :param canvas: The MPL canvas.
        :param peak_id: A unique peak id.
        :param x: Peak centre.
        :param y_top: Peak's top.
        :param y_bottom: Peaks bottom (background level).
        :param fwhm: A full width at half maximum.
        """
        super(PeakMarker, self).__init__()
        self.peak_id = peak_id
        self.centre_marker = CentreMarker(canvas, x, y0=y_bottom, y1=y_top)
        self.left_width = WidthMarker(canvas, x - fwhm / 2)
        self.right_width = WidthMarker(canvas, x + fwhm / 2)
        self.is_selected = False

    def redraw(self):
        """
        Redraw the marker.
        """
        self.centre_marker.redraw()
        if self.is_selected:
            self.left_width.redraw()
            self.right_width.redraw()

    def override_cursor(self, x, y):
        """
        Get the override cursor for mouse position (x, y)
        :param x: An x mouse coordinate.
        :param y: An y mouse coordinate.
        :return: QCursor or None.
        """
        cursor = self.centre_marker.override_cursor(x, y)
        if self.is_selected:
            if cursor is None:
                cursor = self.left_width.override_cursor(x, y)
            if cursor is None:
                cursor = self.right_width.override_cursor(x, y)
        return cursor

    def mouse_move_start(self, x, y):
        """
        Start moving an element of this marker if it's under the cursor.
        :param x: An x mouse coordinate.
        :param y: An y mouse coordinate.
        """
        self.centre_marker.mouse_move_start(x, y)
        if self.centre_marker.is_moving:
            self.left_width.is_moving = True
            self.right_width.is_moving = True
        else:
            self.left_width.mouse_move_start(x, y)
            self.right_width.mouse_move_start(x, y)

    def mouse_move_stop(self):
        """
        Stop moving.
        """
        if self.centre_marker.is_moving:
            self.left_width.is_moving = False
            self.right_width.is_moving = False
        else:
            self.left_width.mouse_move_stop()
            self.right_width.mouse_move_stop()
        self.centre_marker.mouse_move_stop()

    def mouse_move(self, x, y):
        """
        Move an element of this marker if it's started moving.
        :param x: An x mouse coordinate.
        :param y: An y mouse coordinate.
        """
        moved = self.centre_marker.mouse_move(x, y)
        if moved:
            dx = (self.right_width.x - self.left_width.x) / 2
            self.left_width.mouse_move(x - dx, y)
            self.right_width.mouse_move(x + dx, y)
            self.peak_moved.emit(self.peak_id, x, self.centre_marker.height())
        else:
            moved = self.left_width.mouse_move(x, y)
            if moved:
                self.right_width.x = 2 * self.centre_marker.x - x
            else:
                moved = self.right_width.mouse_move(x, y)
                if moved:
                    self.left_width.x = 2 * self.centre_marker.x - x
            if self.left_width.x > self.right_width.x:
                tmp = self.right_width.x
                self.right_width.x = self.left_width.x
                self.left_width.x = tmp
            if moved:
                self.fwhm_changed.emit(self.peak_id, self.fwhm())
        return moved

    @property
    def is_moving(self):
        """
        Check if this marker is moving as a whole.
        """
        return self.centre_marker.is_moving

    def centre(self):
        """
        Get peak centre.
        """
        return self.centre_marker.x

    def height(self):
        """
        Get peak height.
        """
        return self.centre_marker.height()

    def fwhm(self):
        """
        Get peak FWHM.
        """
        return self.right_width.x - self.left_width.x

    def update_peak(self, centre, height, fwhm):
        """
        Update this marker.
        :param centre: A new peak centre.
        :param height: A new peak height.
        :param fwhm: A new peak FWHM.
        """
        self.centre_marker.x = centre
        self.centre_marker.set_height(height)
        dx = fwhm / 2
        self.left_width.x = centre - dx
        self.right_width.x = centre + dx

    def select(self):
        """
        Select this peak.
        """
        self.centre_marker.select()
        self.is_selected = True

    def deselect(self):
        """
        Deselect this peak.
        """
        self.centre_marker.deselect()
        self.is_selected = False

    def remove(self):
        """
        Remove this peak marker from the canvas.
        """
        self.centre_marker.remove()
        self.left_width.remove()
        self.right_width.remove()
