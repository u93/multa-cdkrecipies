class WrongTypeException(Exception):
    """
    Designed to be raised when the wrong type of element is passed.
    """

    def __init__(self, detail=None, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        print(detail)


class WrongRuntimePassed(Exception):
    """
    Designed to be raised when the wrong RUNTIME is passed to a Lambda Function.
    """

    def __init__(self, detail=None, tb=None, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        print(detail)
        print(tb)
