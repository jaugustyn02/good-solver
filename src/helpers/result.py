class OperationResult(object):
    def __init__(self, success, message=None, data=None):
        self.success = success
        self.message = message
        self.data = data