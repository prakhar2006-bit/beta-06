from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.core.errors import APIError
from app.eligibility.engine import InvalidAnswers, evaluate
from app.eligibility.provider import RuleProvider, get_rule_provider
from app.schemas.eligibility import EvaluationRequest, EvaluationResponse, RuleSet
from app.schemas.schemes import ErrorResponse

router = APIRouter(prefix='/api/v1/eligibility', tags=['Eligibility'], responses={
    422: {'model': ErrorResponse}, 503: {'model': ErrorResponse}, 500: {'model': ErrorResponse}})


@router.post('/evaluate', response_model=EvaluationResponse)
def evaluate_eligibility(request: EvaluationRequest, response: Response,
                         provider: Annotated[RuleProvider, Depends(get_rule_provider)]) -> EvaluationResponse:
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    rules = provider.get_rule_set(request.scheme_id)
    if rules is not None and (not isinstance(rules, RuleSet) or rules.scheme_id != request.scheme_id):
        raise APIError(503, 'RULE_SET_INVALID', 'Approved rule definitions are unavailable.')
    try:
        return evaluate(rules, request.scheme_id, request.answers, request.language,
                        as_of=datetime.now(timezone(timedelta(hours=5, minutes=30))).date())
    except InvalidAnswers:
        # Do not include citizen values or allow answer-controlled error messages.
        raise APIError(422, 'INVALID_ANSWERS', 'Answer fields or types do not match the reviewed questions.') from None
