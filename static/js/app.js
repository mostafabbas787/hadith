/**
 * ملف JavaScript الرئيسي - محسّن
 * Main JavaScript file for Hadith Video Generator - Enhanced Version
 * @version 2.0.0
 * @author Hadith Video Generator Team
 */

// =============================================
// متغيرات للفيديو غير المتزامن
// =============================================
let currentJobId = null;
let progressCheckInterval = null;
let asyncModeEnabled = false;
let kieModeEnabled = false;

// =============================================
// متغيرات عامة - Global Variables
// =============================================
let selectedHadith = null;
let currentVideoPath = null;
let favorites = JSON.parse(localStorage.getItem('hadithFavorites') || '[]');
let searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
let generationHistory = JSON.parse(localStorage.getItem('generationHistory') || '[]');

// =============================================
// عناصر DOM - DOM Elements
// =============================================
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsList = document.getElementById('resultsList');
const progressSection = document.getElementById('progressSection');
const progressBarFill = document.getElementById('progressBarFill');
const progressText = document.getElementById('progressText');
const previewSection = document.getElementById('previewSection');
const videoPreview = document.getElementById('videoPreview');
const downloadBtn = document.getElementById('downloadBtn');
const newVideoBtn = document.getElementById('newVideoBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const errorMessage = document.getElementById('errorMessage');
const nightModeToggle = document.getElementById('nightModeToggle');

// عناصر الخيارات المتقدمة
const toggleAdvancedBtn = document.getElementById('toggleAdvancedBtn');
const advancedOptions = document.getElementById('advancedOptions');
const generatePromptBtn = document.getElementById('generatePromptBtn');
const refreshStatusBtn = document.getElementById('refreshStatusBtn');
const customPrompt = document.getElementById('customPrompt');
const asyncModeToggle = document.getElementById('asyncModeToggle');
const kieModeToggle = document.getElementById('kieModeToggle');

// عناصر جديدة
const clearSearchBtn = document.getElementById('clearSearchBtn');
const cancelGenerationBtn = document.getElementById('cancelGenerationBtn');
const shareBtn = document.getElementById('shareBtn');
const helpBtn = document.getElementById('helpBtn');
const helpModal = document.getElementById('helpModal');
const closeHelpModal = document.getElementById('closeHelpModal');
const resultsCount = document.getElementById('resultsCount');
const progressDetail = document.getElementById('progressDetail');
const videoDuration = document.getElementById('videoDuration');
const toastContainer = document.getElementById('toastContainer');
const loadingText = document.getElementById('loadingText');
let currentAbortController = null;

// =============================================
// الوضع الليلي - Night Mode
// =============================================

// تحقق من تفضيل المستخدم المحفوظ
if (localStorage.getItem('nightMode') === 'true') {
    document.body.classList.add('night-mode');
    if (nightModeToggle) nightModeToggle.textContent = '☀️';
}

// مستمع حدث تبديل الوضع الليلي
if (nightModeToggle) {
    nightModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('night-mode');
        const isNightMode = document.body.classList.contains('night-mode');
        localStorage.setItem('nightMode', isNightMode);
        const iconSpan = nightModeToggle.querySelector('.icon');
        if (iconSpan) iconSpan.textContent = isNightMode ? '☀️' : '🌙';
        showToast(isNightMode ? 'تم تفعيل الوضع الليلي' : 'تم تفعيل الوضع النهاري', 'info');
    });
}

// =============================================
// مستمعي الأحداث - Event Listeners
// =============================================
searchBtn.addEventListener('click', handleSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSearch();
    }
});

downloadBtn.addEventListener('click', handleDownload);
newVideoBtn.addEventListener('click', handleNewVideo);

// مستمعي الخيارات المتقدمة
if (toggleAdvancedBtn) {
    toggleAdvancedBtn.addEventListener('click', toggleAdvancedOptions);
}

if (generatePromptBtn) {
    generatePromptBtn.addEventListener('click', handleGeneratePrompt);
}

// مستمع زر توليد الأوامر بالذكاء الاصطناعي
if (refreshStatusBtn) {
    refreshStatusBtn.addEventListener('click', refreshAIStatus);
}

// مستمع زر الوضع غير المتزامن
if (asyncModeToggle) {
    asyncModeToggle.addEventListener('change', (e) => {
        asyncModeEnabled = e.target.checked;
        showToast(
            asyncModeEnabled ? 'تم تفعيل الوضع غير المتزامن' : 'تم إيقاف الوضع غير المتزامن',
            'info'
        );
    });
}

// مستمع زر وضع KIE
if (kieModeToggle) {
    kieModeToggle.addEventListener('change', (e) => {
        kieModeEnabled = e.target.checked;
        showToast(
            kieModeEnabled ? 'تم تفعيل وضع KIE AI' : 'تم إيقاف وضع KIE AI',
            kieModeEnabled ? 'success' : 'info'
        );
    });
}
const generateAIPromptBtn = document.getElementById('generateAIPromptBtn');
if (generateAIPromptBtn) {
    generateAIPromptBtn.addEventListener('click', handleGenerateAIPrompt);
}

if (refreshStatusBtn) {
    refreshStatusBtn.addEventListener('click', refreshAIStatus);
}

// =============================================
// مستمعي الأحداث الجديدة - New Event Listeners
// =============================================

// زر مسح البحث
if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        clearSearchBtn.style.display = 'none';
        searchInput.focus();
    });
}

// إظهار/إخفاء زر المسح حسب محتوى الحقل
if (searchInput) {
    searchInput.addEventListener('input', () => {
        clearSearchBtn.style.display = searchInput.value.length > 0 ? 'flex' : 'none';
    });
}

// أزرار البحث السريع
document.querySelectorAll('.quick-tag').forEach(tag => {
    tag.addEventListener('click', () => {
        searchInput.value = tag.dataset.search;
        clearSearchBtn.style.display = 'flex';
        handleSearch();
    });
});

// التبويبات
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // إزالة الحالة النشطة من جميع التبويبات
        document.querySelectorAll('.tab-btn').forEach(b => {
            b.classList.remove('active');
            b.setAttribute('aria-selected', 'false');
        });
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // تفعيل التبويب المحدد
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        const tabId = btn.dataset.tab;
        const tabContent = document.getElementById(tabId);
        if (tabContent) tabContent.classList.add('active');
    });
});

// أزرار القوالب
document.querySelectorAll('.template-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if (customPrompt) {
            customPrompt.value = btn.dataset.template;
            showToast('تم تطبيق القالب', 'success');
        }
    });
});

// زر الإلغاء
if (cancelGenerationBtn) {
    cancelGenerationBtn.addEventListener('click', () => {
        if (currentAbortController) {
            currentAbortController.abort();
            currentAbortController = null;
        }
        progressSection.style.display = 'none';
        resultsSection.style.display = 'block';
        showToast('تم إلغاء العملية', 'warning');
    });
}

// زر المشاركة
if (shareBtn) {
    shareBtn.addEventListener('click', async () => {
        if (!currentVideoPath) {
            showToast('لا يوجد فيديو للمشاركة', 'error');
            return;
        }

        const shareUrl = `${window.location.origin}/api/preview/${currentVideoPath}`;

        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'فيديو حديث نبوي',
                    text: selectedHadith ? selectedHadith.text.substring(0, 100) + '...' : 'فيديو حديث نبوي',
                    url: shareUrl
                });
                showToast('تمت المشاركة بنجاح', 'success');
            } catch (err) {
                if (err.name !== 'AbortError') {
                    copyToClipboard(shareUrl);
                }
            }
        } else {
            copyToClipboard(shareUrl);
        }
    });
}

// نسخ الرابط للحافظة
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('تم نسخ الرابط للحافظة', 'success');
    }).catch(() => {
        showToast('فشل في نسخ الرابط', 'error');
    });
}

// زر المساعدة
if (helpBtn) {
    helpBtn.addEventListener('click', () => {
        if (helpModal) helpModal.style.display = 'flex';
    });
}

// إغلاق نافذة المساعدة
if (closeHelpModal) {
    closeHelpModal.addEventListener('click', () => {
        if (helpModal) helpModal.style.display = 'none';
    });
}

// إغلاق النافذة عند النقر على الخلفية
if (helpModal) {
    helpModal.querySelector('.modal-overlay')?.addEventListener('click', () => {
        helpModal.style.display = 'none';
    });
}

// إغلاق النافذة بزر Escape
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && helpModal && helpModal.style.display !== 'none') {
        helpModal.style.display = 'none';
    }
});

// =============================================
// اختصارات لوحة المفاتيح - Keyboard Shortcuts
// =============================================

document.addEventListener('keydown', (e) => {
    // تجنب الاختصارات أثناء الكتابة في الحقول
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        // فقط Enter للبحث
        if (e.key === 'Enter' && e.target === searchInput) {
            e.preventDefault();
            handleSearch();
        }
        return;
    }

    // Ctrl/Cmd + K: التركيز على البحث
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
    }

    // Ctrl/Cmd + /: عرض المساعدة
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        if (helpModal) {
            helpModal.style.display = helpModal.style.display === 'none' ? 'flex' : 'none';
        }
    }

    // Ctrl/Cmd + F: عرض المفضلة
    if ((e.ctrlKey || e.metaKey) && e.key === 'f' && !e.shiftKey) {
        e.preventDefault();
        showFavoritesModal();
    }

    // N: الوضع الليلي
    if (e.key === 'n' && !e.ctrlKey && !e.metaKey) {
        if (nightModeToggle) nightModeToggle.click();
    }

    // D: تحميل الفيديو (إذا كان متاحاً)
    if (e.key === 'd' && !e.ctrlKey && !e.metaKey && currentVideoPath) {
        handleDownload();
    }

    // Escape: إغلاق النوافذ
    if (e.key === 'Escape') {
        // إغلاق جميع النوافذ المنبثقة
        const modals = document.querySelectorAll('.modal[style*="flex"]');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });

        // إخفاء سجل البحث
        hideSearchHistory();
    }
});

// =============================================
// وظائف الخيارات المتقدمة - Advanced Options Functions
// =============================================

/**
 * تبديل عرض الخيارات المتقدمة
 * Toggle advanced options display
 */
function toggleAdvancedOptions() {
    if (advancedOptions) {
        const isHidden = advancedOptions.style.display === 'none';
        advancedOptions.style.display = isHidden ? 'block' : 'none';

        // تحديث الزر
        const toggleIcon = toggleAdvancedBtn.querySelector('.toggle-icon');
        const toggleText = toggleAdvancedBtn.querySelector('.toggle-text');
        const toggleArrow = toggleAdvancedBtn.querySelector('.toggle-arrow');

        if (toggleText) toggleText.textContent = isHidden ? 'إخفاء الخيارات المتقدمة' : 'خيارات متقدمة';
        if (toggleArrow) toggleArrow.textContent = isHidden ? '▲' : '▼';
        toggleAdvancedBtn.setAttribute('aria-expanded', isHidden);

        // تحديث حالة AI عند الفتح
        if (isHidden) {
            refreshAIStatus();
        }
    }
}

/**
 * تحديث حالة خدمات AI
 * Refresh AI services status
 */
async function refreshAIStatus() {
    try {
        const response = await fetch('/api/ai_status');
        const data = await response.json();

        if (data.success && data.status) {
            // Voice
            updateStatusIndicator('statusElevenlabs', data.status.elevenlabs, 'ElevenLabs');

            // Images
            updateStatusIndicator('statusOpenai', data.status.openai_image, 'OpenAI');
            updateStatusIndicator('statusStability', data.status.stability, 'Stability');
            updateStatusIndicator('statusGemini', data.status.gemini, 'Gemini');
            updateStatusIndicator('statusOpenrouter', data.status.openrouter, 'OpenRouter');

            // Video
            updateStatusIndicator('statusVideoGen', data.status.video_gen, 'Video API');
            updateStatusIndicator('statusKling', data.status.kling, 'Kling');
            updateStatusIndicator('statusVeo', data.status.veo, 'Veo');
            updateStatusIndicator('statusLocalVideo', data.status.local_video, 'Local');

            // Local
            updateStatusIndicator('statusAudioEnhancer', data.status.audio_enhancer, 'Audio');
            updateStatusIndicator('statusVideoEnhancer', data.status.video_enhancer, 'Video');
            updateStatusIndicator('statusOllama', data.status.ollama, 'Ollama');
        }
    } catch (error) {
        console.error('خطأ في جلب حالة AI:', error);
    }
}

/**
 * تحديث مؤشر الحالة
 * Update status indicator
 */
function updateStatusIndicator(elementId, isActive, label) {
    const element = document.getElementById(elementId);
    if (element) {
        const statusDot = element.querySelector('.status-dot');
        const statusName = element.querySelector('.status-name');
        if (statusName) statusName.textContent = label;
        element.className = `status-item ${isActive ? 'active' : 'inactive'}`;
    }
}

/**
 * عرض إشعار Toast
 * Show toast notification
 */
function showToast(message, type = 'info') {
    if (!toastContainer) return;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    toastContainer.appendChild(toast);

    // إزالة تلقائية بعد 4 ثواني
    setTimeout(() => {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * توليد أمر نصي للخلفية
 * Generate prompt for background
 */
async function handleGeneratePrompt() {
    if (!selectedHadith && !searchInput.value) {
        showError('الرجاء البحث عن حديث أولاً');
        return;
    }

    try {
        const hadithText = selectedHadith ? selectedHadith.text : searchInput.value;
        const style = getSelectedVideoType();

        const response = await fetch('/api/generate_prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hadith_text: hadithText,
                style: style
            })
        });

        const data = await response.json();

        if (data.success && data.prompt) {
            customPrompt.value = data.prompt;
            showSuccess('تم توليد الأمر النصي بنجاح');
        } else {
            showError(data.error || 'فشل في توليد الأمر');
        }
    } catch (error) {
        console.error('خطأ في توليد الأمر:', error);
        showError('خطأ في توليد الأمر النصي');
    }
}

/**
 * توليد أمر نصي بالذكاء الاصطناعي
 * Generate AI prompt using AI provider
 */
async function handleGenerateAIPrompt() {
    if (!selectedHadith && !searchInput.value) {
        showError('الرجاء البحث عن حديث أولاً');
        return;
    }

    try {
        showLoading();
        const hadithText = selectedHadith ? selectedHadith.text : searchInput.value;
        const style = getSelectedVideoType();
        const provider = document.getElementById('promptProviderSelect')?.value || 'gemini';

        const response = await fetch('/api/generate_ai_prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                description: hadithText,
                style: style,
                provider: provider
            })
        });

        const data = await response.json();

        if (data.success && data.prompt) {
            customPrompt.value = data.prompt;
            showSuccess(`تم توليد الأمر بنجاح باستخدام ${data.provider}`);
        } else {
            showError(data.error || 'فشل في توليد الأمر');
        }
    } catch (error) {
        console.error('خطأ في توليد الأمر AI:', error);
        showError('خطأ في توليد الأمر النصي بالذكاء الاصطناعي');
    } finally {
        hideLoading();
    }
}

/**
 * الحصول على خيارات التوليد المتقدمة
 * Get advanced generation options
 */
function getAdvancedOptions() {
    return {
        use_ai_voice: document.getElementById('useElevenLabs')?.checked || false,
        use_ai_background: document.getElementById('useAIBackground')?.checked || false,
        use_ai_video: document.getElementById('useAIVideo')?.checked || false,
        use_local_video: document.getElementById('useLocalVideo')?.checked || true,
        use_multiple_images: document.getElementById('useMultipleImages')?.checked || false,
        image_count: parseInt(document.getElementById('imageCountSelect')?.value) || 5,
        image_duration: parseInt(document.getElementById('imageDurationSelect')?.value) || 3,
        image_provider: document.getElementById('imageProviderSelect')?.value || 'openai',
        video_provider: document.getElementById('videoProviderSelect')?.value || 'local',
        prompt_provider: document.getElementById('promptProviderSelect')?.value || 'local',
        enhance_locally: document.getElementById('enhanceVideo')?.checked || true,
        enhance_audio: document.getElementById('enhanceAudio')?.checked || true,
        ken_burns: document.getElementById('kenBurnsEffect')?.checked || true,
        vignette: document.getElementById('vignetteEffect')?.checked || true,
        film_grain: document.getElementById('filmGrainEffect')?.checked || false,
        custom_prompt: customPrompt?.value || '',
        voice: document.getElementById('voiceSelect')?.value || 'ar-SA-HamedNeural'
    };
}

// =============================================
// وظائف المساعدة - Helper Functions
// =============================================

/**
 * عرض رسالة خطأ
 * Display error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.className = 'error-message';

    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

/**
 * عرض رسالة نجاح
 * Display success message
 */
function showSuccess(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.className = 'success-message';

    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 3000);
}

/**
 * إخفاء رسالة الخطأ
 * Hide error message
 */
function hideError() {
    errorMessage.style.display = 'none';
}

/**
 * عرض شاشة التحميل
 * Show loading overlay
 */
function showLoading(text = 'جاري المعالجة...') {
    if (loadingText) loadingText.textContent = text;
    loadingOverlay.style.display = 'flex';
}

/**
 * إخفاء شاشة التحميل
 * Hide loading overlay
 */
function hideLoading() {
    loadingOverlay.style.display = 'none';
}

/**
 * تحديث نص التحميل
 * Update loading text
 */
function updateLoadingText(text) {
    if (loadingText) loadingText.textContent = text;
}

/**
 * تحديث شريط التقدم
 * Update progress bar
 */
function updateProgress(percentage, text) {
    progressBarFill.style.width = `${percentage}%`;
    progressText.textContent = text;
}

/**
 * تحديث حالة الخطوة
 * Update step status
 */
function updateStep(stepNumber, status) {
    const step = document.getElementById(`step${stepNumber}`);
    if (step) {
        step.classList.remove('active', 'completed');
        if (status === 'active') {
            step.classList.add('active');
        } else if (status === 'completed') {
            step.classList.add('completed');
        }
    }
}

/**
 * الحصول على نوع الفيديو المحدد
 * Get selected video type
 */
function getSelectedVideoType() {
    const selectedRadio = document.querySelector('input[name="videoType"]:checked');
    return selectedRadio ? selectedRadio.value : 'nature calm';
}

// =============================================
// وظائف البحث - Search Functions
// =============================================

/**
 * معالجة البحث عن الأحاديث
 * Handle hadith search
 */
async function handleSearch() {
    const keyword = searchInput.value.trim();

    if (!keyword) {
        showError('الرجاء إدخال كلمة مفتاحية للبحث');
        searchInput.focus();
        return;
    }

    // Validate keyword length
    if (keyword.length < 2) {
        showError('كلمة البحث قصيرة جداً، الرجاء إدخال كلمتين على الأقل');
        return;
    }

    hideError();
    showLoading('جاري البحث عن الأحاديث...');

    // Save to search history
    saveToSearchHistory(keyword);

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ keyword }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'حدث خطأ في البحث');
        }

        if (!data.hadiths || data.hadiths.length === 0) {
            showError('لم يتم العثور على نتائج. جرب كلمة بحث أخرى.');
            resultsSection.style.display = 'none';
            return;
        }

        displayResults(data.hadiths);

    } catch (error) {
        console.error('خطأ في البحث:', error);

        if (error.name === 'AbortError') {
            showError('انتهت مهلة البحث. الرجاء المحاولة مرة أخرى.');
        } else if (!navigator.onLine) {
            showError('لا يوجد اتصال بالإنترنت. تحقق من اتصالك وحاول مرة أخرى.');
        } else {
            showError(`خطأ في البحث: ${error.message}`);
        }
    } finally {
        hideLoading();
    }
}

/**
 * حفظ في سجل البحث
 * Save to search history
 */
function saveToSearchHistory(keyword) {
    // Remove if already exists
    searchHistory = searchHistory.filter(item => item.keyword !== keyword);

    // Add to beginning
    searchHistory.unshift({
        keyword,
        timestamp: new Date().toISOString()
    });

    // Keep only last 20 searches
    searchHistory = searchHistory.slice(0, 20);

    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
}

/**
 * عرض سجل البحث
 * Show search history dropdown
 */
function showSearchHistory() {
    if (searchHistory.length === 0) return;

    // Create or update dropdown
    let dropdown = document.getElementById('searchHistoryDropdown');

    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'searchHistoryDropdown';
        dropdown.className = 'search-history-dropdown';
        searchInput.parentElement.appendChild(dropdown);
    }

    dropdown.innerHTML = `
        <div class="history-header">
            <span>🕐 البحث السابق</span>
            <button class="clear-history-btn" onclick="clearSearchHistory()">مسح</button>
        </div>
        ${searchHistory.slice(0, 5).map(item => `
            <div class="history-item" onclick="searchFromHistory('${escapeHtml(item.keyword)}')">
                <span class="history-icon">🔍</span>
                <span class="history-keyword">${escapeHtml(item.keyword)}</span>
            </div>
        `).join('')}
    `;

    dropdown.style.display = 'block';
}

/**
 * البحث من السجل
 * Search from history
 */
function searchFromHistory(keyword) {
    searchInput.value = keyword;
    hideSearchHistory();
    handleSearch();
}

/**
 * إخفاء سجل البحث
 * Hide search history
 */
function hideSearchHistory() {
    const dropdown = document.getElementById('searchHistoryDropdown');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

/**
 * مسح سجل البحث
 * Clear search history
 */
function clearSearchHistory() {
    searchHistory = [];
    localStorage.removeItem('searchHistory');
    hideSearchHistory();
    showToast('تم مسح سجل البحث', 'info');
}

/**
 * عرض نتائج البحث
 * Display search results
 */
function displayResults(hadiths) {
    if (!hadiths || hadiths.length === 0) {
        resultsList.innerHTML = '<p class="text-center">لم يتم العثور على نتائج</p>';
        if (resultsCount) resultsCount.textContent = '';
        resultsSection.style.display = 'block';
        return;
    }

    // تحديث عدد النتائج
    if (resultsCount) {
        resultsCount.textContent = `${hadiths.length} نتيجة`;
    }

    resultsList.innerHTML = '';

    hadiths.forEach((hadith, index) => {
        const hadithCard = createHadithCard(hadith, index);
        resultsList.appendChild(hadithCard);
    });

    resultsSection.style.display = 'block';

    // التمرير إلى النتائج
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    showToast(`تم العثور على ${hadiths.length} حديث`, 'success');
}

/**
 * إنشاء بطاقة الحديث المحسنة
 * Create improved hadith card
 */
function createHadithCard(hadith, index) {
    const card = document.createElement('div');
    card.className = 'hadith-card';
    card.setAttribute('data-index', index);
    card.setAttribute('data-hadith-id', hadith.id || index);

    // Check if this hadith is in favorites
    const isFavorite = favorites.some(fav => fav.text === hadith.text);

    // === عنوان بسم الله ===
    const header = document.createElement('div');
    header.className = 'hadith-header';
    header.innerHTML = '﷽';
    card.appendChild(header);

    // === نص الحديث ===
    const hadithText = document.createElement('div');
    hadithText.className = 'hadith-text';
    hadithText.textContent = hadith.text || 'نص الحديث غير متوفر';
    card.appendChild(hadithText);

    // === قسم المعلومات المنظمة ===
    const infoSection = document.createElement('div');
    infoSection.className = 'hadith-info-section';

    // الراوي
    if (hadith.narrator && hadith.narrator.trim()) {
        const narratorDiv = document.createElement('div');
        narratorDiv.className = 'hadith-info-item narrator-info';
        narratorDiv.innerHTML = `
            <span class="info-icon">📜</span>
            <span class="info-label">الراوي:</span>
            <span class="info-value">${escapeHtml(hadith.narrator)}</span>
        `;
        infoSection.appendChild(narratorDiv);
    }

    // المحدث/المصدر
    if (hadith.source && hadith.source.trim()) {
        const sourceDiv = document.createElement('div');
        sourceDiv.className = 'hadith-info-item source-info';
        sourceDiv.innerHTML = `
            <span class="info-icon">📚</span>
            <span class="info-label">المحدث:</span>
            <span class="info-value">${escapeHtml(hadith.source)}</span>
        `;
        infoSection.appendChild(sourceDiv);
    }

    // درجة الصحة
    if (hadith.grade && hadith.grade.trim()) {
        const gradeDiv = document.createElement('div');
        gradeDiv.className = 'hadith-info-item grade-info';

        // تحديد لون ونمط الدرجة
        let gradeClass = 'grade-badge';
        let gradeIcon = '⭐';
        if (hadith.grade.includes('صحيح')) {
            gradeClass += ' grade-sahih';
            gradeIcon = '✅';
        } else if (hadith.grade.includes('حسن')) {
            gradeClass += ' grade-hasan';
            gradeIcon = '👍';
        } else if (hadith.grade.includes('ضعيف')) {
            gradeClass += ' grade-daif';
            gradeIcon = '⚠️';
        } else if (hadith.grade.includes('موضوع')) {
            gradeClass += ' grade-mawdoo';
            gradeIcon = '❌';
        }

        gradeDiv.innerHTML = `
            <span class="info-icon">${gradeIcon}</span>
            <span class="info-label">الحكم:</span>
            <span class="${gradeClass}">${escapeHtml(hadith.grade)}</span>
        `;
        infoSection.appendChild(gradeDiv);
    }

    card.appendChild(infoSection);

    // === شرح الحديث ===
    const explanation = document.createElement('div');
    explanation.className = 'hadith-explanation';

    const explanationTitle = document.createElement('div');
    explanationTitle.className = 'hadith-explanation-title';
    explanationTitle.innerHTML = '📖 شرح مختصر';

    const explanationText = document.createElement('div');
    explanationText.className = 'hadith-explanation-text';

    // استخدم الشرح إذا وجد، أو أنشئ شرحاً مختصراً
    if (hadith.explanation && hadith.explanation.trim()) {
        explanationText.textContent = hadith.explanation;
    } else {
        // شرح تلقائي بسيط بناءً على نص الحديث
        explanationText.textContent = generateSimpleExplanation(hadith);
    }

    explanation.appendChild(explanationTitle);
    explanation.appendChild(explanationText);

    // === رابط الشرح الكامل من موقع الدرر ===
    if (hadith.explanation_link) {
        const linkDiv = document.createElement('div');
        linkDiv.className = 'hadith-full-explanation-link';
        linkDiv.innerHTML = `
            <a href="${escapeHtml(hadith.explanation_link)}" target="_blank" rel="noopener noreferrer" class="dorar-link">
                🔗 اقرأ الشرح الكامل على موقع الدرر السنية
            </a>
        `;
        explanation.appendChild(linkDiv);
    }

    card.appendChild(explanation);

    // === أزرار الإجراءات ===
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'hadith-actions';

    // زر المفضلة
    const favoriteBtn = document.createElement('button');
    favoriteBtn.className = `btn btn-outline favorite-btn ${isFavorite ? 'active' : ''}`;
    favoriteBtn.innerHTML = `<span class="btn-icon">${isFavorite ? '❤️' : '🤍'}</span><span class="btn-text">${isFavorite ? 'في المفضلة' : 'إضافة للمفضلة'}</span>`;
    favoriteBtn.onclick = (e) => {
        e.stopPropagation();
        toggleFavorite(hadith, favoriteBtn);
    };

    // زر النسخ
    const copyBtn = document.createElement('button');
    copyBtn.className = 'btn btn-secondary copy-btn';
    copyBtn.innerHTML = '<span class="btn-icon">📋</span><span class="btn-text">نسخ</span>';
    copyBtn.onclick = (e) => {
        e.stopPropagation();
        copyHadithText(hadith);
    };

    // زر إنشاء الفيديو
    const generateBtn = document.createElement('button');
    generateBtn.className = 'btn btn-success generate-video-btn';
    generateBtn.innerHTML = '<span class="btn-icon">🎬</span><span class="btn-text">إنشاء فيديو</span>';
    generateBtn.onclick = (e) => {
        e.stopPropagation();
        handleGenerateVideo(hadith);
    };

    actionsDiv.appendChild(favoriteBtn);
    actionsDiv.appendChild(copyBtn);
    actionsDiv.appendChild(generateBtn);
    card.appendChild(actionsDiv);

    return card;
}

/**
 * تبديل حالة المفضلة
 * Toggle favorite status
 */
function toggleFavorite(hadith, button) {
    const index = favorites.findIndex(fav => fav.text === hadith.text);

    if (index > -1) {
        favorites.splice(index, 1);
        button.classList.remove('active');
        button.innerHTML = '<span class="btn-icon">🤍</span><span class="btn-text">إضافة للمفضلة</span>';
        showToast('تم إزالة الحديث من المفضلة', 'info');
    } else {
        favorites.push({
            ...hadith,
            savedAt: new Date().toISOString()
        });
        button.classList.add('active');
        button.innerHTML = '<span class="btn-icon">❤️</span><span class="btn-text">في المفضلة</span>';
        showToast('تم إضافة الحديث للمفضلة', 'success');
    }

    localStorage.setItem('hadithFavorites', JSON.stringify(favorites));
}

/**
 * نسخ نص الحديث
 * Copy hadith text
 */
function copyHadithText(hadith) {
    const text = `${hadith.text}\n\nالراوي: ${hadith.narrator || 'غير محدد'}\nالمحدث: ${hadith.source || 'غير محدد'}\nالحكم: ${hadith.grade || 'غير محدد'}`;

    navigator.clipboard.writeText(text).then(() => {
        showToast('تم نسخ الحديث بنجاح', 'success');
    }).catch(() => {
        showToast('فشل في نسخ الحديث', 'error');
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * توليد شرح بسيط للحديث
 * Generate simple explanation for hadith
 */
function generateSimpleExplanation(hadith) {
    const text = hadith.text || '';
    const grade = hadith.grade || '';

    // تحليل بسيط للحديث
    let explanation = '';

    if (text.includes('الصدق') || text.includes('صدق')) {
        explanation = 'يحث هذا الحديث على فضيلة الصدق وأهميته في حياة المسلم، وأن الصدق يهدي إلى البر والجنة.';
    } else if (text.includes('الصلاة') || text.includes('صلاة')) {
        explanation = 'يبين هذا الحديث أهمية الصلاة ومكانتها في الإسلام كركن أساسي من أركان الدين.';
    } else if (text.includes('الزكاة') || text.includes('زكاة')) {
        explanation = 'يوضح هذا الحديث فضل الزكاة وأثرها في تطهير المال والنفس.';
    } else if (text.includes('الصوم') || text.includes('صيام')) {
        explanation = 'يبين هذا الحديث فضل الصيام وثوابه العظيم عند الله تعالى.';
    } else if (text.includes('الحج') || text.includes('حج')) {
        explanation = 'يوضح هذا الحديث فضل الحج وما فيه من مغفرة للذنوب.';
    } else if (text.includes('الكذب') || text.includes('كذب')) {
        explanation = 'يحذر هذا الحديث من الكذب وخطورته وأنه يهدي إلى الفجور والنار.';
    } else if (text.includes('الجنة') || text.includes('جنة')) {
        explanation = 'يبين هذا الحديث بعض الأعمال التي توصل إلى الجنة ورضوان الله.';
    } else if (text.includes('النار') || text.includes('نار')) {
        explanation = 'يحذر هذا الحديث من بعض الأعمال التي تؤدي إلى النار والعياذ بالله.';
    } else if (text.includes('الرحمة') || text.includes('رحم')) {
        explanation = 'يبين هذا الحديث سعة رحمة الله وأهمية التراحم بين المسلمين.';
    } else {
        // شرح عام
        if (grade.includes('صحيح')) {
            explanation = 'هذا حديث صحيح ثابت عن النبي ﷺ، يحمل معاني عظيمة وتوجيهات نبوية للمسلمين.';
        } else if (grade.includes('حسن')) {
            explanation = 'هذا حديث حسن مقبول، يحتوي على إرشادات نبوية مهمة للمسلم في حياته.';
        } else {
            explanation = 'يحتوي هذا الحديث على توجيهات وإرشادات نبوية للمسلمين في أمور دينهم ودنياهم.';
        }
    }

    return explanation;
}

// =============================================
// وظائف توليد الفيديو - Video Generation
// =============================================

/**
 * معالجة توليد الفيديو
 * Handle video generation
 */
async function handleGenerateVideo(hadith) {
    selectedHadith = hadith;

    // إخفاء النتائج وعرض قسم التقدم
    resultsSection.style.display = 'none';
    previewSection.style.display = 'none';
    progressSection.style.display = 'block';

    // التمرير إلى قسم التقدم
    progressSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // إعادة تعيين التقدم
    updateProgress(0, 'جاري بدء العملية...');
    updateStep(1, 'active');
    updateStep(2, '');
    updateStep(3, '');
    updateStep(4, '');

    try {
        // المرحلة 1: جلب البيانات
        updateProgress(10, 'جاري جلب بيانات الحديث...');
        await sleep(500);
        updateStep(1, 'completed');

        // المرحلة 2: توليد الصوت
        updateProgress(25, 'جاري توليد الملف الصوتي...');
        updateStep(2, 'active');
        await sleep(1000);

        // المرحلة 3: تحميل الفيديو
        updateProgress(40, 'جاري تحميل فيديو الخلفية...');
        updateStep(2, 'completed');
        updateStep(3, 'active');
        await sleep(1500);

        // المرحلة 4: دمج المكونات
        updateProgress(60, 'جاري دمج المكونات وإنشاء الفيديو...');
        updateStep(3, 'completed');
        updateStep(4, 'active');

        const videoType = getSelectedVideoType();
        const advancedOpts = getAdvancedOptions();

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hadith: hadith,
                video_type: videoType,
                // Voice options
                use_ai_voice: advancedOpts.use_ai_voice,
                voice: advancedOpts.voice,
                enhance_audio: advancedOpts.enhance_audio,
                // Image options
                use_ai_background: advancedOpts.use_ai_background,
                image_provider: advancedOpts.image_provider,
                // Video options
                use_ai_video: advancedOpts.use_ai_video,
                use_local_video: advancedOpts.use_local_video,
                use_multiple_images: advancedOpts.use_multiple_images,
                video_provider: advancedOpts.video_provider,
                image_count: advancedOpts.image_count,
                image_duration: advancedOpts.image_duration,
                // Enhancement options
                enhance_locally: advancedOpts.enhance_locally,
                ken_burns: advancedOpts.ken_burns,
                vignette: advancedOpts.vignette,
                film_grain: advancedOpts.film_grain,
                // Prompt options
                custom_prompt: advancedOpts.custom_prompt,
                prompt_provider: advancedOpts.prompt_provider
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'حدث خطأ في إنشاء الفيديو');
        }

        // اكتمال العملية - تحديث فوري
        updateStep(4, 'completed');
        updateProgress(100, '✅ تم إنشاء الفيديو بنجاح!');

        // عرض رسالة نجاح للمستخدم
        progressText.style.color = '#28a745';
        progressText.style.fontWeight = 'bold';

        await sleep(1500);

        // عرض الفيديو
        showVideoPreview(data.video_path);

    } catch (error) {
        console.error('خطأ في توليد الفيديو:', error);
        showError(`خطأ في توليد الفيديو: ${error.message}`);
        progressSection.style.display = 'none';
    }
}

/**
 * عرض معاينة الفيديو
 * Show video preview
 */
function showVideoPreview(videoPath) {
    currentVideoPath = videoPath;

    // إخفاء قسم التقدم وعرض قسم المعاينة
    progressSection.style.display = 'none';
    previewSection.style.display = 'block';

    // تحميل الفيديو
    videoPreview.src = `/api/preview/${videoPath}`;
    videoPreview.load();

    // تحديث معلومات الفيديو عند تحميل البيانات الوصفية
    videoPreview.onloadedmetadata = () => {
        if (videoDuration) {
            const duration = Math.round(videoPreview.duration);
            const minutes = Math.floor(duration / 60);
            const seconds = duration % 60;
            videoDuration.textContent = minutes > 0
                ? `${minutes}:${seconds.toString().padStart(2, '0')}`
                : `${seconds} ثانية`;
        }
    };

    // التمرير إلى المعاينة
    previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    showToast('تم إنشاء الفيديو بنجاح! 🎉', 'success');
}

// =============================================
// وظائف الفيديو - Video Functions
// =============================================

/**
 * معالجة تحميل الفيديو
 * Handle video download
 */
function handleDownload() {
    if (!currentVideoPath) {
        showError('لا يوجد فيديو للتحميل');
        return;
    }

    window.location.href = `/api/download/${currentVideoPath}`;
}

/**
 * معالجة إنشاء فيديو جديد
 * Handle new video creation
 */
function handleNewVideo() {
    // إعادة تعيين الحالة
    selectedHadith = null;
    currentVideoPath = null;
    searchInput.value = '';

    // إخفاء جميع الأقسام
    resultsSection.style.display = 'none';
    progressSection.style.display = 'none';
    previewSection.style.display = 'none';

    // التمرير إلى الأعلى
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // التركيز على حقل البحث
    searchInput.focus();
}

// =============================================
// وظائف مساعدة إضافية - Additional Helper Functions
// =============================================

/**
 * وظيفة النوم (للتأخير)
 * Sleep function for delay
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * تنسيق النص العربي
 * Format Arabic text
 */
function formatArabicText(text) {
    if (!text) return '';

    // إزالة المسافات الزائدة
    text = text.trim().replace(/\s+/g, ' ');

    // إضافة علامات الترقيم إذا لم تكن موجودة
    if (!text.endsWith('.') && !text.endsWith('؟') && !text.endsWith('!')) {
        text += '.';
    }

    return text;
}

/**
 * التحقق من دعم الفيديو
 * Check video support
 */
function checkVideoSupport() {
    const video = document.createElement('video');
    const canPlayMP4 = video.canPlayType('video/mp4');

    if (!canPlayMP4) {
        showError('متصفحك لا يدعم تشغيل فيديوهات MP4');
        return false;
    }

    return true;
}

// =============================================
// التهيئة - Initialization
// =============================================

/**
 * تهيئة التطبيق
 * Initialize application
 */
function initApp() {
    console.log('تطبيق مولد فيديوهات الأحاديث النبوية');
    console.log('Hadith Video Generator Application');

    // التحقق من دعم الفيديو
    checkVideoSupport();

    // التركيز على حقل البحث
    searchInput.focus();

    // تحديث حالة الوضع الليلي
    const isNightMode = localStorage.getItem('nightMode') === 'true';
    if (isNightMode && nightModeToggle) {
        const iconSpan = nightModeToggle.querySelector('.icon');
        if (iconSpan) iconSpan.textContent = '☀️';
    }

    // جلب عدد الفيديوهات المنشأة
    fetchVideoStats();

    // تحديث حالة خدمات AI
    updateAIStatusCount();

    // تهيئة مراقبة الشبكة
    initNetworkMonitor();

    // تهيئة المفضلة
    initFavorites();

    // تهيئة سجل البحث
    initSearchHistory();

    // إضافة مستمع لتغيير حجم النافذة
    window.addEventListener('resize', debounce(() => {
        // تحديث التخطيط إذا لزم الأمر
    }, 250));

    console.log('✅ تم تهيئة التطبيق بنجاح');
}

/**
 * مراقبة حالة الشبكة
 * Network status monitor
 */
function initNetworkMonitor() {
    const networkStatus = document.getElementById('networkStatus');

    if (!networkStatus) return;

    function updateNetworkStatus() {
        if (!navigator.onLine) {
            networkStatus.classList.add('visible');
            showToast('انقطع الاتصال بالإنترنت', 'error');
        } else {
            networkStatus.classList.remove('visible');
        }
    }

    window.addEventListener('online', () => {
        networkStatus.classList.remove('visible');
        showToast('تم استعادة الاتصال بالإنترنت', 'success');
    });

    window.addEventListener('offline', () => {
        networkStatus.classList.add('visible');
        showToast('انقطع الاتصال بالإنترنت', 'error');
    });

    // Initial check
    updateNetworkStatus();
}

/**
 * تهيئة المفضلة
 * Initialize favorites
 */
function initFavorites() {
    const favoritesBtn = document.getElementById('favoritesBtn');
    const showFavoritesBtn = document.getElementById('showFavoritesBtn');
    const favoritesModal = document.getElementById('favoritesModal');
    const closeFavoritesModal = document.getElementById('closeFavoritesModal');

    if (favoritesBtn) {
        favoritesBtn.addEventListener('click', showFavoritesModal);
    }

    if (showFavoritesBtn) {
        showFavoritesBtn.addEventListener('click', showFavoritesModal);
    }

    if (closeFavoritesModal) {
        closeFavoritesModal.addEventListener('click', () => {
            if (favoritesModal) favoritesModal.style.display = 'none';
        });
    }

    if (favoritesModal) {
        favoritesModal.querySelector('.modal-overlay')?.addEventListener('click', () => {
            favoritesModal.style.display = 'none';
        });
    }
}

/**
 * عرض نافذة المفضلة
 * Show favorites modal
 */
function showFavoritesModal() {
    const favoritesModal = document.getElementById('favoritesModal');
    const favoritesList = document.getElementById('favoritesList');

    if (!favoritesModal || !favoritesList) return;

    if (favorites.length === 0) {
        favoritesList.innerHTML = '<p class="empty-favorites">لا توجد أحاديث مفضلة بعد. اضغط على ❤️ لإضافة أحاديث.</p>';
    } else {
        favoritesList.innerHTML = favorites.map((hadith, index) => `
            <div class="favorite-item">
                <div class="favorite-text">${escapeHtml(hadith.text?.substring(0, 150) || '')}...</div>
                <div class="favorite-meta">
                    <span>📜 ${escapeHtml(hadith.narrator) || 'غير محدد'}</span>
                    <span>📅 ${new Date(hadith.savedAt).toLocaleDateString('ar-SA')}</span>
                </div>
                <div class="favorite-actions">
                    <button class="btn btn-small btn-success" onclick="generateVideoFromFavorite(${index})">
                        🎬 إنشاء فيديو
                    </button>
                    <button class="btn btn-small btn-danger" onclick="removeFavorite(${index})">
                        🗑️ حذف
                    </button>
                </div>
            </div>
        `).join('');
    }

    favoritesModal.style.display = 'flex';
}

/**
 * توليد فيديو من المفضلة
 * Generate video from favorite
 */
function generateVideoFromFavorite(index) {
    const hadith = favorites[index];
    if (hadith) {
        const favoritesModal = document.getElementById('favoritesModal');
        if (favoritesModal) favoritesModal.style.display = 'none';
        handleGenerateVideo(hadith);
    }
}

/**
 * إزالة من المفضلة
 * Remove from favorites
 */
function removeFavorite(index) {
    favorites.splice(index, 1);
    localStorage.setItem('hadithFavorites', JSON.stringify(favorites));
    showFavoritesModal(); // Refresh the list
    showToast('تم حذف الحديث من المفضلة', 'info');
}

/**
 * تهيئة سجل البحث
 * Initialize search history
 */
function initSearchHistory() {
    if (searchInput) {
        searchInput.addEventListener('focus', () => {
            if (searchHistory.length > 0 && searchInput.value === '') {
                showSearchHistory();
            }
        });

        searchInput.addEventListener('blur', () => {
            // Delay to allow clicking on history items
            setTimeout(hideSearchHistory, 200);
        });
    }
}

/**
 * تصدير البيانات
 * Export data
 */
function exportData() {
    const data = {
        favorites: favorites,
        searchHistory: searchHistory,
        generationHistory: generationHistory,
        exportDate: new Date().toISOString()
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hadith-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('تم تصدير البيانات بنجاح', 'success');
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// تهيئة زر تصدير البيانات
const exportDataBtn = document.getElementById('exportDataBtn');
if (exportDataBtn) {
    exportDataBtn.addEventListener('click', exportData);
}

/**
 * جلب إحصائيات الفيديو
 * Fetch video statistics
 */
async function fetchVideoStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        if (data.success) {
            const totalVideos = document.getElementById('totalVideos');
            if (totalVideos) {
                totalVideos.textContent = data.total_videos || 0;
            }
        }
    } catch (error) {
        console.log('لم يتم تحميل إحصائيات الفيديو');
    }
}

/**
 * تحديث عدد خدمات AI
 * Update AI services count
 */
async function updateAIStatusCount() {
    try {
        const response = await fetch('/api/ai_status');
        const data = await response.json();
        if (data.success && data.status) {
            let activeCount = 0;
            Object.values(data.status).forEach(status => {
                if (status) activeCount++;
            });
            const aiStatusCount = document.getElementById('aiStatusCount');
            if (aiStatusCount) {
                aiStatusCount.textContent = activeCount;
            }
        }
    } catch (error) {
        console.log('لم يتم تحميل حالة AI');
    }
}

// تشغيل التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', initApp);

// =============================================
// Scroll to Top Button
// =============================================
const scrollTopBtn = document.getElementById('scrollTopBtn');

if (scrollTopBtn) {
    // إظهار/إخفاء الزر حسب موضع التمرير
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            scrollTopBtn.classList.add('visible');
            scrollTopBtn.style.display = 'flex';
        } else {
            scrollTopBtn.classList.remove('visible');
            setTimeout(() => {
                if (!scrollTopBtn.classList.contains('visible')) {
                    scrollTopBtn.style.display = 'none';
                }
            }, 300);
        }
    });

    // التمرير للأعلى عند النقر
    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// =============================================
// معالجة الأخطاء العامة - Global Error Handling
// =============================================

window.addEventListener('error', (event) => {
    console.error('خطأ في التطبيق:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('وعد غير معالج:', event.reason);
});
