import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from langchain_core.messages import HumanMessage
from app.graph import app_graph

st.set_page_config(page_title="Gemini 3.5 개발 스쿼드", layout="wide")
st.title("Gemini 3.5 Flash 자율형 소프트웨어 개발 스쿼드")
st.markdown("구글 I/O 2026에서 발표된 **Gemini 3.5 Flash**를 탑재하여, 기획-개발-리뷰 및 자율 교정 루프를 초고속으로 수행합니다.")

prompt_example = "사용자로부터 숫자를 입력받아 소수(Prime Number)인지 판별하고, 에러 처리가 포함된 콘솔 프로그램을 만들어줘."
user_input = st.text_input("생성할 프로그램의 요구사항을 입력하십시오:", value=prompt_example)

if st.button("소프트웨어 개발 시작"):
    if not user_input.strip():
        st.warning("요구사항을 입력해주세요.")
    
    else:
        # 3단 레이아웃 구성
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("1. 설계 명세서")
            architect_box = st.empty()
        with col2:
            st.subheader("소스 코드")
            coder_box = st.empty()
        with col3:
            st.subheader("코드 검증")
            reviewer_box = st.empty()
        
        inputs = {"messages": [HumanMessage(content=user_input)], "specs": "", "code": "", "review_result": ""}
        
        # 방어 로직 및 타입 가공이 적용된 실시간 그래프 스트리밍
        for state_update in app_graph.stream(inputs, stream_mode="updates"):
            if not state_update:
                continue
            
            for node_name, state_data in state_update.items():
                if not state_data:
                    continue
                
                # 헬퍼 함수: 데이터가 리스트나 딕셔너리 객체일 경우 내부 텍스트만 추출
                def parse_clean_text(raw_data):
                    if isinstance(raw_data, list) and len(raw_data) > 0:
                        item = raw_data[0]
                        if isinstance(item, dict) and "text" in item:
                            return item["text"]
                        if hasattr(item, "content"):
                            return item.content
                    if isinstance(raw_data, dict) and "text" in raw_data:
                        return raw_data["text"]
                    if hasattr(raw_data, "content"):
                        return raw_data.content
                    
                    # 문자열인 경우 원시 줄바꿈 기호(\n)가 이스케이프 되었는지 처리
                    return str(raw_data).replace("\\n", "\n")

                if node_name == "Architect":
                    specs = parse_clean_text(state_data.get("specs", ""))
                    architect_box.markdown(specs)
                    
                elif node_name == "Coder":
                    code = parse_clean_text(state_data.get("code", ""))
                    coder_box.markdown(code)
                    
                elif node_name == "Reviewer":
                    review = parse_clean_text(state_data.get("review_result", ""))
                    if "FAIL" in review:
                        reviewer_box.error(review)
                    else:
                        reviewer_box.success(review)
                        st.balloons()