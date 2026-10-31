from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.eligibility import questionnaire
from app.eligibility.provider import RuleProvider, get_rule_provider
from app.schemas.questionnaire import AnswerRequest, NextRequest, QuestionnaireResponse, StartRequest
from app.schemas.schemes import ErrorResponse

router = APIRouter(prefix='/api/v1/questionnaire', tags=['Questionnaire'], responses={
    409: {'model': ErrorResponse}, 422: {'model': ErrorResponse},
    503: {'model': ErrorResponse}, 500: {'model': ErrorResponse}})
Provider = Annotated[RuleProvider, Depends(get_rule_provider)]


def context(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    return datetime.now(timezone(timedelta(hours=5, minutes=30))).date()


@router.post('/start', response_model=QuestionnaireResponse)
def start(request: StartRequest, response: Response, provider: Provider):
    return questionnaire.start(request, provider, as_of=context(response))


@router.post('/next', response_model=QuestionnaireResponse)
def next_question(request: NextRequest, response: Response, provider: Provider):
    return questionnaire.next_question(request.state, provider, as_of=context(response))


@router.post('/answer', response_model=QuestionnaireResponse)
def answer(request: AnswerRequest, response: Response, provider: Provider):
    return questionnaire.answer(request, provider, as_of=context(response))
