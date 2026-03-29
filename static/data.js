// دالة جلب الكتب
async function fetchBooks() {
    try {
        // نستخدم المسار المباشر بدون كتابة http أو IP
        const response = await fetch('/api/books');
        return await response.json();
    } catch (error) {
        console.error("خطأ في جلب الكتب:", error);
        return [];
    }
}

// دالة جلب الوزاريات
async function fetchPapers() {
    try {
        const response = await fetch('/api/papers');
        return await response.json();
    } catch (error) {
        console.error("خطأ في جلب الوزاريات:", error);
        return [];
    }
}