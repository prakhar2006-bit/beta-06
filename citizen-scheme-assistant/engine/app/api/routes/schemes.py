from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, Response

from app.api.routes import demo
from app.core.errors import APIError
from app.db.repository import SchemeRepository, get_repository
from app.schemas.schemes import (DBHealth, ErrorResponse, Language, Languages,
                                Level, SchemeDetail, SchemeList)

router = APIRouter(prefix="/api/v1", responses={
    422: {"model": ErrorResponse}, 503: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
})
Repository = Annotated[SchemeRepository, Depends(get_repository)]


@router.get("/schemes", response_model=SchemeList, tags=["Schemes"])
def list_schemes(repository: Repository, request: Request, response: Response, lang: Language = "en",
                 search: Annotated[str | None, Query(max_length=200)] = None,
                 level: Level | None = None,
                 limit: Annotated[int, Query(ge=1, le=100)] = 20,
                 offset: Annotated[int, Query(ge=0, le=1_000_000)] = 0) -> SchemeList:
    """Published catalogue; opt-in loopback development uses the /demo DTO instead.

    Demo results keep draft/unverified labels and null publication dates. Pagination
    and language parameters are identical; no PostgreSQL access occurs in that mode.
    """
    if demo.is_local_demo(request):
        return demo.local_response(demo.schemes(response,lang,search,level,limit,offset),response)
    return repository.list_schemes(lang, search, level, limit, offset)


@router.get("/schemes/{scheme_id}", response_model=SchemeDetail,
            responses={404: {"model": ErrorResponse}}, tags=["Schemes"])
def get_scheme(repository: Repository, request: Request, response: Response,
               scheme_id: Annotated[str, Path(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", max_length=200)],
               lang: Language = "en") -> SchemeDetail:
    """Published details, or the existing /demo details under the shared local gate."""
    if demo.is_local_demo(request):
        return demo.local_response(demo.detail(response,scheme_id,lang),response)
    scheme = repository.get_scheme(scheme_id, lang)
    if scheme is None:
        raise APIError(404, "SCHEME_NOT_FOUND", "Published scheme not found.")
    return scheme


@router.get("/meta/languages", response_model=Languages, tags=["Metadata"])
def languages() -> Languages:
    return Languages(items=[{"code": "en", "name": "English"}, {"code": "hi", "name": "हिन्दी"}])


@router.get("/meta/health/db", response_model=DBHealth, tags=["Metadata"])
def database_health(repository: Repository) -> DBHealth:
    repository.health()
    return DBHealth()
