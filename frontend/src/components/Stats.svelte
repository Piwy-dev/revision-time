<script>
  import { onMount } from 'svelte'

  export let examSessionId = null
  export let dateRange = { start: '', end: '' }
  export let examSession = null

  let stats = null
  let loading = true
  let error = ''
  let editingTarget = false
  let editValue = 0
  let currentPage = 0
  const daysPerPage = 7
  let paginatedDays = []

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

  function formatDate(dateString) {
    const [year, month, day] = dateString.split('-')
    return `${day}/${month}/${year}`
  }

  async function fetchStats() {
    if (!examSessionId || !examSession) return

    try {
      loading = true
      error = ''
      
      // Use exam session start date to today (or end date if exam has ended)
      const today = new Date()
      const startDate = examSession.start_date
      
      // Use end_date if available and before today, otherwise use today
      const endDate = examSession.end_date 
        ? new Date(examSession.end_date) < today
          ? examSession.end_date
          : today.toISOString().split('T')[0]
        : today.toISOString().split('T')[0]
      
      // Fetch daily stats for the full range
      const statsResponse = await fetch(
        `/api/stats/daily?exam_session_id=${examSessionId}&start_date=${startDate}&end_date=${endDate}`
      )
      if (!statsResponse.ok) throw new Error('Failed to fetch stats')
      const statsData = await statsResponse.json()
      
      // Aggregate stats by date (reverse to show most recent first)
      const aggregated = { total: 0, days: {}, datesList: [] }
      statsData.slice().reverse().forEach((d) => {
        aggregated.total += d.total_minutes
        const dateStr = formatDate(d.date)
        aggregated.days[dateStr] = { total: d.total_minutes }
        aggregated.datesList.push(dateStr)
      })
      stats = aggregated
      currentPage = 0
    } catch (err) {
      error = err.message || 'Error loading stats'
    } finally {
      loading = false
    }
  }

  function getTotalPages() {
    return Math.max(1, Math.ceil((stats?.datesList?.length || 0) / daysPerPage))
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

  async function updateTarget() {
    if (!examSessionId || !editValue || editValue <= 0) return
    
    try {
      const response = await fetch(`/api/exam-sessions/${examSessionId}/target`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_minutes: editValue }),
      })
      if (!response.ok) throw new Error('Failed to update target')
      
      // Update the exam session in parent
      if (examSession) {
        examSession.target_minutes = editValue
      }
      
      editingTarget = false
    } catch (err) {
      error = err.message || 'Error updating target'
    }
  }

  function formatMinutes(minutes) {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}h ${mins}m`
  }

  function calculateDifference(actualMinutes, targetMinutes) {
    const diff = actualMinutes - targetMinutes
    if (diff > 0) return `+${Math.floor(diff)}m`
    if (diff < 0) return `-${Math.floor(Math.abs(diff))}m`
    return '✓'
  }

  function isAboveTarget(actualMinutes, targetMinutes) {
    return actualMinutes >= targetMinutes
  }

  $: if (examSessionId && examSession) fetchStats()

  $: {
    if (stats?.datesList) {
      const start = currentPage * daysPerPage
      const end = start + daysPerPage
      paginatedDays = stats.datesList.slice(start, end)
    }
  }

  onMount(() => {
    if (examSessionId && examSession) fetchStats()
  })
</script>

<div class="card">
  <h3>📊 Statistics</h3>

  {#if loading}
    <div class="loading">Loading...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else if stats}
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-label">Total Study Time</div>
        <div class="stat-value">{formatMinutes(stats.total)}</div>
      </div>

      <div class="stat-item">
        <div class="stat-label">Average per Day</div>
        <div class="stat-value">
          {#if stats.datesList && stats.datesList.length > 0}
            {formatMinutes(Math.round(stats.total / stats.datesList.length))}
          {:else}
            {formatMinutes(0)}
          {/if}
        </div>
      </div>

      {#if examSession}
        <div class="stat-item">
          <div class="stat-label">Daily Target</div>
          <div class="stat-value">{formatMinutes(examSession.target_minutes)}</div>
        </div>
      {/if}
    </div>

    <div class="targets-section">
      {#if editingTarget && examSession}
        <div class="edit-form">
          <div class="form-group">
            <label for="target-input">Daily Target (minutes)</label>
            <input
              id="target-input"
              type="number"
              bind:value={editValue}
              min="1"
              placeholder="240"
            />
          </div>
          <div class="form-buttons">
            <button class="save-btn" on:click={updateTarget}>Save</button>
            <button class="cancel-btn" on:click={() => (editingTarget = false)}>Cancel</button>
          </div>
        </div>
      {/if}

      <div class="targets-section-header">
        <h4>Daily Stats</h4>
        {#if getTotalPages() > 1}
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

      <div class="targets-list">
        {#each paginatedDays as dateStr}
          <div class="target-item">
            <div class="target-left">
              <span class="day-name">{dateStr}</span>
              {#if stats.days[dateStr]}
                <span class="current-time">
                  {formatMinutes(stats.days[dateStr].total)} / {formatMinutes(examSession?.target_minutes || 240)}
                </span>
                <span class="difference" class:above={isAboveTarget(stats.days[dateStr].total, examSession?.target_minutes || 240)}>
                  {calculateDifference(stats.days[dateStr].total, examSession?.target_minutes || 240)}
                </span>
              {:else}
                <span class="current-time">0m / {formatMinutes(examSession?.target_minutes || 240)}</span>
                <span class="difference below">
                  {calculateDifference(0, examSession?.target_minutes || 240)}
                </span>
              {/if}
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill"
                class:above={stats.days[dateStr] && isAboveTarget(stats.days[dateStr].total, examSession?.target_minutes || 240)}
                style="width: {Math.min(100, (stats.days[dateStr]?.total || 0) / (examSession?.target_minutes || 240) * 100)}%"
              ></div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-top: 30px;
  }

  h3 {
    margin: 0 0 20px 0;
    font-size: 18px;
    color: #333;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .stat-item {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px;
    border-radius: 8px;
    text-align: center;
  }

  .stat-label {
    font-size: 12px;
    opacity: 0.9;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .stat-value {
    font-size: 24px;
    font-weight: bold;
  }

  .targets-section {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid #eee;
  }

  .targets-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    gap: 16px;
  }

  .targets-section-header h4 {
    margin: 0;
    font-size: 16px;
    color: #333;
  }

  .pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
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

  .edit-form {
    background: #fffacd;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    border-left: 4px solid #667eea;
  }

  .form-group {
    margin-bottom: 12px;
  }

  .form-group label {
    display: block;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 6px;
    color: #333;
  }

  .form-group input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  .form-group input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
  }

  .form-buttons {
    display: flex;
    gap: 8px;
  }

  .save-btn,
  .cancel-btn {
    flex: 1;
    padding: 8px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
  }

  .save-btn {
    background: #2ecc71;
    color: white;
  }

  .save-btn:hover {
    background: #27ae60;
  }

  .cancel-btn {
    background: #95a5a6;
    color: white;
  }

  .cancel-btn:hover {
    background: #7f8c8d;
  }

  .targets-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .target-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 6px;
    transition: background 0.2s ease;
  }

  .target-item:hover {
    background: #ecf0f1;
  }

  .target-left {
    display: flex;
    gap: 16px;
    align-items: center;
    justify-content: space-between;
  }

  .day-name {
    font-weight: 600;
    min-width: 80px;
    color: #333;
  }

  .current-time {
    font-size: 14px;
    color: #666;
  }

  .difference {
    font-size: 13px;
    font-weight: 600;
    color: #e74c3c;
    min-width: 50px;
    text-align: right;
  }

  .difference.above {
    color: #2ecc71;
  }

  .difference.below {
    color: #e74c3c;
  }

  .progress-bar {
    width: 100%;
    height: 6px;
    background: #ddd;
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    transition: width 0.3s ease;
  }

  .progress-fill.above {
    background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
  }

  .loading,
  .error {
    padding: 20px;
    text-align: center;
    border-radius: 6px;
  }

  .loading {
    background: #ecf0f1;
    color: #555;
  }

  .error {
    background: #fadbd8;
    color: #e74c3c;
  }
</style>
