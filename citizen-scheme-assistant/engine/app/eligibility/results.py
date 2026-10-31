"""Source-backed presentation; eligibility comes only from the existing evaluator."""
from urllib.parse import urlsplit

from app.core.errors import APIError
from app.db.guidance import GuidanceContext, guidance_digest
from app.eligibility.questionnaire import next_question
from app.schemas.eligibility import SourceReference
from app.schemas.results import (ApplicationResult, ApplicationURL, BenefitResult, DisplayText,
    DocumentResult, GuidanceSection, ResultResponse)

MESSAGES={
 'en':{
  'notice':'This assessment does not guarantee government approval, enrolment or benefit disbursement.',
  'available':'Reviewed published information is available.',
  'partial':'Some information is unavailable or lacks reviewed wording or provenance.',
  'unavailable':'Verified information is unavailable. Confirm with the official implementing agency.',
  'url_unavailable':'No verified application URL is available. Do not treat a source citation as an application link.',
  'url_available':'A reviewed application URL is available; current application acceptance is not guaranteed.',
  'required':'The published guidance lists this document as required.',
  'conditional':'This document is required only under the stated condition.',
  'optional':'The published guidance lists this document as optional.',
  'unknown':'Whether this document is required needs verification.'},
 'hi':{
  'notice':'यह आकलन सरकारी मंज़ूरी, नामांकन या लाभ के भुगतान की गारंटी नहीं देता।',
  'available':'समीक्षित प्रकाशित जानकारी उपलब्ध है।',
  'partial':'कुछ जानकारी उपलब्ध नहीं है या उसके शब्दांकन अथवा स्रोत की समीक्षा बाकी है।',
  'unavailable':'सत्यापित जानकारी उपलब्ध नहीं है। आधिकारिक कार्यान्वयन संस्था से पुष्टि करें।',
  'url_unavailable':'सत्यापित आवेदन लिंक उपलब्ध नहीं है। स्रोत के संदर्भ को आवेदन लिंक न मानें।',
  'url_available':'समीक्षित आवेदन लिंक उपलब्ध है; वर्तमान में आवेदन स्वीकार होने की गारंटी नहीं है।',
  'required':'प्रकाशित मार्गदर्शन में यह दस्तावेज़ आवश्यक बताया गया है।',
  'conditional':'यह दस्तावेज़ केवल बताई गई शर्त लागू होने पर आवश्यक है।',
  'optional':'प्रकाशित मार्गदर्शन में यह दस्तावेज़ वैकल्पिक बताया गया है।',
  'unknown':'इस दस्तावेज़ की आवश्यकता की पुष्टि बाकी है।'}
}


def system(key,language):
    return DisplayText(text=MESSAGES[language][key],requested_language=language,content_language=language,
                       review_status='system',origin='system')


def content(text,actual,requested,source_id,origin='source_text'):
    if not text or not text.strip() or actual != requested and actual != 'en':
        return DisplayText(requested_language=requested)
    return DisplayText(text=text,requested_language=requested,content_language=actual,
        translation_fallback=actual!=requested,review_status='reviewed',origin=origin,
        is_official_translation=origin=='official',source_ids=(source_id,))


def section(items,total,language,reason='NO_REVIEWED_PUBLISHED_INFORMATION'):
    status='available' if items and len(items)==total else 'partial' if items else 'unavailable'
    return GuidanceSection(status=status,reason_code=None if status=='available' else reason,
                           message=system(status,language),items=tuple(items))


def valid_url(url,hosts):
    try:
        parsed=urlsplit(url or '')
        return (parsed.scheme=='https' and parsed.hostname in hosts and not parsed.username
                and not parsed.password and parsed.port in (None,443))
    except ValueError:return False


def explain(request,provider,*,as_of):
    # Enforces the existing policy fingerprint, typed answer state and re-evaluation.
    questionnaire=next_question(request.state,provider,as_of=as_of)
    evaluation=questionnaire.evaluation
    language=request.state.language
    name=DisplayText(requested_language=language)
    sources={s.reference_id:s for s in evaluation.sources}
    benefits=[];documents=[];applications=[];urls=[]
    totals={'benefits':0,'documents':0,'application_routes':0}
    reason='GUIDANCE_UNAVAILABLE'
    context=None
    policy=evaluation.policy_review
    if (evaluation.rule_set_version and policy.publication_status=='published'
            and policy.approval_status=='approved' and policy.execution_enabled and policy.complete
            and policy.applicable and not policy.blockers):
        getter=getattr(provider,'get_guidance',None)
        if callable(getter):context=getter(evaluation.scheme_id,evaluation.rule_set_version)
    if context is not None:
        if not isinstance(context,GuidanceContext) or context.snapshot.scheme_id != evaluation.scheme_id:
            raise APIError(503,'GUIDANCE_INVALID','Published guidance is unavailable.')
        snapshot=context.snapshot
        all_rows=(snapshot.translations,snapshot.benefits,snapshot.documents,snapshot.application_routes,snapshot.sources)
        if any(len({r.id for r in rows})!=len(rows) for rows in all_rows):
            raise APIError(503,'GUIDANCE_INVALID','Published guidance is unavailable.')
        evidence={}
        for source in snapshot.sources:
            if source.last_checked_date>as_of or not valid_url(source.original_url,context.allowed_source_hosts):continue
            try:
                reference=SourceReference(reference_id=str(source.id),original_url=source.original_url,title=source.source_title,
                    locator=source.locator,last_checked_date=source.last_checked_date,content_sha256=source.content_sha256)
            except ValueError:continue
            evidence[source.id]=reference

        def cite(source_id):
            ref=evidence.get(source_id)
            if ref is None:return None
            if ref.reference_id in sources and sources[ref.reference_id]!=ref:
                raise APIError(409,'POLICY_CHANGED','The policy changed. Start a new questionnaire.')
            sources[ref.reference_id]=ref
            return ref

        for preferred in (language,'en') if language!='en' else ('en',):
            translation=next((t for t in snapshot.translations if t.language_code==preferred
                and t.review_status=='reviewed' and t.evidence_id in evidence and t.title.strip()),None)
            if translation:
                reference=cite(translation.evidence_id)
                name=content(translation.title,preferred,language,reference.reference_id,translation.translation_origin)
                break
        totals={key:len(getattr(snapshot,key)) for key in totals}
        review=context.approval
        valid=(review is not None and review.reviewed_on<=as_of<=review.valid_until
               and review.snapshot_sha256==guidance_digest(snapshot))
        if valid:
            for key in totals:
                if {r.item_id for r in getattr(review,key)}-{r.id for r in getattr(snapshot,key)}:
                    valid=False
        if valid:
            reason='ITEM_REVIEW_OR_PROVENANCE_UNAVAILABLE'
            for key in totals:
                annotations={r.item_id:r for r in getattr(review,key)}
                for row in sorted(getattr(snapshot,key),key=lambda r:(r.item_key,str(r.id))):
                    annotation=annotations.get(row.id)
                    if annotation is None or row.evidence_id not in evidence:continue
                    text=row.description if key=='benefits' else row.document_type if key=='documents' else row.instructions
                    shown=content(text,annotation.language,language,str(row.evidence_id))
                    if shown.review_status!='reviewed':continue
                    ref=cite(row.evidence_id)
                    common=dict(item_id=str(row.id),item_key=row.item_key,source_ids=(ref.reference_id,),last_verified_date=ref.last_checked_date)
                    if key=='benefits':
                        benefits.append(BenefitResult(**common,description=shown,amount_min=row.amount_min,
                            amount_max=row.amount_max,currency=row.currency,frequency=row.frequency))
                    elif key=='documents':
                        if row.requirement not in ('required','conditional','optional','unknown'):continue
                        documents.append(DocumentResult(**common,title=shown,requirement=row.requirement,
                            requirement_explanation=system(row.requirement,language),
                            condition=content(row.condition_text,annotation.language,language,ref.reference_id)))
                    else:
                        if row.last_checked_date>as_of or row.mode not in ('online','offline','both'):continue
                        verified_url=(row.original_url if annotation.application_url_verified
                            and valid_url(row.original_url,review.allowed_application_hosts) else None)
                        common['last_verified_date']=min(ref.last_checked_date,row.last_checked_date)
                        applications.append(ApplicationResult(**common,mode=row.mode,steps=(shown,),official_application_url=verified_url,
                            url_status='available' if verified_url else 'unavailable',url_message=system('url_available' if verified_url else 'url_unavailable',language)))
                        if verified_url:urls.append(ApplicationURL(route_id=str(row.id),url=verified_url,source_ids=(ref.reference_id,)))
        else:reason='GUIDANCE_REVIEW_UNAVAILABLE'
    references=tuple(sources[key] for key in sorted(sources))
    dates=[s.last_checked_date for s in references]
    if context is not None and dates and context.snapshot.last_checked_date and context.snapshot.last_checked_date<=as_of:
        dates.append(context.snapshot.last_checked_date)
    return ResultResponse(scheme_id=evaluation.scheme_id,language=language,scheme_name=name,
        eligibility_status=evaluation.status,explanation=DisplayText(text=evaluation.explanation,requested_language=language,
            content_language=language,review_status='system',origin='system'),assessment_notice=system('notice',language),
        conditions_satisfied=tuple(r for r in evaluation.evaluated_conditions if r.result=='SATISFIED'),
        conditions_not_satisfied=tuple(r for r in evaluation.evaluated_conditions if r.result=='FAILED'),
        missing_information=questionnaire.missing_information,
        benefits=section(benefits,totals['benefits'],language,reason),
        required_documents=section(documents,totals['documents'],language,reason),
        application_guidance=section(applications,totals['application_routes'],language,reason),
        official_application_urls=section(urls,len(applications),language,'NO_VERIFIED_APPLICATION_URL'),
        sources=references,last_verification_date=min(dates) if dates else None,evaluation=evaluation)
