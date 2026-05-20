# Gemini 3.5 Flash 기반 자율형 소프트웨어 개발 스쿼드

## 프로젝트 개요
이 프로젝트는 구글 I/O 2026에서 공개된 차세대 모델 **Gemini 3.5 Flash**의 초고속 추론 능력과 고도화된 다중 에이전트 제어력을 실증하는 소프트웨어 자동 생성 파이프라인입니다. 사용자 요구사항이 접수되면 아키텍트, 개발자, 리뷰어 에이전트가 완벽한 결과물이 도출될 때까지 자율적으로 피드백 루프(Self-Correction Loop)를 수행합니다. 이전 세대 대비 4배 이상 빨라진 Gemini 3.5 Flash의 성능을 극대화하여 복잡한 다중 에이전트 협업의 지연 시간을 혁신적으로 단축한 구조를 보여줍니다.

## 기술 스택
* 언어: Python 3
* 프레임워크: LangGraph, LangChain, Streamlit
* LLM: Google Gemini 3.5 Flash (`langchain-google-genai`)
* 데이터 검증: Pydantic
* 환경 관리: uv, python-dotenv

## 설치 및 실행방법
1. 프로젝트 디렉토리 준비 및 이동
2. 최상단 폴더에 .env 파일을 생성하고 구글 AI 스튜디오에서 발급받은 API 키를 입력합니다.
```
   GOOGLE_API_KEY=AIzaSyYourGeminiAPIKeyHere
   ```
3. uv 도구를 이용해 가상 환경을 활성화하고 의존성을 설치합니다.
```
   uv venv
   (가상환경 활성화)
   uv pip install -r requirements.txt
   ```
4. 웹 인터페이스 구동
```
   streamlit run main.py
```
## 로직 설명
1. Architect 노드: 입력된 아이디어를 구현 가능한 구체적인 마크다운 스펙 명세서로 변환합니다.
2. Coder 노드: 생성된 명세서 또는 Reviewer 노드로부터 전달된 피드백 텍스트를 조합하여 파이썬 코드를 작성 및 수정합니다.
3. Reviewer 노드: 요구사항 충족률을 검증하고 Pydantic 구조화 출력을 통해 PASS 혹은 FAIL 결정을 내립니다. FAIL이 선언될 경우 제어권이 다시 Coder 노드로 넘어가며, PASS가 선언될 때까지 이 루프가 완벽히 자율적으로 동기화되어 반복됩니다.

# 실행 화면

<img width="1567" height="1097" alt="스크린샷 2026-05-20 131339" src="https://github.com/user-attachments/assets/b3b1d1a2-9d80-489e-a582-bb7a5dfae2e6" />
