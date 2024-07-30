import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import uuid

# 문서 폴더 경로 설정
documents_path = os.path.expanduser("~/Documents")
env_path = os.path.join(documents_path, "test.env")

# test.env 파일에서 환경 변수 로드
load_dotenv(env_path)

# OpenAI API 키 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {str(e)}")
        return None

def initialize_session_state():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

def main():
    initialize_session_state()

    st.set_page_config(page_title="윤리적 딜레마 토론 시스템", page_icon="🤔", layout="wide")
    
    st.title("🧠 윤리적 딜레마 토론 시스템")
    st.write("각 시나리오를 읽고 자신의 의견을 입력하세요. 근거를 포함한 의견을 제시해 주세요. AI가 의견에 대한 피드백을 제공합니다.")

    scenarios = {
        "시나리오 1: 박물관에서의 하루": {
            "description": "빈티지 철도 박물관에서 수업을 감독 중, 철도 마차가 다수의 학생을 위협하고 있습니다...",
            "options": ["전환기를 돌려 케빈을 희생시킨다.", "전환기를 돌리지 않는다."],
            "resources": ["밀 - 공리주의", "필리파 풋 - 트롤리 딜레마", "칸트 - 의무론", "톰슨 - 권리와 트롤리 딜레마"]
        },
        "시나리오 2: 목적 적합성": {
            "description": "다양한 배경의 학생들이 있는 고등학교에서 2년차 교사로 재직 중, 비효과적인 교육용 소프트웨어 사용에 의문을 가집니다...",
            "options": ["프로그램의 문제점을 보고함", "프로그램을 긍정적으로 홍보함"],
            "resources": ["존 듀이의 진보주의 교육 철학", "비고츠키의 사회문화적 이론", "마이클 풀란 - 교육 개혁 이론", "앨버트 반두라 - 자기 효능감 이론"]
        },
        "시나리오 3: 럭비경기": {
            "description": "스포츠 명문 공립학교에서 교사 첫 해, 인기 체육 교사의 부적절한 언행에 대한 의혹이 제기됩니다...",
            "options": ["부적절한 언행을 보고함", "침묵을 지킴"],
            "resources": ["존 롤스 - 정의론", "넬 나딩스 - 페미니즘 윤리학", "한나 아렌트 - 악의 평범성", "아지리스 - 조직 행동 이론"]
        },
        "시나리오 4: 비밀과 삶": {
            "description": "중학교 학생 복지 담당자로, 친구인 잭의 개인 문제로 인한 부정적인 영향을 목격합니다...",
            "options": ["잭의 상태를 학교에 알림", "비밀을 지켜줌"],
            "resources": ["피터 싱어 - 실용주의 윤리학", "윌리엄 제임스 - 실용주의", "칸트 - 의무론", "알버트 허쉬만 - 충성, 탈퇴, 항의 이론"]
        }
    }

    selected_scenario = st.selectbox("시나리오를 선택하세요:", list(scenarios.keys()), key=f"scenario_select_{st.session_state.user_id}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("시나리오")
        st.write(scenarios[selected_scenario]["description"])
        st.subheader("선택 옵션")
        for option in scenarios[selected_scenario]["options"]:
            st.write(f"- {option}")
        st.subheader("참고 자료")
        for resource in scenarios[selected_scenario]["resources"]:
            st.write(f"- {resource}")

        opinion = st.text_area("당신의 의견을 입력하세요 (근거를 포함해 주세요):", height=150, key=f"opinion_input_{st.session_state.user_id}")
        
        if st.button("의견 제출", key=f"submit_button_{st.session_state.user_id}"):
            if opinion:
                with st.spinner("AI가 응답을 생성 중입니다..."):
                    messages = [
                        {"role": "system", "content": """당신은 윤리적 딜레마에 대해 논리적이고 공정한 피드백을 제공하는 AI 조교입니다. 
                        제시된 참고 자료를 고려하여 답변해주세요. 
                        사용자가 토론 주제에서 벗어난 경우, 예의 바르게 주제로 돌아오도록 유도해주세요. 
                        사용자의 의견에 근거가 부족한 경우, 추가적인 근거를 요청하세요."""},
                        {"role": "user", "content": f"""
                        시나리오: {scenarios[selected_scenario]['description']}
                        옵션: {', '.join(scenarios[selected_scenario]['options'])}
                        참고 자료: {', '.join(scenarios[selected_scenario]['resources'])}
                        의견: {opinion}

                        다음 형식으로 응답해주세요:
                        1. 의견에 대한 분석 (토론 주제 관련성 및 근거의 적절성 평가 포함)
                        2. 가능한 대안적 관점
                        3. 추가 고려사항
                        4. 참고 자료와 연관된 분석
                        5. (필요시) 토론 주제로의 유도 또는 추가 근거 요청
                        6. 피드백을 반영해 토론에서 발언할 내용을 제작, 영어로 번역
                        """}
                    ]
                    response = generate_response(messages)
                    if response:
                        st.session_state.conversation_history.append({"user": opinion, "ai": response})
                        with col2:
                            st.subheader("AI의 피드백")
                            st.write(response)
            else:
                st.warning("의견을 입력해주세요.")

    # 대화 기록 표시
    if st.session_state.conversation_history:
        with col2:
            st.subheader("대화 기록")
            for entry in st.session_state.conversation_history:
                st.text("사용자:")
                st.write(entry["user"])
                st.text("AI:")
                st.write(entry["ai"])
                st.markdown("---")

if __name__ == "__main__":
    main()
