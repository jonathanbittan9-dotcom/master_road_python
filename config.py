class app_config:
    _instance = None
    def __new__(cls):
        if cls._instance == None:
            cls._instance = super().__new__(cls)
            cls._instance.settings = {"debu0g:": True , "port:": "5000"}
        return cls._instance
