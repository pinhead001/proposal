const API = '';
let uploadedProposals = false;
let generatedSections = [];

// --- DOM refs ---
const fileInput = document.getElementById('file-input');
const uploadZone = document.getElementById('upload-zone');
const browseLink = document.getElementById('browse-link');
const fileList = document.getElementById('file-list');
const uploadStatus = document.getElementById('upload-status');
const rfpInput = document.getElementById('rfp-input');
const rfpCharCount = document.getElementById('rfp-char-count');
const btnGenerate = document.getElementById('btn-generate');
const btnExport = document.getElementById('btn-export');
const stepResults = document.getElementById('step-results');
const progressBar = document.getElementById('progress-bar');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const sectionsContainer = document.getElementById('sections-container');
const regenModal = document.getElementById('regen-modal');
const regenSectionName = document.getElementById('regen-section-name');
const regenInstructions = document.getElementById('regen-instructions');
const regenCancel = document.getElementById('regen-cancel');
const regenSubmit = document.getElementById('regen-submit');

let pendingFiles = [];
let regenTarget = null;

// --- Toast ---
function showToast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// --- File upload ---
browseLink.addEventListener('click', e => {
    e.preventDefault();
    fileInput.click();
});

uploadZone.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', e => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', e => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    addFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', () => {
    addFiles(fileInput.files);
    fileInput.value = '';
});

function addFiles(files) {
    for (const f of files) {
        const ext = f.name.split('.').pop().toLowerCase();
        if (ext !== 'pdf' && ext !== 'docx') {
            showToast(`${f.name}: Only PDF and DOCX are supported`, 'error');
            continue;
        }
        if (f.size > 10 * 1024 * 1024) {
            showToast(`${f.name}: File exceeds 10MB limit`, 'error');
            continue;
        }
        if (!pendingFiles.find(pf => pf.name === f.name)) {
            pendingFiles.push(f);
        }
    }
    renderFileList();
    if (pendingFiles.length > 0) uploadFiles();
}

function renderFileList() {
    fileList.innerHTML = pendingFiles.map((f, i) => {
        const ext = f.name.split('.').pop().toUpperCase();
        const size = (f.size / 1024).toFixed(0) + ' KB';
        return `<div class="file-item">
            <span class="file-name">
                <span class="file-ext">${ext}</span>
                ${f.name}
            </span>
            <span class="file-size">${size}</span>
            <button class="file-remove" data-idx="${i}">&times;</button>
        </div>`;
    }).join('');

    fileList.querySelectorAll('.file-remove').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            pendingFiles.splice(parseInt(btn.dataset.idx), 1);
            renderFileList();
            if (pendingFiles.length === 0) {
                uploadedProposals = false;
                uploadStatus.textContent = '';
                uploadStatus.className = 'status-msg';
            }
            updateGenerateBtn();
        });
    });

    updateGenerateBtn();
}

async function uploadFiles() {
    const formData = new FormData();
    pendingFiles.forEach(f => formData.append('files', f));

    uploadStatus.textContent = 'Uploading and extracting text...';
    uploadStatus.className = 'status-msg';

    try {
        const res = await fetch(`${API}/upload-proposals`, {
            method: 'POST',
            body: formData,
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Upload failed');
        }

        const data = await res.json();
        uploadedProposals = true;
        uploadStatus.textContent = `${data.file_count} proposal(s) analyzed successfully.`;
        uploadStatus.className = 'status-msg success';
        updateGenerateBtn();
    } catch (err) {
        uploadStatus.textContent = err.message;
        uploadStatus.className = 'status-msg error';
    }
}

// --- RFP input ---
rfpInput.addEventListener('input', () => {
    const len = rfpInput.value.length;
    rfpCharCount.textContent = `${len.toLocaleString()} characters`;
    updateGenerateBtn();
});

function updateGenerateBtn() {
    btnGenerate.disabled = !(uploadedProposals && rfpInput.value.trim().length > 20);
}

// --- Generate proposal ---
btnGenerate.addEventListener('click', generateProposal);

async function generateProposal() {
    btnGenerate.disabled = true;
    btnGenerate.innerHTML = '<span class="spinner"></span>Generating...';
    stepResults.classList.remove('hidden');
    progressBar.classList.remove('hidden');
    sectionsContainer.innerHTML = '';
    generatedSections = [];
    btnExport.disabled = true;

    try {
        const res = await fetch(`${API}/stream-pipeline`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rfp_text: rfpInput.value }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Generation failed');
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                const raw = line.slice(6).trim();
                if (!raw || raw === '[DONE]') continue;

                try {
                    const event = JSON.parse(raw);
                    handleStreamEvent(event);
                } catch {}
            }
        }

        // Process remaining buffer
        if (buffer.startsWith('data: ')) {
            const raw = buffer.slice(6).trim();
            if (raw && raw !== '[DONE]') {
                try { handleStreamEvent(JSON.parse(raw)); } catch {}
            }
        }

        progressBar.classList.add('hidden');
        btnExport.disabled = false;
        showToast('Proposal generated successfully!', 'success');
    } catch (err) {
        showToast(err.message, 'error');
        progressBar.classList.add('hidden');
    } finally {
        btnGenerate.disabled = false;
        btnGenerate.textContent = 'Generate Proposal';
        updateGenerateBtn();
    }
}

function handleStreamEvent(event) {
    switch (event.type) {
        case 'progress':
            progressFill.style.width = event.percent + '%';
            progressText.textContent = event.message;
            break;

        case 'section':
            const section = event.data;
            generatedSections.push(section);
            appendSectionCard(section, generatedSections.length - 1);
            break;

        case 'error':
            showToast(event.message, 'error');
            break;

        case 'done':
            progressFill.style.width = '100%';
            progressText.textContent = 'Complete!';
            break;
    }
}

function appendSectionCard(section, index) {
    const card = document.createElement('div');
    card.className = 'section-card';
    card.dataset.index = index;
    card.innerHTML = `
        <div class="section-card-header">
            <h3>${section.title}</h3>
            <div class="section-card-actions">
                <button class="btn-icon regen-btn" title="Regenerate with instructions">&#x21bb;</button>
                <span class="collapse-icon">&#9660;</span>
            </div>
        </div>
        <div class="section-card-body">
            <p>${escapeHtml(section.content)}</p>
        </div>
    `;

    card.querySelector('.section-card-header').addEventListener('click', e => {
        if (e.target.closest('.regen-btn')) return;
        card.classList.toggle('collapsed');
    });

    card.querySelector('.regen-btn').addEventListener('click', () => {
        regenTarget = index;
        regenSectionName.textContent = `Refining: "${section.title}"`;
        regenInstructions.value = '';
        regenModal.classList.remove('hidden');
        regenInstructions.focus();
    });

    sectionsContainer.appendChild(card);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// --- Regenerate section ---
regenCancel.addEventListener('click', () => {
    regenModal.classList.add('hidden');
});

regenModal.querySelector('.modal-backdrop').addEventListener('click', () => {
    regenModal.classList.add('hidden');
});

regenSubmit.addEventListener('click', async () => {
    if (regenTarget === null) return;

    const section = generatedSections[regenTarget];
    const instructions = regenInstructions.value.trim();
    regenModal.classList.add('hidden');

    const card = sectionsContainer.querySelector(`[data-index="${regenTarget}"]`);
    const bodyP = card.querySelector('.section-card-body p');
    card.classList.add('generating');
    bodyP.textContent = 'Regenerating...';

    try {
        const res = await fetch(`${API}/regenerate-section`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                section_title: section.title,
                rfp_text: rfpInput.value,
                instructions: instructions,
                current_content: section.content,
            }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Regeneration failed');
        }

        const data = await res.json();
        generatedSections[regenTarget] = data;
        bodyP.textContent = data.content;
        card.classList.remove('generating');
        showToast(`"${section.title}" regenerated`, 'success');
    } catch (err) {
        bodyP.textContent = section.content;
        card.classList.remove('generating');
        showToast(err.message, 'error');
    }
});

// --- Export ---
btnExport.addEventListener('click', async () => {
    if (generatedSections.length === 0) return;

    btnExport.disabled = true;
    btnExport.innerHTML = '<span class="spinner"></span>Exporting...';

    try {
        const res = await fetch(`${API}/export`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sections: generatedSections }),
        });

        if (!res.ok) throw new Error('Export failed');

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'proposal.docx';
        a.click();
        URL.revokeObjectURL(url);
        showToast('Proposal exported!', 'success');
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        btnExport.disabled = false;
        btnExport.textContent = 'Export .docx';
    }
});
