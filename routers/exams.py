import os
import json
import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# استيراد دالة التوليد من ملف المودل الخاص بك
# الاستدعاء من (اسم المجلد . اسم الملف) ثم استيراد الدالة
from ai_models.generator import generate_exam_dynamic

router = APIRouter(prefix="/api/exams", tags=["Exams"])

class ExamRequest(BaseModel):
    subject: str        # اسم المادة كما هو في قاعدة البيانات
    topic: str          # رقم الفصل (مثلاً "1" أو "2") أو كلمة "شامل"
    grade: str = "سادس علمي"

def get_db_connection():
    # تأكد إن المسار يشير لمكان الملف الحقيقي
    conn = sqlite3.connect('database/exam_platform.db')
    conn.row_factory = sqlite3.Row
    return conn

@router.post("/generate")
async def generate_exam(request: ExamRequest):
    conn = get_db_connection()
    try:
        # 1. جلب بيانات المادة من قاعدة البيانات
        target_subject = request.subject.strip()
        subject_data = conn.execute(
            "SELECT q_prompt, a_prompt, json_book_path, json_question_path FROM subjects WHERE subject_name LIKE ?",
            (f"%{target_subject}%",)
        ).fetchone()

        if not subject_data:
            raise HTTPException(status_code=404, detail=f"المادة {target_subject} غير موجودة")

        # 2. جلب المادة العلمية (زيادة الجرعة لضمان وجود المسائل)
        material_content = []
        base_path = subject_data['json_book_path']

        def clean_content(data_list, limit=12):
            cleaned = []
            for item in data_list[:limit]:
                if isinstance(item, dict):
                    item_copy = {}
                    for k, v in item.items():
                        if isinstance(v, str):
                            item_copy[k] = v[:1000] + "..." if len(v) > 1000 else v
                        elif isinstance(v, list):
                            item_copy[k] = v
                        else:
                            item_copy[k] = v
                    cleaned.append(item_copy)
                else:
                    cleaned.append(item)
            return cleaned

        if request.topic == "شامل":
            if os.path.exists(base_path):
                all_files = [f for f in os.listdir(base_path) if f.endswith('.json')]
                for file_name in sorted(all_files):
                    with open(os.path.join(base_path, file_name), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        content = data if isinstance(data, list) else data.get('sections', [data])
                        material_content.extend(clean_content(content, limit=4))
        else:
            file_path = os.path.join(base_path, f"part{request.topic}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = data if isinstance(data, list) else data.get('sections', [data])
                    material_content = clean_content(content, limit=15)
            else:
                raise HTTPException(status_code=404, detail=f"ملف الفصل {request.topic} غير موجود")

            # =========================================================
            # التعديل الذكي: دمج أحكام التلاوة (part0.json) إجبارياً مع التربية الإسلامية
            # =========================================================
            if "إسلامية" in target_subject or "islamic" in target_subject.lower():
                part0_path = os.path.join(base_path, "part0.json")
                if os.path.exists(part0_path) and str(request.topic) != "0":
                    try:
                        with open(part0_path, 'r', encoding='utf-8') as f:
                            part0_data = json.load(f)
                            # جيسون أحكام التلاوة ما بيه sections، لذلك نخليه داخل List مباشرة
                            content0 = part0_data if isinstance(part0_data, list) else [part0_data]
                            material_content.extend(clean_content(content0, limit=5))
                    except Exception as e:
                        print(f"⚠️ ملاحظة: لم يتم دمج أحكام التلاوة - {e}")

        # 3. استرجاع الأسئلة الوزارية لضبط نمط الذكاء الاصطناعي
        previous_q_path = subject_data['json_question_path']
        previous_questions = {}
        if previous_q_path and os.path.exists(previous_q_path):
            try:
                with open(previous_q_path, 'r', encoding='utf-8') as f:
                    pq_data = json.load(f)
                    if isinstance(pq_data, list):
                        previous_questions = pq_data[:10]
                    elif isinstance(pq_data, dict):
                        previous_questions = dict(list(pq_data.items())[:10])
            except Exception as e:
                print(f"⚠️ فشل تحميل الوزاريات: {e}")

        # 4. إرسال البيانات "المحسنة" للمودل
        ai_response = generate_exam_dynamic(
            material_data=material_content,
            previous_questions=previous_questions,
            prompt_questions=subject_data['q_prompt'],
            prompt_answers=subject_data['a_prompt'],
            subject_name=target_subject  # أضف هذا السطر ضروري جداً
        )

        if "error" in ai_response:
            raise HTTPException(status_code=500, detail=ai_response["error"])

        return {
            "status": "success",
            "subject": request.subject,  # تأكد إن هذا الاسم هو "التربية الإسلامية"
            "topic": request.topic,
            "exam_data": ai_response["exam_data"],
            "answers_data": ai_response["answers_data"]
        }

    except Exception as e:
        print(f"❌ Error in generate_exam: {str(e)}")
        raise HTTPException(status_code=500, detail=f"حدث خطأ: {str(e)}")
    finally:
        conn.close()