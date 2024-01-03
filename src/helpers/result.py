class OperationResult(object):
    def __init__(self, success: bool, message:str =None, data=None):
        self.success = success
        self.message = message
        self.data = data