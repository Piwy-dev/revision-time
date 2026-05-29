<script>
  import { onMount } from 'svelte'

  export let examSessionId = null

  let sessions = []
  let loading = false
  let error = ''
  let editingId = null
  let editFormData = {}
  let currentPage = 0
  const itemsPerPage = 20
  let paginatedSessions = []

  function sortSessions(sessionsToSort) {
    return sessionsToSort.sort((a, b) => {
      // First sort by date (descending - most recent first)
      const dateCompare = b.date.localeCompare(a.date)
      if (dateCompare !== 0) return dateCompare
      // Then sort by start time (descending)
      return b.start_time.localeCompare(a.start_time)
    })
  }

  function formatDate(dateString) {
    const [year, month, day] = dateString.split('-')
    return `${day}/${month}/${year}`
  }

  async function loadSessions() {
    if (!examSessionId) return
    loading = true
    error = ''
    currentPage = 0

    try {
      // Fetch all sessions for this exam session using a wide date range
      const startDate = '2000-01-01' // Far in the past
      const today = new Date()
      const endDate = today.toISOString().split('T')[0]
      
      const response = await fetch(
        `/api/sessions?exam_session_id=${examSessionId}&start_date=${startDate}&end_date=${endDate}`
      )
      if (!response.ok) throw new Error('Failed to load sessions')
      sessions = sortSessions(await response.json())
    } catch (err) {
      error = err.message || 'Error loading sessions'
    } finally {
      loading = false
    }
  }

  function startEdit(session) {
    editingId = session.id
    editFormData = {
      date: session.date,
      start_time: session.start_time,
      end_time: session.end_time,
    }
  }

  function cancelEdit() {
    editingId = null
    editFormData = {}
  }

  async function saveEdit() {
    if (!examSessionId) return

    try {
      const response = await fetch(`/api/sessions/${editingId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exam_session_id: examSessionId,
          date: editFormData.date,
          start_time: editFormData.start_time,
          end_time: editFormData.end_time,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to update session')
      }

      editingId = null
      editFormData = {}
      await loadSessions()
      sessions = sortSessions(sessions)
    } catch (err) {
      error = err.message || 'Error updating session'
    }
  }

  async function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this session?')) return

    try {
      const response = await fetch(`/api/sessions/${sessionId}`, {
        method: 'DELETE',
      })

      if (!response.ok) throw new Error('Failed to delete session')

      await loadSessions()
      sessions = sortSessions(sessions)
    } catch (err) {
      error = err.message || 'Error deleting session'
    }
  }

  function calculateDuration(startTime, endTime) {
    const start = new Date(`2000-01-01 ${startTime}`)
    const end = new Date(`2000-01-01 ${endTime}`)
    const diff = (end - start) / 1000 / 60
    return Math.max(0, diff)
  }

  function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours === 0) return `${mins}m`
    if (mins === 0) return `${hours}h`
    return `${hours}h ${mins}m`
  }

  function getPaginatedSessions() {
    const start = currentPage * itemsPerPage
    const end = start + itemsPerPage
    return sessions.slice(start, end)
  }

  function getTotalPages() {
    return Math.max(1, Math.ceil(sessions.length / itemsPerPage))
  }

  function goToNextPage() {
    const maxPage = getTotalPages() - 1
    if (currentPage < maxPage) {
      currentPage = currentPage + 1
    }
  }

  function goToPreviousPage() {
    if (currentPage > 0) {
      currentPage = currentPage - 1
    }
  }

  $: if (examSessionId) {
    loadSessions()
  }

  $: {
    const start = currentPage * itemsPerPage
    const end = start + itemsPerPage
    paginatedSessions = sessions.slice(start, end)
  }
</script>

<div class="sessions-list-container">
  <h2>📋 All Sessions</h2>

  {#if error}
    <div class="error-message">{error}</div>
  {/if}

  {#if loading}
    <div class="loading">Loading sessions...</div>
  {:else if sessions.length === 0}
    <div class="empty-state">
      <p>No sessions found for this period.</p>
    </div>
  {:else}
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Duration</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each paginatedSessions as session (session.id)}
            {#if editingId === session.id}
              <tr class="editing">
                <td>
                  <input type="date" bind:value={editFormData.date} required />
                </td>
                <td>
                  <input type="time" bind:value={editFormData.start_time} required />
                </td>
                <td>
                  <input type="time" bind:value={editFormData.end_time} required />
                </td>
                <td class="duration">
                  {formatDuration(calculateDuration(editFormData.start_time, editFormData.end_time))}
                </td>
                <td class="actions">
                  <button class="btn-save" on:click={saveEdit}>Save</button>
                  <button class="btn-cancel" on:click={cancelEdit}>Cancel</button>
                </td>
              </tr>
            {:else}
              <tr>
                <td>{formatDate(session.date)}</td>
                <td>{session.start_time}</td>
                <td>{session.end_time}</td>
                <td class="duration">{formatDuration(session.duration_minutes)}</td>
                <td class="actions">
                  <button class="btn-edit" on:click={() => startEdit(session)}>Edit</button>
                  <button class="btn-delete" on:click={() => deleteSession(session.id)}>Delete</button>
                </td>
              </tr>
            {/if}
          {/each}
        </tbody>
      </table>
    </div>

    <div class="pagination-controls">
      <button 
        class="pagination-btn" 
        on:click={goToPreviousPage} 
        disabled={currentPage === 0}
      >
        ← Previous
      </button>
      <span class="page-info">
        Page {currentPage + 1} of {getTotalPages()}
      </span>
      <button 
        class="pagination-btn" 
        on:click={goToNextPage} 
        disabled={currentPage === getTotalPages() - 1}
      >
        Next →
      </button>
    </div>
  {/if}
</div>

<style>
  .sessions-list-container {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
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

  .loading {
    text-align: center;
    padding: 40px 20px;
    color: #666;
    font-style: italic;
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #999;
  }

  .table-container {
    overflow-x: auto;
    margin-bottom: 20px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
  }

  thead {
    background: #f5f5f5;
    border-bottom: 2px solid #ddd;
  }

  th {
    padding: 12px;
    text-align: left;
    font-weight: 600;
    color: #333;
  }

  td {
    padding: 12px;
    border-bottom: 1px solid #e0e0e0;
  }

  tr:hover {
    background: #fafafa;
  }

  tr.editing {
    background: #fffacd;
  }

  tr.editing:hover {
    background: #fffacd;
  }

  td input {
    width: 100%;
    padding: 6px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 0.9rem;
    font-family: inherit;
  }

  td input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
  }

  .duration {
    font-weight: 500;
    color: #667eea;
    text-align: center;
  }

  .actions {
    text-align: center;
    white-space: nowrap;
  }

  button {
    padding: 6px 12px;
    margin: 0 4px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.2s ease;
  }

  .btn-edit {
    background: #667eea;
    color: white;
  }

  .btn-edit:hover {
    background: #5568d3;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
  }

  .btn-delete {
    background: #ff6b6b;
    color: white;
  }

  .btn-delete:hover {
    background: #ee5a52;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(255, 107, 107, 0.3);
  }

  .btn-save {
    background: #51cf66;
    color: white;
  }

  .btn-save:hover {
    background: #40c057;
    transform: translateY(-1px);
  }

  .btn-cancel {
    background: #adb5bd;
    color: white;
  }

  .btn-cancel:hover {
    background: #868e96;
    transform: translateY(-1px);
  }

  .pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .pagination-btn {
    padding: 6px 12px;
    border: 1px solid #667eea;
    background: white;
    color: #667eea;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.2s ease;
  }

  .pagination-btn:hover:not(:disabled) {
    background: #667eea;
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
  }

  .pagination-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .page-info {
    font-size: 13px;
    color: #666;
    font-weight: 500;
    min-width: 100px;
    text-align: center;
  }

  @media (max-width: 768px) {
    .sessions-list-container {
      padding: 15px;
    }

    table {
      font-size: 0.85rem;
    }

    th,
    td {
      padding: 8px;
    }

    button {
      padding: 4px 8px;
      font-size: 0.75rem;
      margin: 0 2px;
    }

    .pagination-controls {
      flex-direction: column;
      gap: 10px;
    }

    .pagination-btn {
      width: 100%;
    }
  }
</style>
