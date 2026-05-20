import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

# 전역 상태 정의
class SquadState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    specs: str
    code: str
    review_result: str

# 코드 리뷰 통과 여부 검증 스키마
class ReviewOutput(BaseModel):
    decision: Literal["PASS", "FAIL"] =Field(
        description="코드가 완벽하고 요구 사항을 모두 충족하면 'PASS', 버그나 개선점이 있다면 'FAIL'을 선택하십시오."
    )
    feedback: str = Field(description="FAIL일 경우 개발자에게 전달할 구체적인 수정 요청 사항, PASS일 경우 칭찬 멘트")

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

# 아키텍트 노드: 요구사항 구체화
architect_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 수석 소프트웨어 아키텍트입니다. 사용자의 투박한 요구사항을 분석하여 "
               "프로그램의 핵심 기능 정의와 세부 구현 명세서(Specs)를 마크다운 형태로 작성하십시오."),
    MessagesPlaceholder(variable_name="messages")
])

def architect_node(state: SquadState):
    messages = state.get("messages", [])
    chain = architect_prompt | llm
    response = chain.invoke({"messages": messages})
    return {"specs": response.content}

# 개발자 노드 : 코드 작성 및 수정
coder_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 민첩한 풀스택 개발자입니다. 다음 명세서를 바탕으로 완벽하게 작동하는 파이썬 코드를 작성하십시오. "
               "만약 리뷰어의 피드백이 제공된다면, 기존 코드를 분석하여 버그를 완벽히 수정한 코드를 다시 작성하십시오.\n\n"
               "구현 명세서: {specs}\n"
               "리뷰어 피드백: {feedback}"),
    MessagesPlaceholder(variable_name="messages")
])

def coder_node(state: SquadState):
    messages = state.get("messages", [])
    specs = state.get("specs", "")
    feedback = state.get("review_result", "최초 작성 단계입니다. 피드백 없음.")
    
    chain = coder_prompt | llm
    response = chain.invoke({"messages": messages, "specs": specs, "feedback": feedback})
    return {"code": response.content}

# 리뷰어 노드 :코드 검증 및 품질 평가
reviewer_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 까다로운 수석 코드 리뷰어입니다. 작성된 코드가 구현 명세서의 요구사항을 모두 만족하는지, "
               "논리적 오류나 예외 처리가 누락되지 않았는지 엄격하게 검토하십시오.\n\n"
               "구현 명세서: {specs}\n"
               "작성된 코드: {code}"),
    MessagesPlaceholder(variable_name="messages")
])

def reviewer_node(state: SquadState):
    messages = state.get("messages", [])
    specs = state.get("specs", "")
    code = state.get("code", "")

    # 구조화된 출력을 활용해 합격 여부 결정
    chain = reviewer_prompt | llm.with_structured_output(ReviewOutput)
    result = chain.invoke({"messages": messages, "specs": specs, "code": code})

    # 라우팅 결정을 위해 상태를 업데이트
    return {"review_result": f"결정: {result.decision}\n내용: {result.feedback}"}

# 조건부 라우팅 함수: 리뷰 결과에 따른 수환 또는 종료
def route_review_result(state: SquadState):
    result_text = state.get("review_result", "")
    if "결정: PASS" in result_text:
        return END
    #통과 하지 못하면 다시 개발자에게 돌려보냄
    return "Coder"

# 그래프 조립
builder = StateGraph(SquadState)

builder.add_node("Architect", architect_node)
builder.add_node("Coder", coder_node)
builder.add_node("Reviewer", reviewer_node)

builder.add_edge(START, "Architect")
builder.add_edge("Architect", "Coder")
builder.add_edge("Coder", "Reviewer")

builder.add_conditional_edges(
    "Reviewer",
    route_review_result,
    {
        "Coder": "Coder",
        END: END
    }
)

app_graph = builder.compile()