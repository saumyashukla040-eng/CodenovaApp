/**
 * CodeNova Full-Stack Suite - Main Frontend Application Logic
 * Integrates Notes Application & Expense Tracker with FastAPI REST API & SQLite
 */

// Determine API Base URL dynamically
const API_BASE = window.location.origin.includes('http') && !window.location.origin.startsWith('file://')
    ? `${window.location.origin}/api`
    : 'http://127.0.0.1:8000/api';

// Categories Configuration
const EXPENSE_CATEGORIES = [
    'Food & Dining',
    'Housing & Rent',
    'Utilities',
    'Transportation',
    'Entertainment',
    'Shopping',
    'Healthcare',
    'Education',
    'Other'
];

const INCOME_CATEGORIES = [
    'Salary',
    'Freelance',
    'Investment',
    'Bonus',
    'Gifts & Grants',
    'Other'
];

class AppState {
    constructor() {
        this.currentView = 'overview';
        this.notes = [];
        this.transactions = [];
        this.summary = {
            total_income: 0,
            total_expenses: 0,
            net_savings: 0,
            transaction_count: 0,
            income_count: 0,
            expense_count: 0
        };
        this.notesViewMode = 'grid'; // 'grid' | 'list'
        this.pendingDelete = null; // { type: 'note' | 'transaction', id: number, title: string }
        this.searchDebounceTimer = null;
    }
}

const state = new AppState();

// Main Controller
const app = {
    /**
     * Application Initialization
     */
    async init() {
        this.setupNavigation();
        this.setupClock();
        this.setupEventListeners();
        this.populateCategoryDropdown('expense');
        this.setDefaultDate();

        // Check backend health and load initial data
        await this.checkBackendHealth();
        await this.loadAllData();

        // Periodic health check every 20 seconds
        setInterval(() => this.checkBackendHealth(), 20000);
    },

    /**
     * Check API connection status
     */
    async checkBackendHealth() {
        const pulse = document.getElementById('serverPulse');
        const text = document.getElementById('serverStatusText');
        try {
            const res = await fetch(`${API_BASE}/health`);
            if (res.ok) {
                pulse.classList.remove('offline');
                text.textContent = 'Connected (SQLite)';
                text.style.color = 'var(--green-income)';
            } else {
                throw new Error('Unhealthy status');
            }
        } catch (err) {
            pulse.classList.add('offline');
            text.textContent = 'Disconnected';
            text.style.color = 'var(--rose-expense)';
        }
    },

    /**
     * Topbar Live Clock
     */
    setupClock() {
        const clockEl = document.getElementById('liveTimeBadge');
        const update = () => {
            const now = new Date();
            clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        };
        update();
        setInterval(update, 1000);
    },

    /**
     * Setup sidebar view switching and mobile drawer
     */
    setupNavigation() {
        const navButtons = document.querySelectorAll('.nav-item[data-view]');
        const sidebar = document.getElementById('sidebar');
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');

        navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const view = btn.getAttribute('data-view');
                this.switchView(view);
                // Close sidebar on mobile
                sidebar.classList.remove('open');
            });
        });

        mobileMenuBtn.addEventListener('click', () => sidebar.classList.add('open'));
        sidebarCloseBtn.addEventListener('click', () => sidebar.classList.remove('open'));

        // Dynamic Topbar Action Button
        const topbarActionBtn = document.getElementById('topbarActionBtn');
        topbarActionBtn.addEventListener('click', () => {
            if (state.currentView === 'expenses') {
                this.openTransactionModal();
            } else {
                this.openNoteModal();
            }
        });
    },

    /**
     * Switch current view panel
     */
    switchView(viewName) {
        state.currentView = viewName;

        // Update nav items
        document.querySelectorAll('.nav-item[data-view]').forEach(item => {
            item.classList.toggle('active', item.getAttribute('data-view') === viewName);
        });

        // Update view sections
        document.querySelectorAll('.view-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        const activePanel = document.getElementById(`view-${viewName}`);
        if (activePanel) {
            activePanel.classList.add('active');
        }

        // Update topbar titles and quick action
        const titleEl = document.getElementById('pageTitle');
        const subTitleEl = document.getElementById('pageSubtitle');
        const actionText = document.getElementById('topbarActionText');

        if (viewName === 'overview') {
            titleEl.textContent = 'Dashboard Overview';
            subTitleEl.textContent = 'Comprehensive system overview and financial summary';
            actionText.textContent = 'Create Note';
        } else if (viewName === 'notes') {
            titleEl.textContent = 'Notes Application';
            subTitleEl.textContent = 'Organize, search, and manage your notes';
            actionText.textContent = 'New Note';
        } else if (viewName === 'expenses') {
            titleEl.textContent = 'Expense Tracker';
            subTitleEl.textContent = 'Track income, monitor expenses, and calculate net savings';
            actionText.textContent = 'Add Transaction';
        }
    },

    /**
     * Load notes and expenses from the backend
     */
    async loadAllData() {
        await Promise.all([
            this.fetchNotes(),
            this.fetchTransactions(),
            this.fetchSummary()
        ]);
        this.renderOverview();
    },

    // =========================================================================
    // TASK 1: NOTES APPLICATION LOGIC
    // =========================================================================

    /**
     * Fetch notes with optional search query & category filter
     */
    async fetchNotes() {
        try {
            const searchInput = document.getElementById('notesSearchInput').value.trim();
            const categorySelect = document.getElementById('notesCategoryFilter').value;

            const params = new URLSearchParams();
            if (searchInput) params.append('search', searchInput);
            if (categorySelect && categorySelect !== 'all') params.append('category', categorySelect);

            const url = `${API_BASE}/notes${params.toString() ? '?' + params.toString() : ''}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error('Failed to load notes');

            const data = await res.json();
            state.notes = data;
            this.renderNotes();
            this.updateNotesCounter();
        } catch (err) {
            console.error('Error fetching notes:', err);
            this.showToast('Could not load notes from database.', 'error');
        }
    },

    /**
     * Render notes cards into the grid
     */
    renderNotes() {
        const container = document.getElementById('notesContainer');
        const emptyState = document.getElementById('notesEmptyState');
        const emptyMsg = document.getElementById('notesEmptyMessage');

        if (!state.notes || state.notes.length === 0) {
            container.innerHTML = '';
            emptyState.style.display = 'flex';
            const searchVal = document.getElementById('notesSearchInput').value.trim();
            if (searchVal) {
                emptyMsg.textContent = `No notes match your search "${searchVal}".`;
            } else {
                emptyMsg.textContent = 'Create your first note to start organizing your thoughts.';
            }
            return;
        }

        emptyState.style.display = 'none';

        container.className = `notes-grid ${state.notesViewMode === 'list' ? 'list-view' : ''}`;

        container.innerHTML = state.notes.map(note => {
            const formattedDate = new Date(note.updated_at).toLocaleDateString([], {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });

            const colorClass = note.color ? `color-${note.color}` : 'color-purple';

            return `
                <div class="note-card ${colorClass}" data-id="${note.id}">
                    <div class="note-header">
                        <div class="note-title-wrap">
                            ${note.is_pinned ? `
                                <span class="pin-badge" title="Pinned Note">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                                </span>
                            ` : ''}
                            <h4 class="note-title">${this.escapeHtml(note.title)}</h4>
                        </div>
                        <div class="note-actions">
                            <button class="btn-icon" onclick="app.togglePinNote(${note.id}, ${!note.is_pinned})" title="${note.is_pinned ? 'Unpin Note' : 'Pin to Top'}">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="${note.is_pinned ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                            </button>
                            <button class="btn-icon" onclick="app.editNote(${note.id})" title="Edit Note">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                            </button>
                            <button class="btn-icon" onclick="app.confirmDeleteNote(${note.id}, '${this.escapeJs(note.title)}')" title="Delete Note">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </div>
                    <div class="note-content">${this.escapeHtml(note.content)}</div>
                    <div class="note-footer">
                        <span class="category-tag">${this.escapeHtml(note.category || 'General')}</span>
                        <span>Updated ${formattedDate}</span>
                    </div>
                </div>
            `;
        }).join('');
    },

    /**
     * Update Notes count badge
     */
    updateNotesCounter() {
        const count = state.notes.length;
        document.getElementById('notesNavCount').textContent = count;
        document.getElementById('kpiTotalNotes').textContent = count;
        const pinned = state.notes.filter(n => n.is_pinned).length;
        document.getElementById('kpiPinnedNotes').textContent = `${pinned} pinned to top`;
    },

    /**
     * Open Note creation modal
     */
    openNoteModal(note = null) {
        const modal = document.getElementById('noteModal');
        const titleEl = document.getElementById('noteModalTitle');
        const form = document.getElementById('noteForm');

        form.reset();
        document.getElementById('noteId').value = '';

        if (note) {
            titleEl.textContent = 'Edit Note';
            document.getElementById('noteId').value = note.id;
            document.getElementById('noteTitle').value = note.title;
            document.getElementById('noteContent').value = note.content;
            document.getElementById('noteCategory').value = note.category || 'General';
            document.getElementById('noteIsPinned').checked = !!note.is_pinned;

            const colorRadios = document.querySelectorAll('input[name="noteColor"]');
            colorRadios.forEach(r => {
                r.checked = (r.value === (note.color || 'purple'));
            });
        } else {
            titleEl.textContent = 'Create New Note';
            const defaultColor = document.querySelector('input[name="noteColor"][value="purple"]');
            if (defaultColor) defaultColor.checked = true;
        }

        modal.classList.add('open');
        document.getElementById('noteTitle').focus();
    },

    closeNoteModal() {
        document.getElementById('noteModal').classList.remove('open');
    },

    /**
     * Save Note (Create or Update)
     */
    async handleNoteSubmit(e) {
        e.preventDefault();
        const noteId = document.getElementById('noteId').value;
        const title = document.getElementById('noteTitle').value.trim();
        const content = document.getElementById('noteContent').value.trim();
        const category = document.getElementById('noteCategory').value;
        const is_pinned = document.getElementById('noteIsPinned').checked;
        const colorRadio = document.querySelector('input[name="noteColor"]:checked');
        const color = colorRadio ? colorRadio.value : 'purple';

        if (!title || !content) {
            this.showToast('Please provide both a title and content for the note.', 'error');
            return;
        }

        const payload = { title, content, category, color, is_pinned };

        try {
            let res;
            if (noteId) {
                // Update
                res = await fetch(`${API_BASE}/notes/${noteId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } else {
                // Create
                res = await fetch(`${API_BASE}/notes`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'Failed to save note');
            }

            this.closeNoteModal();
            this.showToast(noteId ? 'Note updated successfully!' : 'Note created successfully!', 'success');
            await this.fetchNotes();
            this.renderOverview();
        } catch (err) {
            console.error('Save note error:', err);
            this.showToast(err.message || 'Error saving note.', 'error');
        }
    },

    /**
     * Quick toggle pin on a note
     */
    async togglePinNote(noteId, newPinStatus) {
        try {
            const res = await fetch(`${API_BASE}/notes/${noteId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ is_pinned: newPinStatus })
            });
            if (!res.ok) throw new Error('Failed to update pin status');
            await this.fetchNotes();
            this.renderOverview();
            this.showToast(newPinStatus ? 'Note pinned to top' : 'Note unpinned', 'info');
        } catch (err) {
            this.showToast('Could not update note pin.', 'error');
        }
    },

    /**
     * Edit Note handler
     */
    editNote(noteId) {
        const note = state.notes.find(n => n.id === noteId);
        if (note) {
            this.openNoteModal(note);
        }
    },

    /**
     * Confirm Note deletion
     */
    confirmDeleteNote(noteId, title) {
        state.pendingDelete = { type: 'note', id: noteId, title };
        document.getElementById('deleteModalMessage').textContent =
            `Are you sure you want to permanently delete the note "${title}"? This cannot be undone.`;
        document.getElementById('deleteModal').classList.add('open');
    },

    // =========================================================================
    // TASK 2: EXPENSE TRACKER LOGIC
    // =========================================================================

    /**
     * Fetch financial summary totals calculated directly from database records
     */
    async fetchSummary() {
        try {
            const res = await fetch(`${API_BASE}/expenses/summary`);
            if (!res.ok) throw new Error('Failed to load summary');
            const data = await res.json();
            state.summary = data;
            this.renderSummary();
        } catch (err) {
            console.error('Error fetching summary:', err);
        }
    },

    /**
     * Render KPI cards with calculated totals
     */
    renderSummary() {
        const { total_income, total_expenses, net_savings, income_count, expense_count } = state.summary;

        const formatCurrency = (val) => {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2
            }).format(val);
        };

        // Overview View
        document.getElementById('kpiTotalIncome').textContent = formatCurrency(total_income);
        document.getElementById('kpiTotalExpense').textContent = formatCurrency(total_expenses);
        const netEl = document.getElementById('kpiNetSavings');
        netEl.textContent = formatCurrency(net_savings);
        netEl.style.color = net_savings >= 0 ? 'var(--blue-primary)' : 'var(--rose-expense)';

        document.getElementById('kpiIncomeCount').textContent = `${income_count} recorded credits`;
        document.getElementById('kpiExpenseCount').textContent = `${expense_count} recorded debits`;

        // Expenses View
        document.getElementById('expenseTotalIncome').textContent = formatCurrency(total_income);
        document.getElementById('expenseTotalExpenses').textContent = formatCurrency(total_expenses);
        const expNetEl = document.getElementById('expenseNetSavings');
        expNetEl.textContent = formatCurrency(net_savings);
        expNetEl.style.color = net_savings >= 0 ? 'var(--blue-primary)' : 'var(--rose-expense)';

        document.getElementById('expenseIncomeSubtext').textContent = `${income_count} credits`;
        document.getElementById('expenseExpensesSubtext').textContent = `${expense_count} debits`;
        document.getElementById('expenseNetStatus').textContent =
            net_savings >= 0 ? 'Surplus / Positive savings' : 'Deficit / Needs attention';
    },

    /**
     * Fetch transactions with search, type and category filters
     */
    async fetchTransactions() {
        try {
            const search = document.getElementById('txnsSearchInput').value.trim();
            const type = document.getElementById('txnsTypeFilter').value;
            const category = document.getElementById('txnsCategoryFilter').value;

            const params = new URLSearchParams();
            if (search) params.append('search', search);
            if (type && type !== 'all') params.append('type', type);
            if (category && category !== 'all') params.append('category', category);

            const url = `${API_BASE}/expenses${params.toString() ? '?' + params.toString() : ''}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error('Failed to load transactions');

            const data = await res.json();
            state.transactions = data;
            this.renderTransactions();
            document.getElementById('expensesNavCount').textContent = data.length;
        } catch (err) {
            console.error('Error fetching transactions:', err);
            this.showToast('Could not load transactions from database.', 'error');
        }
    },

    /**
     * Render interactive transaction table
     */
    renderTransactions() {
        const tbody = document.getElementById('txnsTableBody');
        const emptyState = document.getElementById('txnsEmptyState');
        const table = document.getElementById('txnsTable');

        if (!state.transactions || state.transactions.length === 0) {
            tbody.innerHTML = '';
            table.style.display = 'none';
            emptyState.style.display = 'flex';
            return;
        }

        table.style.display = 'table';
        emptyState.style.display = 'none';

        tbody.innerHTML = state.transactions.map(txn => {
            const isIncome = txn.type.toLowerCase() === 'income';
            const formattedDate = new Date(txn.date).toLocaleDateString([], {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });

            const formattedAmount = (isIncome ? '+ $' : '- $') + txn.amount.toFixed(2);
            const amountClass = isIncome ? 'amount-income' : 'amount-expense';
            const badgeClass = isIncome ? 'badge-income' : 'badge-expense';

            return `
                <tr>
                    <td>
                        <span style="font-family:'JetBrains Mono', monospace; font-size:0.82rem;">${formattedDate}</span>
                    </td>
                    <td>
                        <div style="font-weight:600; color:#fff;">${this.escapeHtml(txn.title)}</div>
                        ${txn.notes ? `<div style="font-size:0.75rem; color:var(--text-muted);">${this.escapeHtml(txn.notes)}</div>` : ''}
                    </td>
                    <td>
                        <span class="category-tag">${this.escapeHtml(txn.category)}</span>
                    </td>
                    <td>
                        <span class="badge ${badgeClass}">${isIncome ? 'Income' : 'Expense'}</span>
                    </td>
                    <td class="text-right">
                        <span class="${amountClass}">${formattedAmount}</span>
                    </td>
                    <td class="text-center">
                        <div class="action-btns-group">
                            <button class="btn-icon" onclick="app.editTransaction(${txn.id})" title="Edit Transaction">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                            </button>
                            <button class="btn-icon" onclick="app.confirmDeleteTransaction(${txn.id}, '${this.escapeJs(txn.title)}')" title="Delete Transaction">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    },

    /**
     * Populate categories inside the transaction modal based on type
     */
    populateCategoryDropdown(type, selectedCategory = '') {
        const select = document.getElementById('txnCategory');
        const categories = type === 'income' ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;

        select.innerHTML = categories.map(cat =>
            `<option value="${cat}" ${cat === selectedCategory ? 'selected' : ''}>${cat}</option>`
        ).join('');
    },

    /**
     * Set default transaction date to today's date YYYY-MM-DD
     */
    setDefaultDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('txnDate').value = today;
    },

    /**
     * Open Transaction Modal
     */
    openTransactionModal(txn = null) {
        const modal = document.getElementById('txnModal');
        const form = document.getElementById('txnForm');
        const titleEl = document.getElementById('txnModalTitle');

        form.reset();
        document.getElementById('txnId').value = '';
        this.setDefaultDate();

        if (txn) {
            titleEl.textContent = 'Edit Transaction';
            document.getElementById('txnId').value = txn.id;
            document.getElementById('txnTitle').value = txn.title;
            document.getElementById('txnAmount').value = txn.amount;
            document.getElementById('txnDate').value = txn.date;
            document.getElementById('txnNotes').value = txn.notes || '';
            this.setTransactionType(txn.type.toLowerCase(), txn.category);
        } else {
            titleEl.textContent = 'Add Transaction';
            this.setTransactionType('expense');
        }

        modal.classList.add('open');
        document.getElementById('txnAmount').focus();
    },

    closeTransactionModal() {
        document.getElementById('txnModal').classList.remove('open');
    },

    /**
     * Toggle type selector buttons in transaction modal
     */
    setTransactionType(type, selectedCategory = '') {
        document.getElementById('txnType').value = type;
        const btnExpense = document.getElementById('typeExpenseBtn');
        const btnIncome = document.getElementById('typeIncomeBtn');

        if (type === 'income') {
            btnIncome.classList.add('active');
            btnExpense.classList.remove('active');
        } else {
            btnExpense.classList.add('active');
            btnIncome.classList.remove('active');
        }

        this.populateCategoryDropdown(type, selectedCategory);
    },

    /**
     * Handle transaction submission with validation
     */
    async handleTransactionSubmit(e) {
        e.preventDefault();
        const txnId = document.getElementById('txnId').value;
        const type = document.getElementById('txnType').value;
        const title = document.getElementById('txnTitle').value.trim();
        const amountRaw = document.getElementById('txnAmount').value;
        const date = document.getElementById('txnDate').value;
        const category = document.getElementById('txnCategory').value;
        const notes = document.getElementById('txnNotes').value.trim();

        // Validation
        const amount = parseFloat(amountRaw);
        if (isNaN(amount) || amount <= 0) {
            this.showToast('Amount must be a valid number strictly greater than 0.', 'error');
            return;
        }

        if (!date) {
            this.showToast('Please select a valid date.', 'error');
            return;
        }

        if (!title) {
            this.showToast('Please enter a description for the transaction.', 'error');
            return;
        }

        const payload = {
            title,
            amount,
            type,
            category,
            date,
            notes
        };

        try {
            let res;
            if (txnId) {
                res = await fetch(`${API_BASE}/expenses/${txnId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            } else {
                res = await fetch(`${API_BASE}/expenses`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
            }

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'Failed to save transaction');
            }

            this.closeTransactionModal();
            this.showToast(txnId ? 'Transaction updated successfully!' : 'Transaction added successfully!', 'success');
            await this.fetchTransactions();
            await this.fetchSummary();
            this.renderOverview();
        } catch (err) {
            console.error('Save transaction error:', err);
            this.showToast(err.message || 'Error saving transaction.', 'error');
        }
    },

    editTransaction(txnId) {
        const txn = state.transactions.find(t => t.id === txnId);
        if (txn) {
            this.openTransactionModal(txn);
        }
    },

    confirmDeleteTransaction(txnId, title) {
        state.pendingDelete = { type: 'transaction', id: txnId, title };
        document.getElementById('deleteModalMessage').textContent =
            `Are you sure you want to permanently delete the transaction "${title}"? This cannot be undone.`;
        document.getElementById('deleteModal').classList.add('open');
    },

    // =========================================================================
    // GENERAL DELETION & MODAL HELPERS
    // =========================================================================

    closeDeleteModal() {
        document.getElementById('deleteModal').classList.remove('open');
        state.pendingDelete = null;
    },

    async handleConfirmDelete() {
        if (!state.pendingDelete) return;
        const { type, id } = state.pendingDelete;

        try {
            let res;
            if (type === 'note') {
                res = await fetch(`${API_BASE}/notes/${id}`, { method: 'DELETE' });
            } else if (type === 'transaction') {
                res = await fetch(`${API_BASE}/expenses/${id}`, { method: 'DELETE' });
            }

            if (!res.ok) throw new Error('Deletion failed on server.');

            this.showToast(`${type === 'note' ? 'Note' : 'Transaction'} permanently deleted.`, 'info');
            this.closeDeleteModal();

            if (type === 'note') {
                await this.fetchNotes();
            } else {
                await this.fetchTransactions();
                await this.fetchSummary();
            }
            this.renderOverview();
        } catch (err) {
            console.error('Delete error:', err);
            this.showToast('Could not delete item. Please retry.', 'error');
        }
    },

    // =========================================================================
    // OVERVIEW VIEW COMPONENT
    // =========================================================================

    renderOverview() {
        // Render up to 4 recent notes
        const recentNotesContainer = document.getElementById('overviewRecentNotes');
        if (!state.notes || state.notes.length === 0) {
            recentNotesContainer.innerHTML = '<div class="empty-state-mini"><p>No notes found. Create your first note!</p></div>';
        } else {
            const topNotes = state.notes.slice(0, 4);
            recentNotesContainer.innerHTML = topNotes.map(n => `
                <div class="recent-item">
                    <div class="recent-item-info">
                        <span class="recent-item-title">${n.is_pinned ? '★ ' : ''}${this.escapeHtml(n.title)}</span>
                        <span class="recent-item-meta">${this.escapeHtml(n.category || 'General')} • ${new Date(n.updated_at).toLocaleDateString()}</span>
                    </div>
                    <button class="btn btn-secondary btn-sm" onclick="app.editNote(${n.id})">Open</button>
                </div>
            `).join('');
        }

        // Render up to 4 recent transactions
        const recentTxnsContainer = document.getElementById('overviewRecentTxns');
        if (!state.transactions || state.transactions.length === 0) {
            recentTxnsContainer.innerHTML = '<div class="empty-state-mini"><p>No transactions yet. Add income or expenses!</p></div>';
        } else {
            const topTxns = state.transactions.slice(0, 4);
            recentTxnsContainer.innerHTML = topTxns.map(t => {
                const isIncome = t.type.toLowerCase() === 'income';
                return `
                    <div class="recent-item">
                        <div class="recent-item-info">
                            <span class="recent-item-title">${this.escapeHtml(t.title)}</span>
                            <span class="recent-item-meta">${this.escapeHtml(t.category)} • ${t.date}</span>
                        </div>
                        <span class="${isIncome ? 'amount-income' : 'amount-expense'}" style="font-size:0.9rem;">
                            ${isIncome ? '+' : '-'} $${t.amount.toFixed(2)}
                        </span>
                    </div>
                `;
            }).join('');
        }
    },

    // =========================================================================
    // EVENT LISTENERS BINDING
    // =========================================================================

    setupEventListeners() {
        // Form submits
        document.getElementById('noteForm').addEventListener('submit', (e) => this.handleNoteSubmit(e));
        document.getElementById('txnForm').addEventListener('submit', (e) => this.handleTransactionSubmit(e));
        document.getElementById('confirmDeleteBtn').addEventListener('click', () => this.handleConfirmDelete());

        // Modal triggers
        document.getElementById('openAddNoteModalBtn').addEventListener('click', () => this.openNoteModal());
        document.getElementById('openAddTxnModalBtn').addEventListener('click', () => this.openTransactionModal());

        // Expense type toggle in modal
        document.getElementById('typeExpenseBtn').addEventListener('click', () => this.setTransactionType('expense'));
        document.getElementById('typeIncomeBtn').addEventListener('click', () => this.setTransactionType('income'));

        // Notes Search & Filters
        const notesSearch = document.getElementById('notesSearchInput');
        const notesClear = document.getElementById('notesClearSearch');
        notesSearch.addEventListener('input', () => {
            notesClear.style.display = notesSearch.value ? 'block' : 'none';
            clearTimeout(state.searchDebounceTimer);
            state.searchDebounceTimer = setTimeout(() => this.fetchNotes(), 250);
        });
        notesClear.addEventListener('click', () => {
            notesSearch.value = '';
            notesClear.style.display = 'none';
            this.fetchNotes();
        });
        document.getElementById('notesCategoryFilter').addEventListener('change', () => this.fetchNotes());

        // Notes Grid/List View Toggle
        const notesToggleBtn = document.getElementById('notesViewToggle');
        notesToggleBtn.addEventListener('click', () => {
            state.notesViewMode = state.notesViewMode === 'grid' ? 'list' : 'grid';
            this.renderNotes();
        });

        // Transactions Search & Filters
        const txnsSearch = document.getElementById('txnsSearchInput');
        const txnsClear = document.getElementById('txnsClearSearch');
        txnsSearch.addEventListener('input', () => {
            txnsClear.style.display = txnsSearch.value ? 'block' : 'none';
            clearTimeout(state.searchDebounceTimer);
            state.searchDebounceTimer = setTimeout(() => this.fetchTransactions(), 250);
        });
        txnsClear.addEventListener('click', () => {
            txnsSearch.value = '';
            txnsClear.style.display = 'none';
            this.fetchTransactions();
        });
        document.getElementById('txnsTypeFilter').addEventListener('change', () => this.fetchTransactions());
        document.getElementById('txnsCategoryFilter').addEventListener('change', () => this.fetchTransactions());

        // Close modals on Escape key or backdrop click
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeNoteModal();
                this.closeTransactionModal();
                this.closeDeleteModal();
            }
        });

        ['noteModal', 'txnModal', 'deleteModal'].forEach(id => {
            const el = document.getElementById(id);
            el.addEventListener('click', (e) => {
                if (e.target === el) {
                    el.classList.remove('open');
                }
            });
        });
    },

    // =========================================================================
    // UTILITY METHODS
    // =========================================================================

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        let icon = '';
        if (type === 'success') {
            icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--green-income)" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
        } else if (type === 'error') {
            icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--rose-expense)" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
        } else {
            icon = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--blue-primary)" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
        }

        toast.innerHTML = `
            ${icon}
            <span class="toast-message">${this.escapeHtml(message)}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.25s ease';
            setTimeout(() => toast.remove(), 250);
        }, 3200);
    },

    escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    },

    escapeJs(str) {
        if (!str) return '';
        return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
    }
};

// Initialize Application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = app;
    app.init();
});
