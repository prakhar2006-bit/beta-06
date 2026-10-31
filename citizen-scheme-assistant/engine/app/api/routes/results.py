from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.eligibility.provider import RuleProvider, get_rule_provider
from app.eligibility.results import explain
from app.schemas.results import ResultRequest, ResultResponse
from app.schemas.schemes import ErrorResponse

router=APIRouter(prefix='/api/v1/results',tags=['Results'],responses={
    409:{'model':ErrorResponse},422:{'model':ErrorResponse},503:{'model':ErrorResponse},500:{'model':ErrorResponse}})


@router.post('/explain',response_model=ResultResponse)
def explain_result(request:ResultRequest,response:Response,provider:Annotated[RuleProvider,Depends(get_rule_provider)]):
    response.headers['Cache-Control']='no-store'
    response.headers['Pragma']='no-cache'
    return explain(request,provider,as_of=datetime.now(timezone(timedelta(hours=5,minutes=30))).date())
