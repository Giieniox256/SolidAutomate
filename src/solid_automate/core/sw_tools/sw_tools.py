class SwTools:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.sw_app = None

    def connect_to_solidworks(self):
        try:
            self.sw_app = win32.client.Dispatch("SldWorks.Application")
        except Exception as e:
            print(e)
