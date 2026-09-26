"""Mystery Province - Streamlit UI."""

from pathlib import Path
import sys
import random

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from game.questions import QUESTIONS
from game.scoring import GameState
from ir.search_engine import ProvinceSearchEngine
from ir.ir_demo import analyze_query


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Mystery Province 🇹🇭",
    page_icon="🇹🇭",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #9CA3AF;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    .card {
        padding: 1.2rem;
        border: 1px solid rgba(128,128,128,.25);
        border-radius: 16px;
        margin-bottom: 1rem;
    }

    .clue {
        padding: .65rem .8rem;
        border-radius: 10px;
        background: rgba(128,128,128,.10);
        margin: .35rem 0;
    }

    .score {
        font-size: 2rem;
        font-weight: 800;
    }

    .feedback-row {
        display: flex;
        align-items: center;
        gap: .75rem;
        padding: .75rem 1rem;
        border-radius: 12px;
        margin: .45rem 0;
        border: 1px solid rgba(255,255,255,.08);
    }

    .feedback-red {
        background: rgba(239,68,68,.12);
        border-left: 5px solid #ef4444;
    }

    .feedback-yellow {
        background: rgba(234,179,8,.14);
        border-left: 5px solid #eab308;
    }

    .feedback-green {
        background: rgba(34,197,94,.14);
        border-left: 5px solid #22c55e;
    }

    .feedback-icon {
        font-size: 1.2rem;
    }

    .feedback-province {
        font-weight: 700;
        flex: 1;
    }

    .feedback-label {
        color: #cbd5e1;
    }

    .feedback-rank {
        font-weight: 800;
        min-width: 3.5rem;
        text-align: right;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

def init_state():

    if "page" not in st.session_state:
        st.session_state.page = "home"

    # สร้างลำดับจังหวัดแบบสุ่ม 77 จังหวัด
    if "game_order" not in st.session_state:
        st.session_state.game_order = list(range(len(QUESTIONS)))
        random.shuffle(st.session_state.game_order)

    if "question_index" not in st.session_state:
        st.session_state.question_index = 0

    if "game_state" not in st.session_state:

        first_question_index = (
            st.session_state.game_order[0]
        )

        st.session_state.game_state = GameState(
            QUESTIONS[first_question_index]
        )

    if "total_score" not in st.session_state:
        st.session_state.total_score = 0

    if "completed" not in st.session_state:
        st.session_state.completed = 0

    if "search_engine" not in st.session_state:
        st.session_state.search_engine = None

    if "last_game_search" not in st.session_state:
        st.session_state.last_game_search = None

    if "guess_feedback" not in st.session_state:
        st.session_state.guess_feedback = []


# =========================================================
# NEW QUESTION
# =========================================================

def new_question(index: int):

    st.session_state.question_index = index

    # ดึงจังหวัดจากลำดับที่ถูกสุ่มไว้
    question_id = (
        st.session_state.game_order[index]
    )

    st.session_state.game_state = GameState(
        QUESTIONS[question_id]
    )

    # ล้างผลการทายของด่านเก่า
    st.session_state.guess_feedback = []

    st.session_state.last_game_search = None


# =========================================================
# START NEW GAME
# =========================================================

def start_new_game():

    # รีเซ็ตคะแนน
    st.session_state.total_score = 0

    # รีเซ็ตจำนวนด่านที่ผ่าน
    st.session_state.completed = 0

    # สร้างลำดับใหม่ครบทุกจังหวัด
    st.session_state.game_order = list(
        range(len(QUESTIONS))
    )

    # สุ่มลำดับจังหวัด
    random.shuffle(
        st.session_state.game_order
    )

    # เริ่มจากด่านที่ 1
    st.session_state.question_index = 0

    # เอาจังหวัดแรกจากลำดับที่สุ่มใหม่
    first_question_index = (
        st.session_state.game_order[0]
    )

    st.session_state.game_state = GameState(
        QUESTIONS[first_question_index]
    )

    # ล้างข้อมูลเกมเก่า
    st.session_state.guess_feedback = []

    st.session_state.last_game_search = None


# =========================================================
# NAVIGATION
# =========================================================

def go(page: str):
    st.session_state.page = page


# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    st.sidebar.title("🇹🇭 Mystery Province")

    pages = {
        "🏠 หน้าหลัก": "home",
        "📖 วิธีเล่น": "how_to_play",
        "🎮 เกมทายจังหวัด": "game",
        "🔎 ค้นหาข้อมูล": "search",
        "🏆 คะแนน": "score",
        "🧠 IR Demo": "ir_demo",
    }

    for label, page in pages.items():

        if st.sidebar.button(
            label,
            use_container_width=True
        ):

            go(page)
            st.rerun()

    st.sidebar.divider()

    st.sidebar.metric(
        "คะแนนรวม",
        st.session_state.total_score
    )

    st.sidebar.metric(
        "ผ่านแล้ว",
        f"{st.session_state.completed}/{len(QUESTIONS)}"
    )


# =========================================================
# HOME
# =========================================================

def render_home():

    st.markdown(
        '<div class="main-title">🇹🇭 Mystery Province</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'เกมทายจังหวัดปริศนาด้วย Word2Vec และ Information Retrieval'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "จังหวัดในฐานข้อมูล",
        "77"
    )

    c2.metric(
        "โจทย์ทั้งหมด",
        len(QUESTIONS)
    )

    c3.metric(
        "เทคโนโลยีหลัก",
        "Word2Vec"
    )

    st.markdown("### 🎯 เกมนี้เล่นอย่างไร?")

    st.write(
        "อ่านคำใบ้ → วิเคราะห์ → ทายจังหวัด "
        "→ ดูอันดับความใกล้เคียงแบบ Contexto"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🎮 เริ่มเกมใหม่",
            type="primary",
            use_container_width=True
        ):

            start_new_game()

            go("game")

            st.rerun()

    with col2:

        if st.button(
            "🔎 ทดลอง Search Engine",
            use_container_width=True
        ):

            go("search")

            st.rerun()

    st.info(
        "💡 ระบบ IR ใช้ Word2Vec + Cosine Similarity "
        "เพื่อวัดความใกล้เคียงของจังหวัด"
    )


# =========================================================
# HOW TO PLAY
# =========================================================

def render_how_to_play():

    st.markdown("## 📖 วิธีเล่น")

    steps = [
        (
            "1",
            "อ่านคำใบ้",
            "แต่ละด่านจะให้ข้อมูลเกี่ยวกับภูมิภาค "
            "สถานที่ อาหาร หรือวัฒนธรรม"
        ),
        (
            "2",
            "วิเคราะห์",
            "นำคำใบ้มาเปรียบเทียบกับจังหวัดที่คิดว่าน่าจะเกี่ยวข้อง"
        ),
        (
            "3",
            "ทาย",
            "กรอกชื่อจังหวัดที่คิดว่าเป็นคำตอบ"
        ),
        (
            "4",
            "ดูอันดับ",
            "ระบบจะแสดงสีและอันดับความใกล้เคียงแบบ Contexto"
        ),
        (
            "5",
            "รับคะแนน",
            "ตอบถูกจะจบด่าน และใช้ Hint จะลดคะแนน 20 คะแนน"
        ),
    ]

    for number, title, detail in steps:

        st.markdown(
            f"### {number}. {title}"
        )

        st.write(detail)

    st.divider()

    st.markdown("### 🧠 IR Pipeline")

    st.code(
        "Province Data → Word2Vec → Province Vector → "
        "Cosine Similarity → Ranking"
    )


# =========================================================
# CONTEXTO FEEDBACK
# =========================================================

def render_guess_feedback():

    feedback = st.session_state.guess_feedback

    if not feedback:
        return

    st.markdown("### 🎯 ผลการทาย")

    st.caption(
        "อันดับยิ่งน้อย = จังหวัดที่คุณทายยิ่งใกล้กับคำตอบ"
    )

    # เรียงจาก แดง → เหลือง → เขียว
    color_order = {
        "red": 0,
        "yellow": 1,
        "green": 2,
    }

    feedback = sorted(
        feedback,
        key=lambda item: (
            color_order.get(
                item["color"],
                99
            ),
            item["rank"]
        )
    )

    for item in feedback:

        if item["color"] == "green":

            icon = "🟢"
            label = "ใกล้มาก"

        elif item["color"] == "yellow":

            icon = "🟡"
            label = "ใกล้ปานกลาง"

        else:

            icon = "🔴"
            label = "ไกล"

        col1, col2, col3 = st.columns(
            [1, 5, 2]
        )

        with col1:

            st.markdown(
                f"### {icon}"
            )

        with col2:

            st.markdown(
                f"**{item['province']}**"
            )

            st.caption(label)

        with col3:

            st.markdown(
                f"### #{item['rank']}"
            )

        st.divider()


# =========================================================
# GAME
# =========================================================

def render_game():

    st.markdown(
        "## 🎮 เกมทายจังหวัดปริศนา"
    )

    state: GameState = (
        st.session_state.game_state
    )

    question = state.question

    # Progress bar
    st.progress(
        (
            st.session_state.question_index + 1
        )
        / len(QUESTIONS)
    )

    st.caption(
        f"ด่าน {st.session_state.question_index + 1} "
        f"/ {len(QUESTIONS)} "
        f"• ลำดับจังหวัดถูกสุ่มแล้ว"
    )

    left, right = st.columns(
        [2, 1]
    )

    # =====================================================
    # LEFT
    # =====================================================

    with left:

        st.markdown("### 🔍 คำใบ้")

        for clue in question["clues"]:

            st.markdown(
                f'<div class="clue">💡 {clue}</div>',
                unsafe_allow_html=True
            )

        # -------------------------------------------------
        # HINT
        # -------------------------------------------------

        if (
            state.hints_used == 0
            and not state.is_finished
        ):

            if st.button(
                "💡 ใช้ Hint (-20 คะแนน)"
            ):

                hint = state.use_hint()

                if hint:

                    st.warning(
                        f"Hint: {hint}"
                    )

        elif state.hints_used > 0:

            st.warning(
                f"Hint: {question['hint']}"
            )

        # -------------------------------------------------
        # GUESS
        # -------------------------------------------------

        guess = st.text_input(
            "ชื่อจังหวัด",
            placeholder="เช่น เชียงใหม่",
            disabled=state.is_finished,
            key=f"guess_{question['id']}",
        )

        if st.button(
            "🎯 ส่งคำตอบ",
            type="primary",
            disabled=state.is_finished
        ):

            guess_clean = guess.strip()

            if not guess_clean:

                st.warning(
                    "กรุณาพิมพ์ชื่อจังหวัดก่อน"
                )

                st.stop()

            engine = get_search_engine()

            province_names = set(
                engine._province_vectors.keys()
            )

            # -------------------------------------------------
            # CHECK PROVINCE
            # -------------------------------------------------

            if guess_clean not in province_names:

                st.warning(
                    "ไม่พบจังหวัดนี้ในฐานข้อมูล 77 จังหวัด"
                )

                st.stop()

            # -------------------------------------------------
            # CHECK DUPLICATE
            # -------------------------------------------------

            already_guessed = {
                item["province"]
                for item in (
                    st.session_state.guess_feedback
                )
            }

            if guess_clean in already_guessed:

                st.warning(
                    "จังหวัดนี้คุณทายไปแล้ว "
                    "กรุณาลองจังหวัดอื่น"
                )

                st.stop()

            # -------------------------------------------------
            # SUBMIT GAME GUESS
            # -------------------------------------------------

            is_correct = state.submit_guess(
                guess_clean
            )

            # -------------------------------------------------
            # CONTEXTO RANKING
            # -------------------------------------------------

            feedback = (
                engine.get_contexto_feedback(
                    question["answer"],
                    guess_clean
                )
            )

            if feedback:

                st.session_state.guess_feedback.append(
                    feedback
                )

            # -------------------------------------------------
            # CORRECT
            # -------------------------------------------------

            if is_correct:

                st.success(
                    f"🎉 ถูกต้อง! คำตอบคือ "
                    f"{question['answer']}"
                )

                st.session_state.total_score += (
                    state.score
                )

                st.session_state.completed += 1

            else:

                st.error(
                    "ยังไม่ถูก! ดูสีและอันดับด้านล่าง "
                    "เพื่อวิเคราะห์ความใกล้เคียง"
                )

            # feedback อยู่ใน session_state
            # ดังนั้น rerun แล้วข้อมูลยังอยู่

            st.rerun()

        # =====================================================
        # CONTEXTO RESULT
        # =====================================================

        render_guess_feedback()

        # =====================================================
        # NEXT QUESTION
        # =====================================================

        if state.is_finished:

            st.success(
                f"คะแนนด่านนี้: {state.score} คะแนน"
            )

            if (
                st.session_state.question_index
                < len(QUESTIONS) - 1
            ):

                if st.button(
                    "➡️ ด่านถัดไป",
                    type="primary"
                ):

                    new_question(
                        st.session_state.question_index + 1
                    )

                    st.rerun()

            else:

                if st.button(
                    "🏆 ดูคะแนนรวม",
                    type="primary"
                ):

                    go("score")

                    st.rerun()

    # =====================================================
    # RIGHT - STATUS
    # =====================================================

    with right:

        st.markdown("### 📊 สถานะ")

        st.metric(
            "คะแนนด่าน",
            state.score
        )

        st.metric(
            "จำนวนครั้งที่ทาย",
            state.attempts
        )

        st.metric(
            "ทายผิด",
            state.wrong_guesses
        )

        st.metric(
            "ใช้ Hint",
            state.hints_used
        )


# =========================================================
# SEARCH ENGINE
# =========================================================

def get_search_engine():

    if (
        st.session_state.search_engine
        is None
    ):

        with st.spinner(
            "กำลังโหลด Word2Vec Model..."
        ):

            st.session_state.search_engine = (
                ProvinceSearchEngine()
            )

    return st.session_state.search_engine


# =========================================================
# SEARCH PAGE
# =========================================================

def render_search():

    st.markdown(
        "## 🔎 ค้นหาจังหวัดด้วย Word2Vec"
    )

    st.write(
        "ลองค้นหาด้วยคำสำคัญ เช่น "
        "`ภูเขา ดอย หนาว กาแฟ`"
    )

    query = st.text_input(
        "🔍 Search Query",
        placeholder="พิมพ์คำที่ต้องการค้นหา..."
    )

    top_k = st.slider(
        "จำนวนผลลัพธ์",
        5,
        20,
        10
    )

    if st.button(
        "ค้นหา",
        type="primary"
    ) and query.strip():

        engine = get_search_engine()

        result = engine.search(
            query,
            top_k=top_k
        )

        st.markdown(
            "### 🧩 คำที่ระบบพบ"
        )

        st.write(
            ", ".join(
                result["known_tokens"]
            )
            if result["known_tokens"]
            else "ไม่พบคำใน Vocabulary"
        )

        if result["unknown_tokens"]:

            st.caption(
                "ไม่พบใน Vocabulary: "
                + ", ".join(
                    result["unknown_tokens"]
                )
            )

        if not result["results"]:

            st.warning(
                "ไม่สามารถสร้าง Query Vector "
                "ได้จากคำค้นนี้"
            )

            return

        st.markdown(
            "### 📊 ผลการจัดอันดับ"
        )

        df = pd.DataFrame(
            result["results"]
        )

        df["score"] = df["score"].map(
            lambda x: f"{x:.4f}"
        )

        df.columns = [
            "อันดับ",
            "จังหวัด",
            "Cosine Similarity"
        ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# IR DEMO
# =========================================================

def render_ir_demo():

    st.markdown(
        "## 🧠 IR Demo — How Information Retrieval Works"
    )

    st.write(
        "หน้านี้แสดงขั้นตอนของ IR จากข้อมูลจริง "
        "ของโปรเจกต์ ตั้งแต่ Query จนถึง Ranking"
    )

    st.markdown(
        "### 🔄 IR Pipeline"
    )

    st.code(
        "Query\n"
        "  ↓\n"
        "Tokenization\n"
        "  ↓\n"
        "Word2Vec Embedding\n"
        "  ↓\n"
        "Query Vector\n"
        "  ↓\n"
        "Province Vector\n"
        "  ↓\n"
        "Cosine Similarity\n"
        "  ↓\n"
        "Ranking"
    )

    query = st.text_input(
        "🔍 ทดลอง Query",
        value="ภูเขา ดอย หนาว กาแฟ",
        key="ir_demo_query",
    )

    top_k = st.slider(
        "จำนวนจังหวัดที่แสดง",
        3,
        10,
        5,
        key="ir_demo_top_k"
    )

    if not query.strip():

        st.info(
            "กรุณาใส่ Query เพื่อเริ่ม Demo"
        )

        return

    engine = get_search_engine()

    demo = analyze_query(
        engine,
        query,
        top_k=top_k
    )

    result = demo["result"]

    # =====================================================
    # 1. TOKENIZATION
    # =====================================================

    st.markdown(
        "### 1️⃣ Query & Tokenization"
    )

    st.write(
        f"**Query:** `{query}`"
    )

    st.write(
        "**Tokens:**",
        result["tokens"]
        or "ไม่พบ Token"
    )

    st.write(
        "**Known Tokens:**",
        result["known_tokens"]
        or "ไม่มี"
    )

    st.write(
        "**Unknown Tokens:**",
        result["unknown_tokens"]
        or "ไม่มี"
    )

    # =====================================================
    # 2. WORD2VEC
    # =====================================================

    st.markdown(
        "### 2️⃣ Word2Vec Embedding"
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Vocabulary",
        f"{demo['vocabulary_size']:,} คำ"
    )

    c2.metric(
        "Vector Size",
        f"{demo['vector_size']} dimensions"
    )

    if demo["token_vectors"]:

        st.write(
            "ตัวอย่างค่าของ Word Vector "
            "8 dimensions แรก"
        )

        rows = []

        for item in demo["token_vectors"]:

            rows.append(
                {
                    "คำ": item["token"],
                    **{
                        f"dim{i+1}": f"{v:.4f}"
                        for i, v in enumerate(
                            item["first_values"]
                        )
                    },
                }
            )

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "ไม่มีคำใน Query ที่อยู่ใน "
            "Word2Vec Vocabulary"
        )

        return

    # =====================================================
    # 3. QUERY VECTOR
    # =====================================================

    st.markdown(
        "### 3️⃣ Query Vector"
    )

    st.write(
        "Query Vector ถูกสร้างจากค่าเฉลี่ย "
        "ของ Word Vectors ที่พบใน Vocabulary"
    )

    st.code(
        str(
            [
                round(v, 4)
                for v in demo[
                    "query_vector_first_values"
                ]
            ]
        )
        + " ..."
    )

    st.caption(
        f"แสดง 8 ค่าแรกจากทั้งหมด "
        f"{demo['vector_size']} dimensions"
    )

    # =====================================================
    # 4. PROVINCE VECTOR
    # =====================================================

    st.markdown(
        "### 4️⃣ Province Vector"
    )

    if demo["top_province"]:

        st.write(
            f"ตัวอย่าง Province Vector ของ "
            f"**{demo['top_province']}**"
        )

        st.code(
            str(
                [
                    round(v, 4)
                    for v in demo[
                        "province_vector_first_values"
                    ]
                ]
            )
            + " ..."
        )

        st.caption(
            "Province Vector สร้างจากค่าเฉลี่ย "
            "Word Vectors ของข้อมูลจังหวัดนั้น"
        )

    # =====================================================
    # 5. COSINE SIMILARITY
    # =====================================================

    st.markdown(
        "### 5️⃣ Cosine Similarity"
    )

    st.latex(
        r"\mathrm{cosine}(Q,P)="
        r"\frac{Q\cdot P}{||Q||\,||P||}"
    )

    if demo["cosine_value"] is not None:

        st.metric(
            "Similarity ของจังหวัดอันดับ 1",
            f"{demo['cosine_value']:.4f}"
        )

    # =====================================================
    # 6. RANKING
    # =====================================================

    st.markdown(
        "### 6️⃣ Ranking"
    )

    if result["results"]:

        df = pd.DataFrame(
            result["results"]
        )

        df["score"] = df["score"].map(
            lambda x: f"{x:.4f}"
        )

        df.columns = [
            "อันดับ",
            "จังหวัด",
            "Cosine Similarity"
        ]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.success(
            "ระบบจัดอันดับจาก Cosine Similarity "
            "สูง → ต่ำ โดยไม่ได้ hard-code คำตอบ"
        )

    else:

        st.warning(
            "Query นี้ไม่สามารถสร้าง "
            "Query Vector ได้"
        )


# =========================================================
# SCORE
# =========================================================

def render_score():

    st.markdown(
        "## 🏆 คะแนน"
    )

    st.metric(
        "คะแนนรวม",
        st.session_state.total_score
    )

    st.metric(
        "ด่านที่ผ่าน",
        f"{st.session_state.completed}/{len(QUESTIONS)}"
    )

    st.divider()

    st.write(
        "คะแนนแต่ละด่านเริ่มที่ 100 คะแนน "
        "และหัก 20 คะแนนเมื่อใช้ Hint"
    )

    if st.button(
        "🔄 เริ่มเกมใหม่",
        type="primary"
    ):

        start_new_game()

        go("game")

        st.rerun()


# =========================================================
# START APP
# =========================================================

init_state()

render_sidebar()


if st.session_state.page == "home":

    render_home()

elif st.session_state.page == "how_to_play":

    render_how_to_play()

elif st.session_state.page == "game":

    render_game()

elif st.session_state.page == "search":

    render_search()

elif st.session_state.page == "score":

    render_score()

elif st.session_state.page == "ir_demo":

    render_ir_demo()