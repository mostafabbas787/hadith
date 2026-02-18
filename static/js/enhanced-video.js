/**
 * Enhanced Video Generation with Async Support and KIE API
 * تحسينات توليد الفيديو مع الدعم غير المتزامن و KIE API
 */

// =============================================
// Async Video Generation Variables
// =============================================
let currentJobId = null;
let progressCheckInterval = null;
let asyncModeEnabled = false;
let kieModeEnabled = false;

// =============================================
// Enhanced UI Elements
// =============================================
function addEnhancedControls() {
    // Add async mode toggle
    const advancedOptions = document.getElementById('advancedOptions');

    if (advancedOptions) {
        const asyncControlsHTML = `
            <div class="advanced-option">
                <label class="option-label">
                    <input type="checkbox" id="asyncModeToggle" ${asyncModeEnabled ? 'checked' : ''}>
                    <span class="option-text">الوضع غير المتزامن</span>
                    <span class="option-description">توليد فيديو مع تتبع التقدم</span>
                </label>
            </div>
            
            <div class="advanced-option">
                <label class="option-label">
                    <input type="checkbox" id="kieModeToggle" ${kieModeEnabled ? 'checked' : ''}>
                    <span class="option-text">وضع KIE AI</span>
                    <span class="option-description">توليد فيديو متقدم بالذكاء الاصطناعي</span>
                </label>
            </div>
            
            <div class="advanced-option" id="progressControls" style="display: none;">
                <button id="cancelJobBtn" class="btn btn-secondary">
                    <span class="btn-icon">⏹️</span>
                    <span class="btn-text">إلغاء التوليد</span>
                </button>
            </div>
        `;

        advancedOptions.insertAdjacentHTML('beforeend', asyncControlsHTML);

        // Setup event listeners
        setupAsyncControls();
    }
}

function setupAsyncControls() {
    const asyncModeToggle = document.getElementById('asyncModeToggle');
    const kieModeToggle = document.getElementById('kieModeToggle');
    const cancelJobBtn = document.getElementById('cancelJobBtn');

    if (asyncModeToggle) {
        asyncModeToggle.addEventListener('change', (e) => {
            asyncModeEnabled = e.target.checked;
            if (asyncModeEnabled) {
                kieModeEnabled = false;
                if (kieModeToggle) kieModeToggle.checked = false;
            }
            showToast(
                asyncModeEnabled ? 'تم تفعيل الوضع غير المتزامن' : 'تم إيقاف الوضع غير المتزامن',
                'info'
            );
        });
    }

    if (kieModeToggle) {
        kieModeToggle.addEventListener('change', (e) => {
            kieModeEnabled = e.target.checked;
            if (kieModeEnabled) {
                asyncModeEnabled = false;
                if (asyncModeToggle) asyncModeToggle.checked = false;
            }
            showToast(
                kieModeEnabled ? 'تم تفعيل وضع KIE AI' : 'تم إيقاف وضع KIE AI',
                kieModeEnabled ? 'success' : 'info'
            );
        });
    }

    if (cancelJobBtn) {
        cancelJobBtn.addEventListener('click', cancelCurrentJob);
    }
}

// =============================================
// Enhanced Video Generation Functions
// =============================================

/**
 * Enhanced video generation with multiple modes
 */
async function enhancedHandleGenerateVideo(hadith) {
    try {
        if (!hadith || !hadith.text) {
            showToast('الرجاء اختيار حديث للتوليد', 'error');
            return;
        }

        selectedHadith = hadith;
        hideSection(document.getElementById('resultsSection'));

        // Choose generation mode
        if (asyncModeEnabled) {
            await handleAsyncVideoGeneration(hadith);
        } else if (kieModeEnabled) {
            await handleKieVideoGeneration(hadith);
        } else {
            showLoadingOverlay('جاري توليد الفيديو...');
            await handleSyncVideoGeneration(hadith);
        }

    } catch (error) {
        console.error('Video generation error:', error);
        hideLoadingOverlay();
        hideProgressSection();
        showError('حدث خطأ غير متوقع، الرجاء المحاولة مرة أخرى');
    }
}

/**
 * Async video generation with progress tracking
 */
async function handleAsyncVideoGeneration(hadith) {
    try {
        const data = {
            hadith: hadith,
            video_type: getSelectedVideoType(),
            use_ai_voice: document.getElementById('useAIVoice')?.checked || true,
            use_ai_background: document.getElementById('useAIBackground')?.checked || false,
            enhance_locally: document.getElementById('enhanceLocally')?.checked || true,
            custom_prompt: document.getElementById('customPrompt')?.value || ''
        };

        showLoadingOverlay('بدء التوليد غير المتزامن...');

        const response = await fetch('/api/generate_async', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        hideLoadingOverlay();

        if (!response.ok) {
            throw new Error(result.error || 'حدث خطأ في بدء توليد الفيديو');
        }

        if (result.success && result.job_id) {
            currentJobId = result.job_id;
            showProgressSection();
            startProgressTracking();
            showToast('تم بدء توليد الفيديو بنجاح', 'success');
        } else {
            throw new Error(result.error || 'فشل في بدء توليد الفيديو');
        }

    } catch (error) {
        hideLoadingOverlay();
        showError(`خطأ في التوليد غير المتزامن: ${error.message}`);
    }
}

/**
 * KIE AI video generation
 */
async function handleKieVideoGeneration(hadith) {
    try {
        const prompt = generateVideoPrompt(hadith.text);

        const data = {
            prompt: prompt,
            duration: 6
        };

        showProgressSection();
        updateProgress(10, 'بدء توليد فيديو KIE AI...');

        const response = await fetch('/api/generate_kie_video', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'حدث خطأ في توليد فيديو KIE');
        }

        if (result.success && result.video_url) {
            updateProgress(100, 'تم توليد الفيديو بنجاح!');

            // Display video
            const videoPreview = document.getElementById('videoPreview');
            videoPreview.src = result.video_url;
            videoPreview.load();

            hideProgressSection();
            showPreviewSection();

            // Update download button
            const downloadBtn = document.getElementById('downloadBtn');
            downloadBtn.onclick = () => {
                const a = document.createElement('a');
                a.href = result.video_url;
                a.download = `kie_hadith_video_${Date.now()}.mp4`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            };

            showToast('تم توليد فيديو KIE بنجاح!', 'success');
        } else {
            throw new Error(result.error || 'فشل في توليد فيديو KIE');
        }

    } catch (error) {
        hideProgressSection();
        showError(`خطأ KIE: ${error.message}`);
    }
}

/**
 * Traditional sync video generation
 */
async function handleSyncVideoGeneration(hadith) {
    try {
        const data = {
            hadith: hadith,
            video_type: getSelectedVideoType(),
            use_ai_voice: document.getElementById('useAIVoice')?.checked || true,
            use_ai_background: document.getElementById('useAIBackground')?.checked || false,
            enhance_locally: document.getElementById('enhanceLocally')?.checked || true,
            custom_prompt: document.getElementById('customPrompt')?.value || ''
        };

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        hideLoadingOverlay();

        if (!response.ok) {
            throw new Error(result.error || 'حدث خطأ في توليد الفيديو');
        }

        if (result.success && result.video_path) {
            currentVideoPath = result.video_path;
            const videoPreview = document.getElementById('videoPreview');
            videoPreview.src = `/api/preview/${result.video_path}`;
            videoPreview.load();
            showPreviewSection();
            showToast('تم إنشاء الفيديو بنجاح', 'success');

            // Save to history
            if (typeof addToGenerationHistory === 'function') {
                addToGenerationHistory(hadith, result.video_path);
            }
        } else {
            throw new Error(result.error || 'فشل في إنشاء الفيديو');
        }

    } catch (error) {
        showError(`خطأ في التوليد: ${error.message}`);
    }
}

// =============================================
// Progress Tracking Functions
// =============================================

/**
 * Start tracking async job progress
 */
function startProgressTracking() {
    if (!currentJobId) return;

    updateProgress(5, 'بدء تتبع التقدم...');
    document.getElementById('progressControls').style.display = 'block';

    progressCheckInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/job_status/${currentJobId}`);
            const result = await response.json();

            if (result.success && result.status) {
                const status = result.status;

                updateProgress(status.progress, status.message);

                if (status.status === 'completed') {
                    clearInterval(progressCheckInterval);
                    progressCheckInterval = null;

                    if (status.result) {
                        currentVideoPath = status.result;
                        const videoPreview = document.getElementById('videoPreview');
                        videoPreview.src = `/api/preview/${status.result}`;
                        videoPreview.load();
                        hideProgressSection();
                        showPreviewSection();
                        showToast('تم إنشاء الفيديو بنجاح!', 'success');

                        // Save to history
                        if (typeof addToGenerationHistory === 'function' && selectedHadith) {
                            addToGenerationHistory(selectedHadith, status.result);
                        }
                    }
                } else if (status.status === 'failed') {
                    clearInterval(progressCheckInterval);
                    progressCheckInterval = null;
                    hideProgressSection();
                    showError(`فشل التوليد: ${status.message}`);
                } else if (status.status === 'cancelled') {
                    clearInterval(progressCheckInterval);
                    progressCheckInterval = null;
                    hideProgressSection();
                    showToast('تم إلغاء توليد الفيديو', 'info');
                }
            }
        } catch (error) {
            console.error('خطأ في تتبع التقدم:', error);
        }
    }, 2000); // Update every 2 seconds
}

/**
 * Cancel current generation job
 */
async function cancelCurrentJob() {
    if (!currentJobId) return;

    try {
        const response = await fetch(`/api/cancel_job/${currentJobId}`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            if (progressCheckInterval) {
                clearInterval(progressCheckInterval);
                progressCheckInterval = null;
            }

            currentJobId = null;
            hideProgressSection();
            showToast('تم إلغاء توليد الفيديو', 'info');
        } else {
            showToast('فشل في إلغاء المهمة', 'error');
        }
    } catch (error) {
        console.error('خطأ في إلغاء المهمة:', error);
        showToast('خطأ في إلغاء المهمة', 'error');
    }
}

// =============================================
// Utility Functions
// =============================================

/**
 * Generate video prompt from hadith text
 */
function generateVideoPrompt(hadithText) {
    const islamicPrompts = [
        'منظر طبيعي هادئ مع ضوء ذهبي ناعم، أجواء روحانية',
        'مسجد جميل في الغروب، إضاءة دافئة، سكينة وهدوء',
        'حديقة خضراء جميلة مع نافورة، أجواء هادئة',
        'شمس مشرقة عبر الغيوم، أضواء ذهبية لطيفة',
        'بحر هادئ عند الفجر، أمواج ناعمة، سلام داخلي'
    ];

    const selectedPrompt = islamicPrompts[Math.floor(Math.random() * islamicPrompts.length)];
    return `${selectedPrompt}, HD جودة عالية, حركة لطيفة, 6 ثوان`;
}

/**
 * Get selected video type
 */
function getSelectedVideoType() {
    const videoTypeSelect = document.querySelector('select[name="video_type"]');
    return videoTypeSelect ? videoTypeSelect.value : null;
}

/**
 * Show progress section
 */
function showProgressSection() {
    const progressSection = document.getElementById('progressSection');
    if (progressSection) {
        progressSection.style.display = 'block';
    }
}

/**
 * Hide progress section
 */
function hideProgressSection() {
    const progressSection = document.getElementById('progressSection');
    const progressControls = document.getElementById('progressControls');

    if (progressSection) {
        progressSection.style.display = 'none';
    }

    if (progressControls) {
        progressControls.style.display = 'none';
    }
}

/**
 * Update progress bar and text
 */
function updateProgress(progress, message) {
    const progressBarFill = document.getElementById('progressBarFill');
    const progressText = document.getElementById('progressText');

    if (progressBarFill) {
        progressBarFill.style.width = `${progress}%`;
    }

    if (progressText) {
        progressText.textContent = message || `${progress}%`;
    }
}

/**
 * Show preview section
 */
function showPreviewSection() {
    const previewSection = document.getElementById('previewSection');
    if (previewSection) {
        previewSection.style.display = 'block';
    }
}

/**
 * Show loading overlay with custom message
 */
function showLoadingOverlay(message = 'جاري المعالجة...') {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');

    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }

    if (loadingText) {
        loadingText.textContent = message;
    }
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

// =============================================
// Initialize Enhanced Features
// =============================================

// Replace the original handleGenerateVideo function
if (typeof window !== 'undefined') {
    window.originalHandleGenerateVideo = typeof handleGenerateVideo !== 'undefined' ? handleGenerateVideo : null;
    window.handleGenerateVideo = enhancedHandleGenerateVideo;

    // Initialize enhanced controls when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addEnhancedControls);
    } else {
        addEnhancedControls();
    }
}