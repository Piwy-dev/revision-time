<script>
  import { onMount } from 'svelte'

  export let dateRange = { start: '', end: '' }

  let stats = null
  let targets = {}
  let loading = true
  let error = ''
  let editingDay = null
  let editValue = 0

  const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

  async function fetchStats() {
    try {
      loading = true
      error = ''
      
      // Fetch daily stats
      const statsResponse = await fetch(
        `/api/stats/daily?start_date=${dateRange.start}&end_date=${dateRange.end}`
      )
      if (!statsResponse.ok) throw new Error('Failed to fetch stats')
      const statsData = await statsResponse.json()
      
      // Aggregate stats
      const aggregated = { total: 0, days: {} }
      statsData.forEach((d) => {
        aggregated.total += d.total_minutes
        if (!aggregated.days[d.day_of_week]) {
          aggregated.days[d.day_of_week] = { total: 0, target: d.target_minutes }
        }
        aggregated.days[d.day_of_week].total += d.total_minutes
      })
      stats = aggregated

      // Fetch targets
      const targetsResponse = await fetch('/api/targets')
      if (!targetsResponse.ok) throw new Error('Failed to fetch targets')
      const targetsData = await targetsResponse.json()
      targetsData.forEach((t) => {
        targets[t.day_of_week] = t.target_minutes
      })
      targets = targets
    } catch (err) {
      error = err.message || 'Error loading stats'
    } finally {
      loading = false
    }
  }

  async function updateTarget(day) {
    try {
      const response = await fetch(`/api/target/${day}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_minutes: editValue }),
      })
      if (!response.ok) throw new Error('Failed to update target')
      targets[day] = editValue
      targets = targets
      editingDay = null
    } catch (err) {
      error = err.message || 'Error updating target'
    }
  }

  function formatMinutes(minutes) {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}h ${mins}m`
  }

  $: dateRange && fetchStats()

  onMount(() => {
    fetchStats()
  })
</script>

<div class="card">
  <h3>Statistics</h3>

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
    </div>

    <div class="targets-section">
      <h4>Daily Targets</h4>
      <div class="targets-list">
        {#each dayNames as day, index}
          <div class="target-item">
            <div class="target-left">
              <span class="day-name">{day}</span>
              {#if stats.days[index]}
                <span class="current-time">
                  {formatMinutes(stats.days[index].total)} / {formatMinutes(targets[index] || 240)}
                </span>
              {:else}
                <span class="current-time">0m / {formatMinutes(targets[index] || 240)}</span>
              {/if}
            </div>
            <button
              class="edit-btn"
              on:click={() => {
                editingDay = index
                editValue = targets[index] || 240
              }}
            >
              ⚙️
            </button>
          </div>

          {#if editingDay === index}
            <div class="edit-form">
              <input
                type="number"
                bind:value={editValue}
                min="0"
                step="15"
                placeholder="Minutes"
              />
              <button class="save-btn" on:click={() => updateTarget(index)}>Save</button>
              <button class="cancel-btn" on:click={() => (editingDay = null)}>Cancel</button>
            </div>
          {/if}
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
    margin: 0 0 16px 0;
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

  .targets-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .target-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 6px;
    transition: background 0.2s ease;
  }

  .target-item:hover {
    background: #ecf0f1;
  }

  .target-left {
    flex: 1;
    display: flex;
    gap: 16px;
    align-items: center;
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

  .edit-btn {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 4px;
    transition: background 0.2s ease;
  }

  .edit-btn:hover {
    background: #ddd;
  }

  .edit-form {
    display: flex;
    gap: 8px;
    padding: 8px 12px;
    background: white;
    border-left: 3px solid #667eea;
    margin: 4px 12px;
    border-radius: 4px;
  }

  .edit-form input {
    flex: 1;
    padding: 6px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  .edit-form input:focus {
    outline: none;
    border-color: #667eea;
  }

  .save-btn,
  .cancel-btn {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
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
