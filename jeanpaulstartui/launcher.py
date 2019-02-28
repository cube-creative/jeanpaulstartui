import jeanpaulstart
from jeanpaulstartui.hourglass_context import HourglassContext
from jeanpaulstartui.view.launcher_widget import LauncherWidget


def _error_as_status(executor):
    return executor.messages[-1].replace('][', ' : ')


class Launcher(object):

    def __init__(self, width=None, height=None, title=None, tray=True):
        self._view = LauncherWidget(width=width, height=height, title=title, tray=tray)
        self._view.controller = self
        self.batch_directories = list()
        self.tags_filepath = None
        self.username = None
        self.version = "unknown"

    def update(self):
        jeanpaulstart.load_plugins()
        batches = jeanpaulstart.batches_for_user(
            batch_directories=self.batch_directories,
            tags_filepath=self.tags_filepath,
            username=self.username
        )
        self._view.populate_layout(batches)
        self._view.set_version("version " + self.version)

    def show(self):
        self._view.show()

    def batch_clicked(self, batch):
        with HourglassContext(self._view):
            executor = jeanpaulstart.Executor(batch)
            while not executor.has_stopped:
                self._view.set_status_message(executor.next_task.name)
                self._view.set_progress(executor.progress)
                self._view.refresh()
                executor.step()

            if not executor.success:
                self._view.set_status_message(_error_as_status(executor))
            else:
                self._view.set_status_message(self.version)
            self._view.set_progress(0)
            self._view.refresh()
