"""
Step 2 – GPT API 기반 서술형 채점 + 피드백 (점수 미사용)
───────────────────────────────────────────────
• 기존 Step 1‑2 코드 하단에 그대로 이어 붙이면 됩니다. (별도 파일로도 사용 가능)
• 교사는 GRADING_GUIDELINES 사전에 문항별 ‘채점 기준’을 자유롭게 입력하세요.
• 피드백은 ‘정답/오답 + 200자 이내 설명’ 형식으로 반환됩니다.
• 비용 절감을 위해 temperature=0, max_tokens≈250(≈200자) 사용.
"""

import streamlit as st

# ── 1. 수업 제목 ──
st.title("<지구와 바다> 수행평가")  # ← 교과별 제목으로 자유롭게 수정하세요.

# ── 2. 학번 입력 ──
student_id = st.text_input("출석번호", help="출석번호를 입력하세요.")

# ── 3‑1. 서술형 문제 1 표시 ──
QUESTION_1 = """
지구의 표면에서 관찰할 수 있는 다양한 모습을 3가지 이상 적어보세요.
"""  # ← 교사가 원하는 서술형 문제로 변경
st.markdown("#### 서술형 문제 1")
st.write(QUESTION_1)
answer_1 = st.text_area("답안을 입력하세요", key="answer1", height=150)

# ── 3‑2. 서술형 문제 2 표시 ──
QUESTION_2 = """
바닷물과 육지의 물을 비교해서 적어보세요.
"""
st.markdown("#### 서술형 문제 2")
st.write(QUESTION_2)
answer_2 = st.text_area("답안을 입력하세요", key="answer2", height=150)

# ── 3‑3. 서술형 문제 3 표시 ──
QUESTION_3 = """
밀물과 썰물에 대해서 설명해보세요.
"""
st.markdown("#### 서술형 문제 3")
st.write(QUESTION_3)
answer_3 = st.text_area("답안을 입력하세요", key="answer3", height=150)

# 답안을 리스트로 모아 이후 채점 로직에서 재사용하기
answers = [answer_1, answer_2, answer_3]

# ── 4. 전체 제출 버튼 ──
if st.button("제출"):
    if not student_id.strip():
        st.warning("출석번호를 입력하세요.")
    elif any(ans.strip() == "" for ans in answers):
        st.warning("모든 답안을 작성하세요.")
    else:
        st.success(f"제출 완료! 출석번호: {student_id}")
        # ⚠️ Step 2에서 GPT 채점 및 DB 저장 로직을 여기에 추가할 예정입니다.
        
from openai import OpenAI, OpenAIError

# ── 0. OpenAI 클라이언트 ──
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("⚠️ secrets.toml 에 OPENAI_API_KEY 를 설정하세요.")
    st.stop()

# ── 1. 문항별 채점 기준 (교사가 수정) ──
GRADING_GUIDELINES = {
    1: "산, 들, 강, 바다, 빙하, 사막, 호수, 계곡 등 예를 3가지 이상 기술한다.",
    2: "• 육지의 물은 빙하와 같이 얼음 상태로 있는 경우가 가장 많고, 강, 호수 등으로도 있다. , 바닷물에서 소금을 얻을 수 있다, 바닷물이 육지의 물보다 더 많다 등 바닷물과 육지의 물의 특징을 기술한다.",
    3: "밀물은 바닷물이 들어오며 바닷물의 높이가 높아지고, 썰물은 바닷물이 나가며 바닷물의 높이가 낮아지는 점을 언급한다."
}

# ── 2. 제출 버튼 (Step 1‑2의 버튼을 대체/호출) ──
if st.button("GPT 피드백 확인"):

    # answers 리스트는 Step 1‑2 코드에서 정의됨
    try:
        answers
    except NameError:
        st.error("answers 리스트가 정의되지 않았습니다. Step 1‑2 코드와 함께 실행하세요.")
        st.stop()

    feedbacks = []
    for idx, ans in enumerate(answers, start=1):
        # 빈 답안 처리
        if ans.strip() == "":
            feedbacks.append("X: 답안이 제출되지 않았습니다.")
            continue
        criterion = GRADING_GUIDELINES.get(idx, "채점 기준이 없습니다.")

        # 프롬프트 구성
        prompt = (
            f"문항 번호: {idx}\n"
            f"채점 기준: {criterion}\n"
            f"학생 답안: {ans}\n"
            "요구사항: 1) 정답 여부(O/X) 한 글자, 2) 200자 이내 구체적 피드백.\n"
            "형식 예시 → O: (피드백)"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",            # 필요 시 모델 변경
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=250,
            )
            feedback_text = response.choices[0].message.content.strip()
        except OpenAIError as e:
            feedback_text = f"API 오류: {e}"

        feedbacks.append(feedback_text)

    # ── 3. 결과 표시 ──
    for i, fb in enumerate(feedbacks, start=1):
        st.markdown(f"##### ▶ 서술형 문제 {i} 피드백")
        st.write(fb)

    st.success("모든 피드백이 생성되었습니다. 교사 확인 후 학생에게 전달하세요.")
