const API = '';
let uploadedProposals = false;
let generatedSections = [];
let selectedSections = [];

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
const btnExpandAll = document.getElementById('btn-expand-all');
const btnCollapseAll = document.getElementById('btn-collapse-all');
const btnSave = document.getElementById('btn-save');
const btnHistory = document.getElementById('btn-history');
const historyPanel = document.getElementById('history-panel');
const historyList = document.getElementById('history-list');
const historyClose = document.getElementById('history-close');
const sectionCheckboxes = document.getElementById('section-checkboxes');
const btnSelectAll = document.getElementById('btn-select-all');
const btnDeselectAll = document.getElementById('btn-deselect-all');

let pendingFiles = [];
let regenTarget = null;

// --- Utilities ---
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function wordCount(text) {
    return text.trim().split(/\s+/).filter(w => w.length > 0).length;
}

// --- Toast ---
function showToast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// --- Section selector ---
async function loadSections() {
    try {
        const res = await fetch(`${API}/available-sections`);
        const data = await res.json();
        selectedSections = [...data.sections];
        renderSectionCheckboxes(data.sections);
    } catch {
        const defaults = ['Executive Summary', 'Technical Approach', 'Staffing Plan', 'Past Performance', 'Cost Narrative'];
        selectedSections = [...defaults];
        renderSectionCheckboxes(defaults);
    }
}

function renderSectionCheckboxes(sections) {
    sectionCheckboxes.innerHTML = '';
    sections.forEach(name => {
        const label = document.createElement('label');
        label.className = 'section-checkbox-label checked';

        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = true;
        cb.value = name;

        cb.addEventListener('change', () => {
            if (cb.checked) {
                if (!selectedSections.includes(name)) selectedSections.push(name);
                label.classList.add('checked');
            } else {
                selectedSections = selectedSections.filter(s => s !== name);
                label.classList.remove('checked');
            }
            updateGenerateBtn();
        });

        label.appendChild(cb);
        label.appendChild(document.createTextNode(name));
        sectionCheckboxes.appendChild(label);
    });
}

btnSelectAll.addEventListener('click', () => {
    sectionCheckboxes.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.checked = true;
        cb.dispatchEvent(new Event('change'));
    });
});

btnDeselectAll.addEventListener('click', () => {
    sectionCheckboxes.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
        cb.dispatchEvent(new Event('change'));
    });
});

loadSections();

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
    fileList.innerHTML = '';
    pendingFiles.forEach((f, i) => {
        const ext = f.name.split('.').pop().toUpperCase();
        const size = (f.size / 1024).toFixed(0) + ' KB';

        const item = document.createElement('div');
        item.className = 'file-item';

        const nameSpan = document.createElement('span');
        nameSpan.className = 'file-name';

        const extBadge = document.createElement('span');
        extBadge.className = 'file-ext';
        extBadge.textContent = ext;

        const nameText = document.createTextNode(' ' + f.name);
        nameSpan.appendChild(extBadge);
        nameSpan.appendChild(nameText);

        const sizeSpan = document.createElement('span');
        sizeSpan.className = 'file-size';
        sizeSpan.textContent = size;

        const removeBtn = document.createElement('button');
        removeBtn.className = 'file-remove';
        removeBtn.innerHTML = '&times;';
        removeBtn.addEventListener('click', e => {
            e.stopPropagation();
            pendingFiles.splice(i, 1);
            renderFileList();
            if (pendingFiles.length === 0) {
                uploadedProposals = false;
                uploadStatus.textContent = '';
                uploadStatus.className = 'status-msg';
            }
            updateGenerateBtn();
        });

        item.appendChild(nameSpan);
        item.appendChild(sizeSpan);
        item.appendChild(removeBtn);
        fileList.appendChild(item);
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
            let msg = 'Upload failed';
            try { msg = (await res.json()).detail || msg; } catch {}
            throw new Error(msg);
        }

        const data = await res.json();
        uploadedProposals = true;
        uploadStatus.textContent = `${data.file_count} proposal(s) analyzed successfully.`;
        uploadStatus.className = 'status-msg success';
        updateGenerateBtn();
    } catch (err) {
        const msg = err.name === 'TypeError' ? 'Network error — is the server running?' : err.message;
        uploadStatus.textContent = msg;
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
    btnGenerate.disabled = !(uploadedProposals && rfpInput.value.trim().length > 20 && selectedSections.length > 0);
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
            body: JSON.stringify({
                rfp_text: rfpInput.value,
                sections: selectedSections,
            }),
        });

        if (!res.ok) {
            let msg = 'Generation failed';
            try { msg = (await res.json()).detail || msg; } catch {}
            throw new Error(msg);
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
                try { handleStreamEvent(JSON.parse(raw)); } catch {}
            }
        }

        if (buffer.startsWith('data: ')) {
            const raw = buffer.slice(6).trim();
            if (raw && raw !== '[DONE]') {
                try { handleStreamEvent(JSON.parse(raw)); } catch {}
            }
        }

        progressBar.classList.add('hidden');
        btnExport.disabled = false;
        btnSave.disabled = false;
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
            generatedSections.push(event.data);
            appendSectionCard(event.data, generatedSections.length - 1);
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

    const words = wordCount(section.content);

    card.innerHTML = `
        <div class="section-card-header">
            <h3>${escapeHtml(section.title)}</h3>
            <div class="section-card-actions">
                <button class="btn-icon copy-btn" title="Copy to clipboard">&#128203;</button>
                <button class="btn-icon edit-btn" title="Edit section">&#9998;</button>
                <button class="btn-icon regen-btn" title="Regenerate with instructions">&#x21bb;</button>
                <span class="collapse-icon">&#9660;</span>
            </div>
        </div>
        <div class="section-card-body">
            <p>${escapeHtml(section.content)}</p>
        </div>
        <div class="edit-actions hidden">
            <button class="btn btn-sm btn-primary save-edit-btn">Save</button>
            <button class="btn btn-sm btn-outline cancel-edit-btn">Cancel</button>
        </div>
        <div class="section-word-count">${words} words</div>
    `;

    const header = card.querySelector('.section-card-header');
    const body = card.querySelector('.section-card-body');
    const bodyP = body.querySelector('p');
    const editActions = card.querySelector('.edit-actions');
    const wordCountEl = card.querySelector('.section-word-count');

    header.addEventListener('click', e => {
        if (e.target.closest('.regen-btn') || e.target.closest('.edit-btn') || e.target.closest('.copy-btn')) return;
        card.classList.toggle('collapsed');
    });

    // Copy
    card.querySelector('.copy-btn').addEventListener('click', () => {
        navigator.clipboard.writeText(section.content).then(() => {
            showToast('Copied to clipboard', 'success');
        });
    });

    // Strip HTML on paste into contentEditable
    body.addEventListener('paste', e => {
        if (body.contentEditable !== 'true') return;
        e.preventDefault();
        const text = (e.clipboardData || window.clipboardData).getData('text/plain');
        document.execCommand('insertText', false, text);
    });

    // Edit inline
    let originalContent = '';
    card.querySelector('.edit-btn').addEventListener('click', () => {
        originalContent = bodyP.textContent;
        body.contentEditable = 'true';
        bodyP.focus();
        editActions.classList.remove('hidden');
    });

    card.querySelector('.save-edit-btn').addEventListener('click', () => {
        body.contentEditable = 'false';
        editActions.classList.add('hidden');
        const newContent = bodyP.textContent;
        generatedSections[index].content = newContent;
        wordCountEl.textContent = wordCount(newContent) + ' words';
        showToast('Section updated', 'success');
    });

    card.querySelector('.cancel-edit-btn').addEventListener('click', () => {
        body.contentEditable = 'false';
        editActions.classList.add('hidden');
        bodyP.textContent = originalContent;
    });

    // Regenerate
    card.querySelector('.regen-btn').addEventListener('click', () => {
        regenTarget = index;
        regenSectionName.textContent = `Refining: "${section.title}"`;
        regenInstructions.value = '';
        regenModal.classList.remove('hidden');
        regenInstructions.focus();
    });

    sectionsContainer.appendChild(card);
}

// --- Expand/Collapse All ---
btnExpandAll.addEventListener('click', () => {
    sectionsContainer.querySelectorAll('.section-card').forEach(c => c.classList.remove('collapsed'));
});

btnCollapseAll.addEventListener('click', () => {
    sectionsContainer.querySelectorAll('.section-card').forEach(c => c.classList.add('collapsed'));
});

// --- Regenerate section ---
regenCancel.addEventListener('click', () => regenModal.classList.add('hidden'));
regenModal.querySelector('.modal-backdrop').addEventListener('click', () => regenModal.classList.add('hidden'));

regenSubmit.addEventListener('click', submitRegen);

async function submitRegen() {
    if (regenTarget === null) return;

    const section = generatedSections[regenTarget];
    const instructions = regenInstructions.value.trim();
    regenModal.classList.add('hidden');

    const card = sectionsContainer.querySelector(`[data-index="${regenTarget}"]`);
    const bodyP = card.querySelector('.section-card-body p');
    const wordCountEl = card.querySelector('.section-word-count');
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
        wordCountEl.textContent = wordCount(data.content) + ' words';
        card.classList.remove('generating');
        showToast(`"${section.title}" regenerated`, 'success');
    } catch (err) {
        bodyP.textContent = section.content;
        card.classList.remove('generating');
        showToast(err.message, 'error');
    }
}

// --- Keyboard shortcuts ---
document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !regenModal.classList.contains('hidden')) {
        regenModal.classList.add('hidden');
    }

    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (!regenModal.classList.contains('hidden')) {
            e.preventDefault();
            submitRegen();
        }
    }
});

// --- Save & History ---
btnSave.addEventListener('click', async () => {
    if (generatedSections.length === 0) return;
    btnSave.disabled = true;

    try {
        const res = await fetch(`${API}/save-proposal`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rfp_text: rfpInput.value,
                sections: generatedSections,
            }),
        });
        if (!res.ok) throw new Error('Save failed');
        showToast('Proposal saved!', 'success');
    } catch (err) {
        showToast(err.message, 'error');
    } finally {
        btnSave.disabled = false;
    }
});

btnHistory.addEventListener('click', openHistory);
historyClose.addEventListener('click', () => historyPanel.classList.add('hidden'));
historyPanel.querySelector('.side-panel-backdrop').addEventListener('click', () => historyPanel.classList.add('hidden'));

async function openHistory() {
    historyPanel.classList.remove('hidden');
    historyList.innerHTML = '<p class="text-muted">Loading...</p>';

    try {
        const res = await fetch(`${API}/history`);
        const data = await res.json();

        if (data.length === 0) {
            historyList.innerHTML = '<p class="text-muted">No saved proposals yet.</p>';
            return;
        }

        historyList.innerHTML = '';
        data.reverse().forEach(entry => {
            const item = document.createElement('div');
            item.className = 'history-item';

            const date = new Date(entry.timestamp);
            const dateStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            item.innerHTML = `
                <div class="history-date">${escapeHtml(dateStr)}</div>
                <div class="history-preview">${escapeHtml(entry.rfp_preview)}</div>
                <div class="history-sections">${entry.sections.length} sections</div>
            `;

            item.addEventListener('click', () => {
                generatedSections = entry.sections;
                sectionsContainer.innerHTML = '';
                entry.sections.forEach((s, i) => appendSectionCard(s, i));
                stepResults.classList.remove('hidden');
                btnExport.disabled = false;
                btnSave.disabled = false;
                historyPanel.classList.add('hidden');
                showToast('Proposal loaded from history', 'success');
            });

            historyList.appendChild(item);
        });
    } catch {
        historyList.innerHTML = '<p class="text-muted">Failed to load history.</p>';
    }
}

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
