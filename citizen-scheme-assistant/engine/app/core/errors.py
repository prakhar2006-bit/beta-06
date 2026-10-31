from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException


class APIError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message


def private_headers(request: Request) -> dict[str, str]:
    if request.url.path.startswith(('/api/v1/questionnaire/', '/api/v1/eligibility/', '/api/v1/results/')):
        return {'Cache-Control': 'no-store', 'Pragma': 'no-cache'}
    return {}


def register_errors(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def api_error(request: Request, exc: APIError) -> JSONResponse:
        return JSONResponse(status_code=exc.status, content={"error": {"code": exc.code, "message": exc.message}}, headers=private_headers(request))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Never echo input values, request bodies, or arbitrary validation context.
        # Answer dictionary keys are untrusted too: never reflect them as fields.
        fields = ["body" if error["type"] == "extra_forbidden"
                  else ".".join(str(x) for x in error["loc"][:error["loc"].index("answers")+1]) if "answers" in error["loc"]
                  else ".".join(str(x) for x in error["loc"]) for error in exc.errors()]
        return JSONResponse(status_code=422, content={"error": {
            "code": "INVALID_REQUEST", "message": "Invalid request parameters.", "fields": fields,
        }}, headers=private_headers(request))

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"error": {
            "code": "HTTP_ERROR", "message": "Request could not be completed.",
        }}, headers={**(exc.headers or {}), **private_headers(request)})

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content={"error": {
            "code": "INTERNAL_ERROR", "message": "An internal error occurred.",
        }}, headers=private_headers(request))
