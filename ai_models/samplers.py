import json
import random


# =========================================================
# 1. ساحب مادة اللغة العربية (المعدل الذكي للأجزاء والشامل)
# =========================================================
def extract_arabic_sample(material_data):
    grammar_text = "=== قسم القواعد ===\n"
    literature_text = "=== قسم الأدب والنصوص ===\n"

    sections = material_data if isinstance(material_data, list) else material_data.get("sections", [])

    if not sections:
        return f"=== المادة ===\n{str(material_data)[:3000]}"

    for sec in sections:
        title = sec.get('title', '')
        is_literature = any(keyword in title for keyword in ["أدب", "مدرسة", "قصيدة", "شاعر", "حياة", "نصوص", "النقد"])

        pool = []
        if sec.get('definition'):
            pool.append(f"التعريف/الشرح: {sec.get('definition')}")
        if sec.get('rules'):
            for rule in sec.get('rules', []):
                pool.append(f"قاعدة/نقطة: {rule.get('rule')} - {rule.get('description')}")

        if pool:
            random.shuffle(pool)
            # نأخذ 5 أو 6 معلومات من كل موضوع حتى إذا دزيت 10 وحدات يكفيها وتتوزع صح
            selected_items = pool[:6]

            content = f"📌 {title}\n"
            for item in selected_items:
                content += f" - {item}\n"
            content += "-" * 20 + "\n"

            if is_literature:
                literature_text += content
            else:
                grammar_text += content

    # تم رفع الاستيعاب حتى يتحمل 10 وحدات (الشامل) بدون ما يگص النص
    return grammar_text[:6000] + "\n\n" + literature_text[:6000]


# =========================================================
# 2. ساحب مادة التربية الإسلامية (المعدل الذكي)
# =========================================================
def extract_islamic_sample(material_data):
    quran_text = "=== القرآن الكريم (حفظ، تفسير، وأحكام) ===\n"
    hadeeth_text = "=== الحديث النبوي الشريف ===\n"
    other_text = "=== التهذيب والأبحاث ===\n"

    # توحيد البيانات لتكون قائمة (List) ليسهل المرور عليها
    sections = material_data if isinstance(material_data, list) else [material_data]

    for data in sections:
        if not isinstance(data, dict):
            continue

        # --- النمط الأول: أحكام التلاوة (مثل part0.json) ---
        if "أحكام_التلاوة" in data:
            ahkam = data["أحكام_التلاوة"]
            quran_text += f"\n📌 الموضوع: {ahkam.get('العنوان', 'أحكام التلاوة')}\n"
            if "التعاريف" in ahkam:
                for key, val in ahkam["التعاريف"].items():
                    if isinstance(val, dict):
                        quran_text += f" - تعريف ({key}): {val.get('التعريف', '')}\n"
                        if "مثال" in val: quran_text += f"   مثال: {val['مثال']}\n"
                        if "أمثلة_في_حالة_الوصل" in val: quran_text += f"   مثال: {val['أمثلة_في_حالة_الوصل'][0]}\n"
            continue

        # --- النمط الثاني والثالث: الوحدات والدروس ---
        exam_sections = data.get('exam_sections', [])
        if not exam_sections and "sections" in data:
            exam_sections = data.get("sections", [])

        for sec in exam_sections:
            section_name = sec.get('section_name', '') or sec.get('title', 'موضوع')
            lessons = sec.get('lessons', [])

            # في حال كان الهيكل لا يحتوي lessons (مثل part3)
            if not lessons and ('title' in sec or 'content' in sec):
                lessons = [sec]

            for lesson in lessons:
                title = lesson.get('lesson_title', '') or lesson.get('title', '')
                content_text = f"\n📌 الموضوع: {title} ({section_name})\n"

                pool = []

                # 1. استخراج النصوص القرآنية أو الأحاديث
                if 'book_text' in lesson:
                    pool.append(f"النص: {str(lesson['book_text'])[:300]}")
                if 'content' in lesson and isinstance(lesson['content'], dict):
                    if 'verses' in lesson['content']:
                        for v in lesson['content']['verses']:
                            pool.append(f"﴿{v.get('text', '')}﴾")

                # 2. المعاني والكلمات
                if 'vocabulary' in lesson and isinstance(lesson['vocabulary'], dict):
                    for k, v in list(lesson['vocabulary'].items())[:3]:
                        pool.append(f"معنى ({k}): {v}")

                # 3. الشرح والمعنى العام
                if 'explanation' in lesson:
                    exp = lesson['explanation']
                    if isinstance(exp, str):
                        pool.append(f"الشرح: {exp[:300]}")
                    elif isinstance(exp, dict) and 'general_meaning' in exp:
                        pool.append(f"الشرح: {str(exp['general_meaning'])[:300]}")

                # 4. المناقشة والأسئلة (مهم جداً للوزاريات)
                if 'discussion_questions' in lesson:
                    for q in lesson['discussion_questions']:
                        q_text = q.get('question', '')
                        a_text = str(q.get('answer', ''))[:150]
                        pool.append(f"❓ سؤال: {q_text} | الجواب: {a_text}")

                # الفلترة الذكية (سحب 5 معلومات عشوائية من كل درس)
                if pool:
                    import random
                    random.shuffle(pool)
                    for p in pool[:5]:
                        content_text += f" - {p}\n"

                # توزيع النص على القسم المناسب
                if any(kw in title or kw in section_name for kw in ["سورة", "قرآن", "تلاوة", "تفسير", "أحكام"]):
                    quran_text += content_text
                elif any(kw in title or kw in section_name for kw in ["حديث", "الحديث", "نبوي"]):
                    hadeeth_text += content_text
                else:
                    other_text += content_text

    # الإرجاع بسعة ممتازة لدعم الامتحان الشامل
    return quran_text[:5000] + "\n\n" + hadeeth_text[:3000] + "\n\n" + other_text[:5000]

# =========================================================
# 3. ساحب مادة الرياضيات (المعدل الذكي للشامل والفصلي)
# =========================================================
def extract_math_sample(material_data):
    math_text = "=== قوانين ومواضيع الرياضيات ===\n"
    sections = material_data if isinstance(material_data, list) else material_data.get("sections", [])

    for sec in sections:
        chapter_text = ""
        data = sec.get("data", sec) if isinstance(sec, dict) and "data" in sec else sec
        items = data if isinstance(data, list) else [data]

        for item in items:
            if isinstance(item, dict):
                if 'chapter' in item:
                    chapter_text += f"\n📌 الفصل: {item['chapter'].get('name_ar', '') or item['chapter'].get('title_ar', '')}\n"
                elif 'chapter_title' in item:
                    chapter_text += f"\n📌 الفصل: {item['chapter_title'].get('arabic', '') or item['chapter_title'].get('english', '')}\n"
                elif 'header' in item and isinstance(item['header'], dict):
                    chapter_text += f"\n📌 الفصل: {item['header'].get('arabic', '') or item['header'].get('title', '')}\n"

                problems_pool = []
                if 'extra_sections' in item:
                    for es in item['extra_sections']:
                        if 'operations' in es:
                            for op_name, op_val in es['operations'].items():
                                problems_pool.append(f"🔹 قاعدة ({op_name}): {op_val}")
                if 'sections' in item:
                    for s in item['sections']:
                        if s.get('type') == 'exercises' and 'list' in s:
                            for ex in s['list']: problems_pool.append(f"🔸 مسألة: {ex.get('problem')}")
                        elif 'text' in s:
                            problems_pool.append(f"🔸 مبرهنة: {s.get('text')}")

                if problems_pool:
                    random.shuffle(problems_pool)
                    for p in problems_pool[:8]: chapter_text += f"{p}\n"

        math_text += chapter_text
    return math_text[:12000]


# =========================================================
# 4. ساحب مادة الفيزياء (المعدل الذكي)
# =========================================================
def extract_physics_sample(material_data):
    physics_text = "=== قوانين وشرحيات الفيزياء ===\n"
    sections = material_data if isinstance(material_data, list) else material_data.get("sections", [])

    for sec in sections:
        data = sec.get("data", sec) if isinstance(sec, dict) and "data" in sec else sec
        items = data if isinstance(data, list) else [data]

        for item in items:
            if isinstance(item, dict):
                if 'chapter_title' in item:
                    physics_text += f"\n📌 الفصل: {item.get('chapter_title')}\n"

                pool = []
                if 'contents' in item:
                    for c in item['contents']:
                        if 'definition' in c: pool.append(f"📖 تعريف: {c.get('definition')}")
                        if 'reasons' in c:
                            for r in c['reasons']: pool.append(f"🤔 علل: {r}")

                if 'problems' in item or 'examples' in item:
                    problems = item.get('problems', []) + item.get('examples', [])
                    for p in problems:
                        pool.append(f"🔸 مسألة: {p.get('text') or p.get('details')}")

                if pool:
                    random.shuffle(pool)
                    for p in pool[:8]: physics_text += f"{p}\n"

    return physics_text[:12000]


# =========================================================
# 5. ساحب مادة الكيمياء (المعدل الذكي)
# =========================================================
def extract_chemistry_sample(material_data):
    chemistry_text = "=== المادة العلمية للكيمياء ===\n"
    sections = material_data if isinstance(material_data, list) else material_data.get("sections", [])

    for sec in sections:
        data = sec.get("data", sec) if isinstance(sec, dict) and "data" in sec else sec
        items = data if isinstance(data, list) else [data]

        for item in items:
            if isinstance(item, dict):
                if 'chapter' in item:
                    chemistry_text += f"\n📌 الفصل: {item['chapter'].get('title_arabic', '')}\n"

                pool = []
                if 'reaction' in item: pool.append(f"⚗️ التفاعل: {item.get('reaction')}")
                if 'question' in item: pool.append(f"❓ سؤال/مسألة: {item.get('question')}")

                if 'contents' in item:
                    for c in item['contents']:
                        if 'definition' in c: pool.append(f"📖 تعريف: {c.get('definition')}")
                        if 'explanation' in c: pool.append(f"💡 شرح: {c.get('explanation')}")

                if pool:
                    random.shuffle(pool)
                    for p in pool[:8]: chemistry_text += f"{p}\n"

    return chemistry_text[:12000]


# =========================================================
# 6. ساحب مادة الأحياء (المعدل الذكي)
# =========================================================
def extract_biology_sample(material_data):
    biology_text = "=== المادة العلمية للأحياء ===\n"
    sections = material_data if isinstance(material_data, list) else material_data.get("sections", [])

    for sec in sections:
        data = sec.get("data", sec) if isinstance(sec, dict) and "data" in sec else sec
        items = data if isinstance(data, list) else [data]

        for item in items:
            if isinstance(item, dict):
                if 'title' in item: biology_text += f"\n📌 الموضوع: {item.get('title')}\n"

                pool = []
                if item.get('definition'): pool.append(f"📖 التعريف: {item.get('definition')}")
                if item.get('explanation'): pool.append(f"💡 الشرح: {item.get('explanation')}")
                if item.get('notes'): pool.append(f"📝 ملاحظة: {item.get('notes')}")

                if item.get('examples') and isinstance(item['examples'], list):
                    for ex in item['examples']:
                        if 'problem' in ex and 'solution' in ex:
                            pool.append(f"سؤال: {ex.get('problem')} | الجواب: {ex.get('solution')}")

                if pool:
                    random.shuffle(pool)
                    for p in pool[:8]: biology_text += f" - {p}\n"

    return biology_text[:12000]


# =========================================================
# 7. ساحب مادة اللغة الإنجليزية (المعدل الذكي)
# =========================================================
def extract_english_sample(material_data):
    english_text = "=== English Study Material ===\n"
    sections = material_data if isinstance(material_data, list) else material_data.get("sections", [])

    for sec in sections:
        data = sec.get("data", sec) if isinstance(sec, dict) and "data" in sec else sec
        items = data if isinstance(data, list) else [data]

        for item in items:
            if isinstance(item, dict):
                if 'title' in item: english_text += f"\n📌 Topic: {item.get('title')}\n"

                pool = []
                if item.get('definition'): pool.append(f"📖 Concept: {item.get('definition')}")
                if item.get('rules'): pool.append(f"⚙️ Rule: {item.get('rules')}")

                if item.get('examples') and isinstance(item['examples'], list):
                    for ex in item['examples']:
                        if 'problem' in ex and 'solution' in ex:
                            pool.append(f"📝 Q: {ex.get('problem')} | A: {ex.get('solution')}")

                if pool:
                    random.shuffle(pool)
                    for p in pool[:8]: english_text += f" - {p}\n"

    return english_text[:12000]


# =========================================================
# 8. الموزع الذكي (النهائي)
# =========================================================
def get_smart_sample(material_data, subject_name="arabic"):
    subject_lower = subject_name.lower()

    if "islamic" in subject_lower or "إسلامية" in subject_name:
        return extract_islamic_sample(material_data)
    elif "math" in subject_lower or "رياضيات" in subject_name:
        return extract_math_sample(material_data)
    elif "physics" in subject_lower or "فيزياء" in subject_name:
        return extract_physics_sample(material_data)
    elif "chem" in subject_lower or "كيمياء" in subject_name:
        return extract_chemistry_sample(material_data)
    elif "bio" in subject_lower or "احياء" in subject_name or "أحياء" in subject_name:
        return extract_biology_sample(material_data)
    elif "eng" in subject_lower or "انجليزي" in subject_name or "إنكليزي" in subject_name:
        return extract_english_sample(material_data)
    else:
        return extract_arabic_sample(material_data)


# =========================================================
# 9. دالة استخراج النمط الوزاري
# =========================================================
def extract_past_exam_pattern(exams_data):
    try:
        if isinstance(exams_data, str):
            exams_json = json.loads(exams_data)
        else:
            exams_json = exams_data

        questions = exams_json.get("questions", [])
        if not questions: return str(exams_data)[:1000]

        exam = questions[0]
        pattern_text = f"نموذج للتقليد ({exam.get('year')}):\n"
        for section in exam.get("sections", []):
            pattern_text += f"القسم: {section.get('title')} ({section.get('total_marks')} درجة)\n"
            for sub in section.get("sub_sections", []):
                pattern_text += f" {sub.get('title')}: {sub.get('instruction')}\n"
                if sub.get("sub_questions"):
                    for q in sub.get("sub_questions", []):
                        pattern_text += f"   - فرع {q.get('part')}: {q.get('text')}\n"
                elif sub.get("options"):
                    for opt in sub.get("options", []):
                        pattern_text += f"   - {opt.get('option') or 'فرع'}: {opt.get('text')}\n"
        return pattern_text
    except Exception:
        return str(exams_data)[:1000]