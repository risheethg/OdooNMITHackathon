class Response:
    @staticmethod
    def success(data, message: str = "Request successful", status_code: int = 200):
        return {
            "status": "success",
            "message": message,
            "data": data,
            "status_code": status_code
        }
    
    @staticmethod
    def failure(message: str, status_code: int = 400, error_details: dict = None):
        return {
            "status": "failure",
            "message": message,
            "error_details": error_details,
            "status_code": status_code
        }
    
response = Response()