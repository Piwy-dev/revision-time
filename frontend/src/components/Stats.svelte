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

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

  async function fetchStats() {
    if (!examSessionId) return

    try {
      loading = true
      error = ''
      
      // Fetch daily stats
      const statsResponse = await fetch(
        `/api/stats/daily?exam_session_id=${examSessionId}&start_date=${dateRange.start}&end_date=${dateRange.end}`
      )
      if (!statsResponse.ok) throw new Error('Failed to fetch stats')
      const statsData = await statsResponse.json()
      
      // Aggregate stats by day of week
      const aggregated = { total: 0, days: {} }
      statsData.forEach((d) => {
        aggregated.total += d.total_minutes
        if (!aggregated.days[d.day_of_week]) {
          aggregated.days[d.day_of_week] = { total: 0 }
        }
        aggregated.days[d.day_of_week].total += d.total_minutes
      })
      stats = aggregated
    } catch (err) {
      error = err.message || 'Error loading stats'
    } finally {
      loading = false
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

  $: examSessionId && dateRange && fetchStats()

  onMount(() => {
    if (examSessionId) fetchStats()
  })
</script>

<div class="card">
  <h3>📊 Statistics (last 7 days)</h3>

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
          {formatMinutes(Math.round(stats.total / 7))}
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

      <div class="targets-list">
        {#each dayNames as day, index}
          <div class="target-item">
            <div class="target-left">
              <span class="day-name">{day}</span>
              {#if stats.days[index]}
                <span class="current-time">
                  {formatMinutes(stats.days[index].total)} / {formatMinutes(examSession?.target_minutes || 240)}
                </span>
              {:else}
                <span class="current-time">0m / {formatMinutes(examSession?.target_minutes || 240)}</span>
              {/if}
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                style="width: {Math.min(100, (stats.days[index]?.total || 0) / (examSession?.target_minutes || 240) * 100)}%"
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
  }

  h3 {
    margin: 0 0 20px 0;
    font-size: 18px;
    color: #333;
  }

  h4 {
    margin: 0;
    font-size: 16px;
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
