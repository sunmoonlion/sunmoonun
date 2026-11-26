"""在 KnowBase 后端 app 以 PYTHONPATH=.:tests 运行；使用项目原有检索夹具。"""
from test_knowledge_retrieval import _request, _version
from app.application.dto.retrieval import Citation
from app.application.services.knowledge_retrieval_service import _assemble_response
from app.infrastructure.external.ragflow import RAGFlowRetrievalResult
from app.infrastructure.external.ragflow_provider import normalize_retrieval

version = _version()
def evidence(content, budget):
    result = normalize_retrieval(RAGFlowRetrievalResult(chunks=[{
        "dataset_id":version.provider_dataset_id, "document_id":version.provider_document_id,
        "content":content, "similarity":1,
    }], total=1))
    return _assemble_response(_request(token_budget=budget),result,[version]).evidence[0]

short = evidence("年度结论：完成",4)
full = evidence("年度结论：完成",20)
other = evidence("年度结论：未完成",4)
assert short.truncated and not full.truncated
assert short.chunk_id != full.chunk_id
assert Citation.from_evidence(short).source_href == Citation.from_evidence(other).source_href
assert short.evidence_id != full.evidence_id
