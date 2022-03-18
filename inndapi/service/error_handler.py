class ApiException(Exception):

    def __init__(self, code, message):
        self._code = code
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def message(self):
        return self._message

    def __str__(self):
        return self.__class__.__name__ + ': ' + self.message


class ResourceDoesNotExist(ApiException):
    """Custom exception when resource is not found."""

    def __init__(self, model, model_id):
        message = 'Resource {} {} not found'.format(model.__name__.title(), model_id)
        super().__init__(404, message)


class MissedFields(ApiException):
    """Custom exception when resource is not found."""

    def __init__(self, model, fields):
        message = '{} {}'.format(model.__name__.title(), fields)
        super().__init__(410, message)


class InvalidPassword(ApiException):
    """Custom exception when resource is not found."""

    def __init__(self, model, fields):
        message = '{} {}'.format(model.__name__.title(), fields)
        super().__init__(403, message)