from model import Container


class BaseContainerException(Exception):
    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(*args, **kwargs)
        self.container_info = None


class CreateContainerError(BaseContainerException):
    def __init__(self, config: dict, *args, **kwargs):
        super(CreateContainerError, self).__init__(*args, **kwargs)
        self.container_info = config
