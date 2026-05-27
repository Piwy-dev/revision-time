<script>
  import { onMount } from 'svelte'

  export let examSessions = []
  export let onExamUpdated = () => {}
  export let onExamDeleted = () => {}

  let loading = false
  let error = ''
  let editingId = null
  let editFormData = {}

  function startEdit(exam) {
    editingId = exam.id
    editFormData = {
      name: exam.name,
      description: exam.description,
      start_date: exam.start_date,
      end_date: exam.end_date,
      target_minutes: exam.target_minutes,
    }
  }

  function cancelEdit() {
    editingId = null
    editFormData = {}
  }

  async function saveEdit() {
    if (!editFormData.name.trim()) {
      error = 'Exam name is required'
      return
    }

    if (new Date(editFormData.end_date) <= new Date(editFormData.start_date)) {
      error = 'End date must be after start date'
      return
    }

    if (!editFormData.target_minutes || editFormData.target_minutes <= 0) {
      error = 'Daily target must be greater than 0'
      return
    }

    loading = true
    error = ''

    try {
      const response = await fetch(`/api/exam-sessions/${editingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editFormData),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to update exam')
      }

      const updatedExam = await response.json()
      
      // Update exam in list
      const index = examSessions.findIndex(e => e.id === editingId)
      if (index !== -1) {
        examSessions[index] = updatedExam
      }

      editingId = null
      editFormData = {}
      onExamUpdated(updatedExam)
    } catch (err) {
      error = err.message || 'Error updating exam'
    } finally {
      loading = false
    }
  }

  async function deleteExam(exam) {
    const message = `Delete "${exam.name}"? All study sessions and data will be permanently removed.`
    if (!confirm(message)) return

    loading = true
    error = ''

    try {
      const response = await fetch(`/api/exam-sessions/${exam.id}`, {
        method: 'DELETE',
      })

      if (!response.ok) throw new Error('Failed to delete exam')

      // Remove from list
      examSessions = examSessions.filter(e => e.id !== exam.id)
      onExamDeleted(exam)
    } catch (err) {
      error = err.message || 'Error deleting exam'
    } finally {
      loading = false
    }
  }

  function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00')
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }
</script>

<div class="exam-manager-container">
  <h2>📚 Manage Exams</h2>

  {#if error}
    <div class="error-message">{error}</div>
  {/if}

  {#if examSessions.length === 0}
    <div class="empty-state">
      <p>No exam sessions yet. Create one to get started!</p>
    </div>
  {:else}
    <div class="exams-list">
      {#each examSessions as exam (exam.id)}
        <div class="exam-card">
          {#if editingId === exam.id}
            <div class="exam-card-edit">
              <div class="form-group">
                <label for="exam-name-{exam.id}">Exam Name</label>
                <input
                  id="exam-name-{exam.id}"
                  type="text"
                  bind:value={editFormData.name}
                  placeholder="Exam name"
                />
              </div>

              <div class="form-group">
                <label for="exam-desc-{exam.id}">Description</label>
                <input
                  id="exam-desc-{exam.id}"
                  type="text"
                  bind:value={editFormData.description}
                  placeholder="Optional description"
                />
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label for="start-date-{exam.id}">Start Date</label>
                  <input id="start-date-{exam.id}" type="date" bind:value={editFormData.start_date} />
                </div>
                <div class="form-group">
                  <label for="end-date-{exam.id}">End Date</label>
                  <input id="end-date-{exam.id}" type="date" bind:value={editFormData.end_date} />
                </div>
              </div>

              <div class="form-group">
                <label for="target-{exam.id}">Daily Target (minutes)</label>
                <input 
                  id="target-{exam.id}" 
                  type="number" 
                  bind:value={editFormData.target_minutes}
                  placeholder="240"
                  min="1"
                />
              </div>

              <div class="button-group">
                <button class="btn-save" on:click={saveEdit} disabled={loading}>
                  {loading ? 'Saving...' : 'Save'}
                </button>
                <button class="btn-cancel" on:click={cancelEdit} disabled={loading}>Cancel</button>
              </div>
            </div>
          {:else}
            <div class="exam-card-view">
              <div class="exam-header">
                <h3>{exam.name}</h3>
                <div class="exam-badge" class:active={exam.is_active}>
                  {exam.is_active ? 'Active' : 'Inactive'}
                </div>
              </div>

              {#if exam.description}
                <p class="description">{exam.description}</p>
              {/if}

              <div class="exam-dates">
                <div class="date-item">
                  <span class="label">Start:</span>
                  <span class="value">{formatDate(exam.start_date)}</span>
                </div>
                <div class="date-item">
                  <span class="label">End:</span>
                  <span class="value">{formatDate(exam.end_date)}</span>
                </div>
                <div class="date-item">
                  <span class="label">Daily Target:</span>
                  <span class="value">{Math.floor(exam.target_minutes / 60)}h {exam.target_minutes % 60}m</span>
                </div>
              </div>

              <div class="button-group">
                <button class="btn-edit" on:click={() => startEdit(exam)}>Edit</button>
                <button class="btn-delete" on:click={() => deleteExam(exam)}>Delete</button>
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .exam-manager-container {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
  }

  h2 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #333;
    font-size: 1.5rem;
  }

  .error-message {
    background: #fee;
    color: #c00;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 15px;
    border-left: 4px solid #c00;
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #999;
  }

  .exams-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
  }

  .exam-card {
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.2s ease;
  }

  .exam-card:hover {
    border-color: #667eea;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  }

  .exam-card-view,
  .exam-card-edit {
    padding: 15px;
  }

  .exam-card-edit {
    background: #fffacd;
  }

  .exam-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    gap: 10px;
  }

  .exam-header h3 {
    margin: 0;
    color: #333;
    font-size: 1.1rem;
    flex: 1;
    word-break: break-word;
  }

  .exam-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    white-space: nowrap;
    background: #e0e0e0;
    color: #666;
  }

  .exam-badge.active {
    background: #c3fac3;
    color: #2d5016;
  }

  .description {
    color: #666;
    font-size: 0.9rem;
    margin: 8px 0;
    font-style: italic;
  }

  .exam-dates {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 10px 0;
    border-top: 1px solid #e0e0e0;
    border-bottom: 1px solid #e0e0e0;
    margin: 10px 0;
  }

  .date-item {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
  }

  .date-item .label {
    color: #999;
    font-weight: 500;
  }

  .date-item .value {
    color: #333;
    font-weight: 600;
  }

  .form-group {
    margin-bottom: 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .form-group label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #333;
  }

  .form-group input {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.9rem;
    font-family: inherit;
  }

  .form-group input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .button-group {
    display: flex;
    gap: 8px;
    margin-top: 12px;
  }

  button {
    flex: 1;
    padding: 8px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.2s ease;
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-edit {
    background: #667eea;
    color: white;
  }

  .btn-edit:hover:not(:disabled) {
    background: #5568d3;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
  }

  .btn-delete {
    background: #ff6b6b;
    color: white;
  }

  .btn-delete:hover:not(:disabled) {
    background: #ee5a52;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(255, 107, 107, 0.3);
  }

  .btn-save {
    background: #51cf66;
    color: white;
  }

  .btn-save:hover:not(:disabled) {
    background: #40c057;
    transform: translateY(-1px);
  }

  .btn-cancel {
    background: #adb5bd;
    color: white;
  }

  .btn-cancel:hover:not(:disabled) {
    background: #868e96;
    transform: translateY(-1px);
  }

  @media (max-width: 768px) {
    .exams-list {
      grid-template-columns: 1fr;
    }

    .exam-dates {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }

    .form-row {
      grid-template-columns: 1fr;
    }
  }
</style>
