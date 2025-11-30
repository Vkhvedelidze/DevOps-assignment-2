// Global variables
let currentNoteId = null;
let notes = [];
let versions = [];
let searchTimeout = null;

// DOM elements  
const notesList = document.getElementById('notesList');
const editorContainer = document.getElementById('editorContainer');
const welcomeMessage = document.getElementById('welcomeMessage');
const noteTitle = document.getElementById('noteTitle');
const noteContent = document.getElementById('noteContent');
const saveBtn = document.getElementById('saveBtn');
const cancelBtn = document.getElementById('cancelBtn');
const newNoteBtn = document.getElementById('newNoteBtn');
const versionHistory = document.getElementById('versionHistory');
const versionsList = document.getElementById('versionsList');
const loadingSpinner = document.getElementById('loadingSpinner');
const searchInput = document.getElementById('searchInput');

// Initialize the app
document.addEventListener('DOMContentLoaded', async function () {
    console.log('✅ App Starting');

    try {
        setupEventListeners();
        console.log('✅ Event listeners set up');

        await loadNotes();
        console.log('✅ Notes loaded');
    } catch (error) {
        console.error('❌ Init error:', error);
        alert('Error: ' + error.message);
    }
});

// Event listeners
function setupEventListeners() {
    if (newNoteBtn) {
        newNoteBtn.addEventListener('click', () => {
            console.log('📝 New Note clicked');
            createNewNote();
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            console.log('💾 Save clicked');
            saveNote();
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            console.log('❌ Cancel clicked');
            cancelEdit();
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', function (e) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                loadNotes(e.target.value);
            }, 300);
        });
    }
}

// API functions
async function apiCall(url, options = {}) {
    showLoading();
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Error occurred');
            }
            return data;
        } else {
            if (!response.ok) {
                const text = await response.text();
                throw new Error(`HTTP ${response.status}: ${text.substring(0, 100)}`);
            }
            // If success but not JSON (shouldn't happen for our API but good for safety)
            return await response.text();
        }
    } catch (error) {
        console.error("API Call Error:", error);
        showNotification('Error: ' + error.message, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

// Load all notes
async function loadNotes(search = '') {
    try {
        let url = '/api/notes/';
        if (search) {
            url += `?search=${encodeURIComponent(search)}`;
        }
        notes = await apiCall(url);
        renderNotes();
    } catch (error) {
        console.error('Failed to load notes:', error);
        notes = [];
        renderNotes();
    }
}

// Render notes list
function renderNotes() {
    if (notes.length === 0) {
        notesList.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-sticky-note fa-2x mb-2"></i>
                <p>No notes found.</p>
            </div>
        `;
        return;
    }

    notesList.innerHTML = notes.map(note => `
        <div class="list-group-item list-group-item-action" onclick="selectNote('${note.id}')">
            <div class="d-flex w-100 justify-content-between align-items-start">
                <h6 class="mb-1 text-truncate flex-grow-1">${escapeHtml(note.title)}</h6>
                <div class="btn-group btn-group-sm" onclick="event.stopPropagation()">
                    <button class="btn btn-sm btn-outline-info" onclick="viewVersionHistory('${note.id}')" title="Version History">
                        <i class="fas fa-history"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteNote('${note.id}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <p class="mb-1 small text-muted text-truncate">${escapeHtml(note.content)}</p>
            <small class="text-muted">Updated: ${formatDate(note.updated_at)} • v${note.version}</small>
        </div>
    `).join('');
}

// Create new note
function createNewNote() {
    currentNoteId = null;
    noteTitle.value = '';
    noteContent.value = '';
    editorContainer.style.display = 'block';
    welcomeMessage.style.display = 'none';
    versionHistory.style.display = 'none';
    document.getElementById('editorTitle').textContent = 'Create New Note';
    noteTitle.focus();
}

// Select note
async function selectNote(noteId) {
    try {
        const note = await apiCall(`/api/notes/${noteId}`);
        currentNoteId = noteId;
        noteTitle.value = note.title;
        noteContent.value = note.content;
        editorContainer.style.display = 'block';
        welcomeMessage.style.display = 'none';
        document.getElementById('editorTitle').textContent = 'Edit Note';

        await loadNoteVersions(noteId);
    } catch (error) {
        console.error('Failed to select note:', error);
    }
}

// Save note
async function saveNote() {
    const title = noteTitle.value.trim();
    const content = noteContent.value.trim();

    if (!title || !content) {
        showNotification('Please fill in both title and content', 'error');
        return;
    }

    try {
        if (currentNoteId) {
            await apiCall(`/api/notes/${currentNoteId}`, {
                method: 'PUT',
                body: JSON.stringify({ title, content })
            });
            showNotification('Note updated successfully!', 'success');
        } else {
            const newNote = await apiCall('/api/notes/', {
                method: 'POST',
                body: JSON.stringify({ title, content })
            });
            currentNoteId = newNote.id;
            showNotification('Note created successfully!', 'success');
        }

        await loadNotes(searchInput.value);
        cancelEdit();
    } catch (error) {
        console.error('Failed to save note:', error);
    }
}

// Cancel edit
function cancelEdit() {
    currentNoteId = null;
    editorContainer.style.display = 'none';
    welcomeMessage.style.display = 'block';
    versionHistory.style.display = 'none';
}

// Delete note
function deleteNote(noteId) {
    if (!confirm('Are you sure you want to delete this note?')) {
        return;
    }

    apiCall(`/api/notes/${noteId}`, {
        method: 'DELETE'
    }).then(() => {
        showNotification('Note deleted!', 'success');

        if (currentNoteId === noteId) {
            cancelEdit();
        }

        loadNotes(searchInput.value);
    }).catch(error => {
        console.error('Failed to delete note:', error);
    });
}

// View version history
function viewVersionHistory(noteId) {
    selectNote(noteId);
}

// Load note versions
async function loadNoteVersions(noteId) {
    try {
        versions = await apiCall(`/api/notes/${noteId}/versions`);
        renderVersions();
        versionHistory.style.display = 'block';
    } catch (error) {
        console.error('Failed to load versions:', error);
    }
}

// Render versions
function renderVersions() {
    if (versions.length === 0) {
        versionsList.innerHTML = '<div class="text-muted text-center py-2">No version history</div>';
        return;
    }

    versionsList.innerHTML = versions.map(version => `
        <div class="list-group-item">
            <div class="d-flex w-100 justify-content-between">
                <div>
                    <h6 class="mb-1">Version ${version.version}</h6>
                    <p class="mb-1 small">${escapeHtml(version.title)}</p>
                    <small class="text-muted">${formatDate(version.created_at)}</small>
                </div>
                <button class="btn btn-sm btn-primary" onclick="restoreVersion('${version.id}')">
                    <i class="fas fa-undo"></i> Restore
                </button>
            </div>
        </div>
    `).join('');
}

// Restore version
async function restoreVersion(versionId) {
    if (!confirm('Restore this version? This will create a new version.')) {
        return;
    }

    try {
        await apiCall(`/api/notes/${currentNoteId}/restore/${versionId}`, {
            method: 'POST'
        });
        showNotification('Version restored!', 'success');

        await loadNotes(searchInput.value);
        await loadNoteVersions(currentNoteId);
        await selectNote(currentNoteId);
    } catch (error) {
        console.error('Failed to restore version:', error);
    }
}

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function showLoading() {
    if (loadingSpinner) {
        loadingSpinner.classList.remove('d-none');
        loadingSpinner.classList.add('d-flex');
    }
}

function hideLoading() {
    if (loadingSpinner) {
        loadingSpinner.classList.remove('d-flex');
        loadingSpinner.classList.add('d-none');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-primary';
    notification.className = `position-fixed top-0 end-0 m-3 p-3 rounded text-white shadow ${bgClass}`;
    notification.style.zIndex = '2000';
    notification.innerHTML = `
        <div class="d-flex align-items-center gap-2">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

console.log('✅ Script loaded');
