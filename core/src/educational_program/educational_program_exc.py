from fastapi import HTTPException  # noqa


class DeletionRestrictedHttpException(HTTPException):
    def __init__(
        self,
        lang="en",
    ):

        message = "Deletion restricted due to deletion policy"
        if lang == "ru":
            message = "Удаление ограничено из-за политики удаления"
        super().__init__(status_code=409, detail=message)
