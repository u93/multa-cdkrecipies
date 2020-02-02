class WrongTypeException(Exception):
    def __init__(self, detail=None, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        print(detail)
