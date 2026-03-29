import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
# استيراد الكلاسات
from database.data_store import ExamDataStore
from routers import exams

# 1. أول خطوة: تعريف الـ app (هذا السطر لازم يكون فوق الكل)
app = FastAPI(title="منصة الطالب العراقي")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # يسمح لأي موقع بالوصول (بما فيها ملفات الـ HTML مالتك)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 2. تعريف مخزن البيانات
store = ExamDataStore(db_path='database/exam_platform.db')

# 3. إعداد القوالب
templates = Jinja2Templates(directory="templates")


# 4. مسار فتح الـ PDF (الآن الـ app صار معروف فما راح يطلع خطأ)
@app.get("/open-pdf/{folder}/{filename}")
async def open_pdf(folder: str, filename: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "assets", folder, filename)

    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type='application/pdf',
            content_disposition_type='inline'
        )
    return {"error": "الملف غير موجود"}


# 5. ربط المجلدات الثابتة
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# 6. تضمين الراوترات
app.include_router(exams.router)


# --- المسارات (Routes) ---

@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("vmn.html", {"request": request})


@app.get("/api/books")
async def api_books():
    return store.get_all_books()


@app.get("/api/papers")
async def api_papers():
    return store.get_all_papers()
# لتشغيل السيرفر استخدم: uvicorn main:app --reload