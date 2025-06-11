class GetCustomersResponse:
    def __init__(self, response: dict):
        self.count: int = response['count']
        self.not_returned_count: int = response['notReturnedCount']
        self.payload: list = response['customers']

    def __repr__(self):
        return str(self.payload)
