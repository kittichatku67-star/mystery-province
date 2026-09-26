"""Question generator for Mystery Province.

สร้างโจทย์จากข้อมูลจังหวัดทั้ง 77 จังหวัดใน data/provinces.csv
แต่ละจังหวัดจะมีโจทย์ 1 ข้อ
"""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "provinces.csv"


def clean_value(value):
    """แปลงค่าใน CSV ให้เป็นข้อความที่พร้อมแสดง"""
    if pd.isna(value):
        return ""

    return str(value).strip()


def split_values(value):
    """แยกข้อมูลที่ใช้ | เป็นตัวคั่น"""
    value = clean_value(value)

    if not value:
        return []

    return [
        item.strip()
        for item in value.split("|")
        if item.strip()
    ]


def build_question(row, question_id):
    """สร้างโจทย์ 1 ข้อจากข้อมูล 1 จังหวัด"""

    province = clean_value(row["province"])
    region = clean_value(row["region"])
    description = clean_value(row["description"])
    landmark = split_values(row["landmark"])
    food = split_values(row["food"])
    culture = split_values(row["culture"])
    geography = split_values(row["geography"])
    keywords = split_values(row["keywords"])

    clues = []

    # คำใบ้ภาค
    if region:
        clues.append(f"อยู่{region}")

    # คำใบ้ภูมิศาสตร์
    if geography:
        clues.append(
            f"ลักษณะพื้นที่เกี่ยวข้องกับ {', '.join(geography[:2])}"
        )

    # คำใบ้สถานที่
    if landmark:
        clues.append(
            f"มีสถานที่หรือแหล่งท่องเที่ยว เช่น {landmark[0]}"
        )

    # คำใบ้อาหาร
    if food:
        clues.append(
            f"มีอาหารหรือของกินที่เกี่ยวข้องกับ {food[0]}"
        )

    # คำใบ้วัฒนธรรม
    if culture:
        clues.append(
            f"มีวัฒนธรรม/ประเพณี เช่น {culture[0]}"
        )

    # ถ้ามีคำใบ้น้อย
    if len(clues) < 4 and description:
        clues.append(description)

    # จำกัดไว้ 4 คำใบ้
    clues = clues[:4]

    # Hint
    if keywords:
        hint = (
            "ลองนึกถึงคำสำคัญเกี่ยวกับ "
            + ", ".join(keywords[:2])
        )
    elif geography:
        hint = f"ลองคิดจากลักษณะภูมิประเทศ เช่น {geography[0]}"
    else:
        hint = "ลองวิเคราะห์จากคำใบ้ทั้งหมดอีกครั้ง"

    return {
        "id": question_id,
        "answer": province,
        "clues": clues,
        "hint": hint,
    }


def load_questions():
    """โหลดโจทย์ให้ครบทั้ง 77 จังหวัด"""

    data = pd.read_csv(
        DATA_PATH,
        encoding="utf-8-sig"
    )

    questions = []

    for index, row in data.iterrows():

        question = build_question(
            row,
            question_id=index + 1
        )

        questions.append(question)

    return questions


# =========================================================
# QUESTIONS
# =========================================================

QUESTIONS = load_questions()


# =========================================================
# CHECK
# =========================================================

if __name__ == "__main__":

    print(
        f"จำนวนโจทย์ทั้งหมด: {len(QUESTIONS)}"
    )

    print(
        f"จำนวนคำตอบไม่ซ้ำ: "
        f"{len(set(q['answer'] for q in QUESTIONS))}"
    )

    print("\nตัวอย่างโจทย์:")

    for question in QUESTIONS[:3]:

        print(
            f"\n#{question['id']} "
            f"{question['answer']}"
        )

        for clue in question["clues"]:
            print(f"- {clue}")