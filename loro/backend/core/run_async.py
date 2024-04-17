# run_async.py
#
# Change the look of Adwaita, with ease
# Copyright (C) 2022 Gradience Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import sys
import threading
import traceback
import logging

from gi.repository import GLib

from loro.backend.core.log import get_logger


class RunAsync(threading.Thread):
    """
    A class to run tasks asynchronously in a separate thread.

    Args:
        task_func (callable): The function to be executed asynchronously.
        callback (callable, optional): The callback function to be called upon task completion.
        args (tuple, optional): The positional arguments to be passed to the task function.
        kwargs (dict, optional): The keyword arguments to be passed to the task function.
    """

    def __init__(self, task_func, callback=None, *args, **kwargs):
        self.log = get_logger('RunAsync')
        if threading.current_thread() is not threading.main_thread():
            raise AssertionError("AsyncRunner must be created in the main thread.")

        super().__init__(target=self._execute_task, args=(task_func, callback, args, kwargs))
        self.task_func = task_func
        self.callback = callback if callback else lambda result, error: None
        self.start()

    def _execute_task(self, *args, **kwargs):
        try:
            result = self.task_func(*args, **kwargs)
            error = None
        except Exception as e:
            result = None
            error = e
            traceback_info = traceback.format_exc()
            self.log.error(f"Error occurred while running task {self.task_func.__name__}: {error}\n{traceback_info}")
        finally:
            self._invoke_callback(result, error)

    def _invoke_callback(self, result, error):
        GLib.idle_add(self.callback, result, error)

    def run(self):
        self.log.debug(f"Running async task '{self.task_func.__name__}'")
        super().run()
