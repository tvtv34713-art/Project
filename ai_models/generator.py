import json
from groq import Groq
from ai_models.samplers import get_smart_sample, extract_past_exam_pattern

client = Groq(api_key="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")


def generate_exam_dynamic(material_data, previous_questions, prompt_questions, prompt_answers, subject_name="arabic"):
    print(f"\n[AI Engine] جاري تشغيل المحرك الوزاري لمادة: {subject_name} 🚀")

    try:
        clean_material = get_smart_sample(material_data, subject_name)
        clean_pattern = extract_past_exam_pattern(previous_questions)

        # 1. توليد الأسئلة
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_questions},
                {"role": "user", "content": f"المادة الصافية:\n{clean_material}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.7,  # درجة حرارة أعلى لضمان العشوائية
            max_tokens=4000
        )

        questions_content = response.choices[0].message.content
        questions_json = json.loads(questions_content)

        # تأكيد وجود المفتاح الصحيح للواجهة
        if "exam_paper" not in questions_json:
            for key in questions_json.keys():
                if isinstance(questions_json[key], list):
                    questions_json = {"exam_paper": questions_json[key]}
                    break

        # 2. توليد الأجوبة النموذجية
        answer_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_answers},
                {"role": "user", "content": f"الأسئلة المطلوب حلها:\n{json.dumps(questions_json, ensure_ascii=False)}"}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.1,  # درجة حرارة منخفضة جداً للدقة في الأجوبة
            max_tokens=4000
        )

        answers_json = json.loads(answer_response.choices[0].message.content)

        # تأكيد وجود المفتاح الصحيح للأجوبة
        if "model_answers" not in answers_json:
            for key in answers_json.keys():
                if isinstance(answers_json[key], list):
                    answers_json = {"model_answers": answers_json[key]}
                    break

        return {"exam_data": questions_json, "answers_data": answers_json}

    except Exception as e:
        print(f"❌ خطأ فني: {str(e)}")
        return {
            "error": str(e),
            "exam_data": {"exam_paper": []},
            "answers_data": {"model_answers": []}
        }