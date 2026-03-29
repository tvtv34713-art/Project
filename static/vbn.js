// ==========================================
// الإعدادات والبيانات الأساسية
// ==========================================
const subjectsData = {
    high: ["اللغة العربية", "اللغة الإنكليزية", "التربية الإسلامية", "الرياضيات", "الفيزياء", "الكيمياء", "الأحياء"]
};

const youtubeChannels = [
    { name: "التلفزيون التربوي", desc: "القناة الرسمية للوزارة", link: "https://www.youtube.com/@%D8%A7%D9%84%D8%B9%D8%B1%D8%A7%D9%82%D9%8A%D8%A9%D8%A7%D9%84%D8%AA%D8%B1%D8%A8%D9%88%D9%8A%D8%A9-%D8%B67%D9%8A" },
    { name: "حيدر عبدالائمه", desc: "رياضيات - سادس علمي", link: "https://youtube.com/@hayder_89?si=AHVhOHC7vR2_cHVZ" },
    { name: "حسين محمد", desc: "فيزياء - سادس علمي", link: "https://youtube.com/@ph-hm?si=cq3S5YFtpnwr-2kT" },
    { name: "هاشم الغرباوي", desc: "كيمياء - سادس علمي", link: "https://youtube.com/@hash_1988?si=bsgcmDxZXpUy2MXa" },
    { name: "جعفر الحسني", desc: "احياء - سادس علمي", link: "https://youtube.com/@jaafarnasif?si=T3AAvlkSsGGlO2ne" },
    { name: "علاء السعداوي", desc: "انكليزي - سادس علمي", link: "https://youtube.com/@alaaigabbar?si=FNDJQuEOFxaYttyK" },
    { name: "حمزة الجابري", desc: "اللغه العربيه - سادس علمي", link: "https://youtube.com/@hamzah-aljaberi?si=GafHr_Kb8CfTJKZT" },
];

let currentArabicAction = '';
let arabicPartModal;

// ==========================================
// تهيئة الصفحة عند التحميل
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupEventListeners();

    // تهيئة المكونات
    if(document.getElementById('arabicPartModal')) {
        arabicPartModal = new bootstrap.Modal(document.getElementById('arabicPartModal'));
    }

    updateSubjects('subjectSelectChapter', 'gradeSelectChapter');
    updateSubjects('subjectSelectComp', 'gradeSelectComp');
    updateTopics();

    // استدعاء البيانات من السيرفر
    renderBooks();
    renderPapers();
    renderYoutube();
});

// ==========================================
// نظام التنقل والتحكم بالقوائم
// ==========================================
function setupNavigation() {
    const navLinks = document.querySelectorAll('.custom-nav-link');
    const sections = document.querySelectorAll('.content-section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            e.currentTarget.classList.add('active');

            sections.forEach(s => s.classList.add('d-none'));
            const targetId = e.currentTarget.getAttribute('data-target');
            document.getElementById(targetId).classList.remove('d-none');
        });
    });
}

function setupEventListeners() {
    // تحديث المواد والفصول
    document.getElementById('gradeSelectChapter').addEventListener('change', () => {
        updateSubjects('subjectSelectChapter', 'gradeSelectChapter');
        updateTopics();
    });
    document.getElementById('subjectSelectChapter').addEventListener('change', updateTopics);

    // أزرار التوليد (الذكاء الاصطناعي)
    document.getElementById('btnGenerateChapter').addEventListener('click', () => {
        const subject = document.getElementById('subjectSelectChapter').value;
        const topic = document.getElementById('topicSelect').value;
        generateQuestions(subject, topic);
    });

    const btnComp = document.getElementById('btnGenerateComp');
    if (btnComp) {
        btnComp.addEventListener('click', () => {
            const subject = document.getElementById('subjectSelectComp').value;
            generateQuestions(subject, "شامل");
        });
    }

    // القائمة الجانبية للموبايل
    const sidebar = document.getElementById("sidebar");
    const openBtn = document.getElementById("mobileMenuBtn");
    const closeBtn = document.getElementById("closeMenuBtn");
    const overlay = document.getElementById("sidebarOverlay");
    if(openBtn && closeBtn && sidebar && overlay){
        openBtn.addEventListener("click", () => { sidebar.classList.add("open"); overlay.classList.add("show"); });
        closeBtn.addEventListener("click", () => { sidebar.classList.remove("open"); overlay.classList.remove("show"); });
        overlay.addEventListener("click", () => { sidebar.classList.remove("open"); overlay.classList.remove("show"); });
    }
}

function updateSubjects(subjectSelectId, gradeSelectId) {
    const grade = document.getElementById(gradeSelectId).value;
    const subjectSelect = document.getElementById(subjectSelectId);
    subjectSelect.innerHTML = subjectsData[grade].map(subject => `<option value="${subject}">${subject}</option>`).join('');
}

function updateTopics() {
    const subject = document.getElementById('subjectSelectChapter').value;
    const topicLabel = document.getElementById('topicLabel');
    const topicSelect = document.getElementById('topicSelect');
    let optionsHTML = '';

    if (subject === "اللغة العربية") {
        topicLabel.innerText = "اختر الجزء:";
        optionsHTML = `<option value="الجزء الأول">الجزء الأول</option><option value="الجزء الثاني">الجزء الثاني</option>`;
    } else if (subject === "التربية الإسلامية" || subject === "اللغة الإنكليزية") {
        topicLabel.innerText = "اختر الوحدة:";
        optionsHTML = Array.from({length: 8}, (_, i) => `<option value="الوحدة ${i+1}">الوحدة ${i+1}</option>`).join('');
    } else {
        topicLabel.innerText = "اختر الفصل:";
        optionsHTML = Array.from({length: 8}, (_, i) => `<option value="الفصل ${i+1}">الفصل ${i+1}</option>`).join('');
    }
    topicSelect.innerHTML = optionsHTML;
}

// ==========================================
// جلب وعرض البيانات (كتب، وزاريات، يوتيوب)
// ==========================================
// التعديل داخل دالة renderBooks
async function renderBooks() {
    const grid = document.getElementById('booksGrid');
    try {
        const response = await fetch('/api/books');
        const books = await response.json();

        if (books.length === 0) {
            grid.innerHTML = '<p class="text-center">لا توجد كتب متوفرة حالياً.</p>';
            return;
        }

        const groupedBooks = {};
        books.forEach(book => {
            let cleanView = book.view_url.replace(/^assets\//, '');
            let cleanDown = book.download_url.replace(/^assets\//, '');

            book.final_view = "/assets/" + cleanView;
            book.final_down = "/assets/" + cleanDown;

            const mainSubject = book.title.includes("العربي") ? "اللغة العربية" :
                              (book.title.includes("الإنكليزية") || book.title.includes("انكليزي")) ? "اللغة الإنكليزية" : book.title;

            if (!groupedBooks[mainSubject]) groupedBooks[mainSubject] = [];
            groupedBooks[mainSubject].push(book);
        });

        grid.innerHTML = Object.keys(groupedBooks).map(subject => {
            const parts = groupedBooks[subject];
            const isArabic = subject === "اللغة العربية" && parts.length >= 2;

            // تحقق إذا كانت المادة إنكليزي
            const isEnglish = subject === "اللغة الإنكليزية";
            // مسار كتاب الطالب الثابت اللي ردته
            const studentBookPath = "/assets/books/english.pdf";

            return `
            <div class="col-md-6 col-lg-4 col-xl-3">
                <div class="card h-100 item-card text-center border-0">
                    <div class="mb-3">
                        <span class="p-3 d-inline-block rounded-circle" style="background: rgba(102, 126, 234, 0.1);">
                            <i class="bi bi-book-half fs-1" style="color: #667eea;"></i>
                        </span>
                    </div>
                    <h4 class="fw-bold" style="color: var(--text-dark);">${subject}</h4>
                    <p class="text-muted small mb-4">سادس علمي</p>
                    <div class="d-flex gap-2 mt-auto">
                        ${isArabic ? `
                            <button class="btn btn-light w-100 fw-bold rounded-3" onclick="handleArabicClick('${parts[0].final_view}', '${parts[1].final_view}', 'مشاهدة')">👁️ مشاهدة</button>
                            <button class="btn btn-grad-primary w-100 fw-bold rounded-3" onclick="handleArabicClick('${parts[0].final_down}', '${parts[1].final_down}', 'تحميل')">📥 تحميل</button>
                        ` : isEnglish ? `
                            <button class="btn btn-light w-100 fw-bold rounded-3" onclick="handleEnglishClick('${studentBookPath}', '${parts[0].final_view}', 'مشاهدة')">👁️ مشاهدة</button>
                            <button class="btn btn-grad-primary w-100 fw-bold rounded-3" onclick="handleEnglishClick('${studentBookPath}', '${parts[0].final_down}', 'تحميل')">📥 تحميل</button>
                        ` : `
                            <a href="${parts[0].final_view}" target="_blank" class="btn btn-light w-100 fw-bold rounded-3">👁️ مشاهدة</a>
                            <a href="${parts[0].final_down}" download class="btn btn-grad-primary w-100 fw-bold rounded-3">📥 تحميل</a>
                        `}
                    </div>
                </div>
            </div>`;
        }).join('');
    } catch (error) {
        console.error("Error loading books:", error);
    }
}

// دالة التحكم بالإنكليزي (تستخدم نفس المودال مال العربي بس نغير النصوص برمجياً)
// دالة التحكم بالإنكليزي - تأكد من وجود window. في البداية// 1. دالة اللغة العربية (تكتب نصوص العربي دائماً عند التشغيل)
window.handleArabicClick = function(linkPart1, linkPart2, action) {
    currentArabicAction = action;

    // التأكد من تهيئة المودال
    if(!arabicPartModal) arabicPartModal = new bootstrap.Modal(document.getElementById('arabicPartModal'));

    // ضبط نصوص العربي فوراً
    document.getElementById('arabicModalTitle').innerText = `${action} كتاب العربي`;
    document.getElementById('arabicModalDesc').innerText = "الرجاء اختيار الجزء المراد التعامل معه:";

    const btn1 = document.getElementById('btnPart1');
    const btn2 = document.getElementById('btnPart2');

    btn1.innerHTML = `<i class="bi bi-journal-text me-2 text-primary"></i>الجزء الأول`;
    btn2.innerHTML = `<i class="bi bi-journal-bookmark-fill me-2"></i>الجزء الثاني`;

    btn1.onclick = () => {
        if(action === 'مشاهدة') window.open(linkPart1, '_blank');
        else { const a = document.createElement('a'); a.href = linkPart1; a.download = 'Arabic_Part1.pdf'; a.click(); }
        arabicPartModal.hide();
    };

    btn2.onclick = () => {
        if(action === 'مشاهدة') window.open(linkPart2, '_blank');
        else { const a = document.createElement('a'); a.href = linkPart2; a.download = 'Arabic_Part2.pdf'; a.click(); }
        arabicPartModal.hide();
    };

    arabicPartModal.show();
};

// 2. دالة اللغة الإنكليزية (تكتب نصوص الإنكليزي دائماً عند التشغيل)
window.handleEnglishClick = function(studentPath, activityPath, action) {
    currentArabicAction = action;

    if(!arabicPartModal) arabicPartModal = new bootstrap.Modal(document.getElementById('arabicPartModal'));

    // ضبط نصوص الإنكليزي فوراً
    document.getElementById('arabicModalTitle').innerText = `${action} كتاب الإنكليزي`;
    document.getElementById('arabicModalDesc').innerText = "الرجاء اختيار الكتاب:";

    const btn1 = document.getElementById('btnPart1');
    const btn2 = document.getElementById('btnPart2');

    btn1.innerHTML = `<i class="bi bi-journal-text me-2 text-primary"></i>كتاب الطالب`;
    btn2.innerHTML = `<i class="bi bi-journal-check me-2 text-success"></i>كتاب النشاط`;

    btn1.onclick = () => {
        if(action === 'مشاهدة') window.open(studentPath, '_blank');
        else { const a = document.createElement('a'); a.href = studentPath; a.download = 'English_Student.pdf'; a.click(); }
        arabicPartModal.hide();
        resetModalTexts(); // اختيارية لزيادة الأمان
    };

    btn2.onclick = () => {
        if(action === 'مشاهدة') window.open(activityPath, '_blank');
        else { const a = document.createElement('a'); a.href = activityPath; a.download = 'English_Activity.pdf'; a.click(); }
        arabicPartModal.hide();
        resetModalTexts(); // اختيارية لزيادة الأمان
    };

    arabicPartModal.show();
};

// 3. دالة الـ Reset (بناءً على طلبك بقت مثل ما هي)
function resetModalTexts() {
    setTimeout(() => {
        const title = document.getElementById('arabicModalTitle');
        const desc = document.getElementById('arabicModalDesc');
        const b1 = document.getElementById('btnPart1');
        const b2 = document.getElementById('btnPart2');

        if(title) title.innerText = `اختيار الجزء`;
        if(desc) desc.innerText = "الرجاء اختيار الجزء المراد التعامل معه:";
        if(b1) b1.innerHTML = `<i class="bi bi-journal-text me-2 text-primary"></i>الجزء الأول`;
        if(b2) b2.innerHTML = `<i class="bi bi-journal-bookmark-fill me-2"></i>الجزء الثاني`;
    }, 500);
}
// جلب وعرض الوزاريات من السيرفر
async function renderPapers() {
    const grid = document.getElementById('papersGrid');
    try {
        const response = await fetch('/api/papers');
        const papers = await response.json();

        if (papers.length === 0) {
            grid.innerHTML = '<p class="text-center">لا توجد وزاريات متوفرة حالياً.</p>';
            return;
        }

        // تصفية البيانات لعرض العربي مرة واحدة فقط (شامل)
        const uniquePapers = [];
        const seenSubjects = new Set();

        papers.forEach(paper => {
            // توحيد المسمى ليكون "اللغة العربية" فقط
            const displayTitle = paper.title.includes("العربي") ? "اللغة العربية" : paper.title;

            if (!seenSubjects.has(displayTitle)) {
                seenSubjects.add(displayTitle);
                uniquePapers.push({
                    ...paper,
                    displayTitle: displayTitle
                });
            }
        });

        grid.innerHTML = uniquePapers.map(paper => `
            <div class="col-md-6 col-lg-4 col-xl-3">
                <div class="card h-100 item-card text-center border-0 shadow-sm">
                    <div class="mb-3">
                        <span class="p-3 d-inline-block rounded-circle" style="background: rgba(0, 158, 253, 0.1);">
                            <i class="bi bi-file-earmark-pdf fs-1" style="color: #009efd;"></i>
                        </span>
                    </div>
                    <h5 class="fw-bold" style="color: #2d3436;">${paper.displayTitle}</h5>
                    <p class="text-muted small">الأسئلة الوزارية الشاملة</p>

                    <div class="d-flex gap-2 mt-auto">
                        <a href="${paper.view_url}" target="_blank" class="btn btn-light w-100 fw-bold rounded-3">👁️ مشاهدة</a>
                        <a href="${paper.download_url}" download class="btn btn-grad-secondary w-100 fw-bold rounded-3">📥 تحميل</a>
                    </div>
                </div>
            </div>`).join('');
    } catch (error) {
        console.error("Error loading papers:", error);
    }
}



function renderYoutube() {
    const grid = document.getElementById('youtubeGrid');
    grid.innerHTML = youtubeChannels.map(ch => `
        <div class="col-md-6 col-lg-4">
            <div class="card h-100 item-card text-center border-0">
                <div class="mb-3"><span class="p-3 d-inline-block rounded-circle" style="background: rgba(255, 75, 75, 0.1);"><i class="bi bi-youtube fs-1" style="color: #ff4b4b;"></i></span></div>
                <h4 class="fw-bold">${ch.name}</h4>
                <p class="text-muted small mb-4">${ch.desc}</p>
                <a href="${ch.link}" target="_blank" class="btn btn-light w-100 fw-bold rounded-3 mt-auto">📺 انتقال للقناة</a>
            </div>
        </div>`).join('');
}



// ==========================================
// نظام توليد وعرض الأسئلة (الذكاء الاصطناعي)
// ==========================================
async function generateQuestions(subject, topic) {
    const resultDiv = document.getElementById('resultDiv');
    const container = document.getElementById('generatedQuestionsContainer');

    resultDiv.classList.remove('d-none');
    resultDiv.scrollIntoView({ behavior: 'smooth' });

    container.innerHTML = `<div class="text-center py-5"><div class="spinner-grow text-primary"></div><p class="mt-3 fw-bold">الذكاء الاصطناعي يولد الأسئلة الآن...</p></div>`;

    const data = await fetchExamData(subject, topic);

    if (data && data.questions) {
        container.innerHTML = `
            <div class="animate-card">
                <h4 class="fw-bold text-center mb-4" style="color: #667eea;">📝 أسئلة ${subject} - ${topic}</h4>
                <div>${data.questions}</div>
                <div class="text-center mt-4">
                    <button class="btn btn-grad-secondary px-5 py-2 fw-bold" id="btnShowAnswers">عرض الأجوبة</button>
                </div>
                <div id="answersBox" class="mt-4 d-none">${data.answers}</div>
            </div>`;

        document.getElementById('btnShowAnswers').onclick = function() {
            const box = document.getElementById('answersBox');
            box.classList.toggle('d-none');
        };
        if (window.MathJax) MathJax.typesetPromise();
    } else {
        container.innerHTML = `<div class="alert alert-danger">⚠️ تأكد من تشغيل السيرفر (FastAPI)</div>`;
    }
}

async function fetchExamData(subject, topic) {
    try {
        // 1. تنظيف التوبك وتجهيز المسار
        let cleanTopic = topic.toString().replace(/[^0-9]/g, '');
        if (topic === "شامل") cleanTopic = "شامل";
        if (topic.includes("الجزء")) cleanTopic = topic.includes("الأول") ? "1" : "2";

        const apiUrl = '/api/exams/generate';

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject: subject,
                topic: cleanTopic,
                grade: "سادس علمي"
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Server Error:", errorText);
            return null;
        }

        const data = await response.json();

        if (data.status === "success") {
            // 2. تنسيق الأسئلة (UI Cards)
            let qHtml = data.exam_data.exam_paper.map(q => `
                <div class="mb-4 shadow-sm p-3 bg-white rounded-3 border-start border-4 border-primary text-end animate-card">
                    <h5 class="fw-bold text-primary">${q.question_number}</h5>
                    <hr>
                    ${q.branches.map(b => `
                        <div class="ms-3 mb-3 p-2">
                            <span class="fw-bold text-dark">(${b.branch})</span>
                            <span class="ms-2">${b.question_text}</span>
                            <span class="badge bg-light text-primary border float-start">${b.marks} د</span>
                        </div>`).join('')}
                </div>
            `).join('');

            // 3. تنسيق الأجوبة النموذجية (UI Cards منفصلة)
            // نفحص الهيكل القادم من الـ AI للتأكد من الوصول للمصفوفة الصحيحة
            const answersArray = data.answers_data.model_answers || data.answers_data.answers_data || [];

            let aHtml = `
                <div class="alert alert-success text-center fw-bold mb-4">✨ الأجوبة النموذجية الذكية</div>
                ${answersArray.map(ans => `
                    <div class="mb-4 shadow-sm p-3 bg-white rounded-3 border-start border-4 border-success text-end animate-card">
                        <h6 class="fw-bold text-success border-bottom pb-2">جواب ${ans.question_number}</h6>
                        ${ans.branches.map(ab => `
                            <div class="ms-3 mt-3">
                                <div class="badge bg-success-soft text-success mb-2 p-2">فرع (${ab.branch})</div>
                                <div class="p-3 bg-light rounded-3 border-0" style="line-height: 1.8;">
                                    ${Array.isArray(ab.answer_steps) ? ab.answer_steps.join('<br>') : ab.answer_steps}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `).join('')}`;

            return {
                questions: qHtml,
                answers: aHtml
            };
        }
        return null;
    } catch (e) {
        console.error("Request failed:", e);
        return null;
    }
}
// === نظام الإشعارات (Toast) ===
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const color = type === 'success' ? '#2af598' : '#667eea';
    const toastHtml = `<div class="toast custom-toast border-0" role="alert"><div class="toast-body d-flex align-items-center p-3"><div style="width:14px; height:14px; background:${color}; border-radius:50%; margin-left:15px;"></div><div class="fw-bold">${message}</div><button type="button" class="btn-close ms-auto" data-bs-dismiss="toast"></button></div></div>`;
    const element = new DOMParser().parseFromString(toastHtml, 'text/html').body.firstChild;
    container.appendChild(element);
    new bootstrap.Toast(element, {delay: 3000}).show();
    element.addEventListener('hidden.bs.toast', () => element.remove());
}