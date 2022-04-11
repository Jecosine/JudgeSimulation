from model import Container


class Launcher:
    def __init__(self, container_config: dict):
        """
        Args:
            container_config:
        """
        self.container_config = container_config
        self.__current_running_tasks = 0

    def __init_container(self):
        # validation
        containers = {
            i: Container(v) for i, v in self.container_config
        }

    def handle_task(self):
        """
        """
        pass

    def get_task_info(self, tid: int):
        pass

    @property
    def current_running_tasks(self):
        return self.__current_running_tasks

    @current_running_tasks.setter
    def current_running_tasks(self, value):
        self.__current_running_tasks = value


