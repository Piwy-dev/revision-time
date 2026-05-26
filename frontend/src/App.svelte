<script>
  import DailyChart from './components/DailyChart.svelte'
  import HourlyChart from './components/HourlyChart.svelte'
  import SessionForm from './components/SessionForm.svelte'
  import Stats from './components/Stats.svelte'
  import { onMount } from 'svelte'

  let showForm = false
  let selectedPeriod = 'week'
  let refreshKey = 0

  const periods = [
    { label: 'This Week', value: 'week' },
    { label: 'Last 7 Days', value: 'days7' },
    { label: 'This Month', value: 'month' },
    { label: 'All Time', value: 'all' },
  ]

  function getDateRange() {
    const end = new Date()
    let start = new Date()

    switch (selectedPeriod) {
      case 'week':
        // Monday to Sunday of current week
        start.setDate(end.getDate() - end.getDay() + 1)
        break
      case 'days7':
        start.setDate(end.getDate() - 6)
        break
      case 'month':
        start.setDate(1)
        break
      case 'all':
        start = new Date('2020-01-01')
        break
    }

    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0],
    }
  }

  function handleSessionAdded() {
    refreshKey++
    showForm = false
  }

  function toggleForm() {
    showForm = !showForm
  }
</script>

<div class="container">
  <header>
    <h1>📚 Study Tracker</h1>
    <button class="btn btn-primary" on:click={toggleForm}>
      {showForm ? '✕ Close' : '+ Add Session'}
    </button>
  </header>

  {#if showForm}
    <SessionForm onSessionAdded={handleSessionAdded} />
  {/if}

  <div class="controls">
    <div class="period-selector">
      <label for="period-select">Time Period:</label>
      <select id="period-select" bind:value={selectedPeriod}>
        {#each periods as period}
          <option value={period.value}>{period.label}</option>
        {/each}
      </select>
    </div>
  </div>

  <div key={refreshKey} class="charts-grid">
    <DailyChart dateRange={getDateRange()} />
    <HourlyChart dateRange={getDateRange()} />
  </div>

  <Stats dateRange={getDateRange()} />
</div>

<style>
  :global(body) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding-bottom: 40px;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  header {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }

  h1 {
    font-size: 28px;
    margin: 0;
  }

  .btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.3s ease;
  }

  .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  .controls {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .period-selector {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .period-selector label {
    font-weight: 600;
    color: #333;
  }

  .period-selector select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    background: white;
    cursor: pointer;
  }

  .period-selector select:hover {
    border-color: #667eea;
  }

  .charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 30px;
    margin-bottom: 30px;
  }

  @media (max-width: 768px) {
    header {
      flex-direction: column;
      gap: 20px;
    }

    .charts-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
