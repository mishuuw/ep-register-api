from fastapi import HTTPException


class FeatureHttpException(HTTPException):
    def __init__(
        self,
        lang="en",
    ):
        message = "error msg"
        if lang == "ru":
            message = "сообщ об ошибке"
        super().__init__(status_code=400, detail=message)
