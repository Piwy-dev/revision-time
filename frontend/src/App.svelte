<script>
  import DailyChart from './components/DailyChart.svelte'
  import HourlyChart from './components/HourlyChart.svelte'
  import WeeklyHourlyChart from './components/WeeklyHourlyChart.svelte'
  import SessionForm from './components/SessionForm.svelte'
  import Stats from './components/Stats.svelte'
  import ExamSelector from './components/ExamSelector.svelte'
  import SessionsList from './components/SessionsList.svelte'
  import ExamSessionManager from './components/ExamSessionManager.svelte'
  import { onMount } from 'svelte'

  let showForm = false
  let showSessionsList = false
  let showExamManager = false
  let selectedPeriod = 'week'
  let selectedExamSession = null
  let selectedExamSessionId = null
  let examSessions = []
  let showExamCreator = false
  let refreshKey = 0

  const periods = [
    { label: 'This Week', value: 'week' },
    { label: 'Last 7 Days', value: 'days7' },
    { label: 'This Month', value: 'month' },
    { label: 'All Time', value: 'all' },
  ]

  async function loadExamSessions() {
    try {
      const response = await fetch('/api/exam-sessions')
      if (!response.ok) throw new Error('Failed to load exam sessions')
      examSessions = await response.json()
      
      // Try to restore previously selected exam from localStorage
      if (!selectedExamSession && selectedExamSessionId) {
        const restored = examSessions.find(e => e.id === selectedExamSessionId)
        if (restored) {
          selectedExamSession = restored
          return
        }
      }
      
      // Preserve currently selected exam session if it still exists
      if (selectedExamSession) {
        const stillExists = examSessions.find(e => e.id === selectedExamSession.id)
        if (stillExists) {
          selectedExamSession = stillExists
          return
        }
      }
      
      // Select first exam session if none selected
      if (examSessions.length > 0) {
        selectedExamSession = examSessions[0]
      }
    } catch (err) {
      console.error('Error loading exam sessions:', err)
    }
  }

  function getDateRange() {
    const end = new Date()
    let start = new Date()

    switch (selectedPeriod) {
      case 'week':
        start.setDate(end.getDate() - end.getDay() + 1)
        break
      case 'days7':
        start.setDate(end.getDate() - 6)
        break
      case 'month':
        start.setDate(1)
        break
      case 'all':
        start = new Date(selectedExamSession?.start_date || '2020-01-01')
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

  function handleExamCreated() {
    loadExamSessions()
    showExamCreator = false
    refreshKey++
  }

  function handleExamUpdated(exam) {
    // Reload sessions in case exam dates changed
    refreshKey++
  }

  function handleExamDeleted(exam) {
    // If deleted exam was selected, select first remaining exam
    loadExamSessions()
    refreshKey++
  }

  function toggleForm() {
    showForm = !showForm
  }

  // Save selected exam session ID to localStorage whenever it changes
  $: if (selectedExamSession?.id) {
    localStorage.setItem('selectedExamSessionId', selectedExamSession.id)
    refreshKey++
  }

  onMount(() => {
    // Load previously selected exam session ID from localStorage
    const savedId = localStorage.getItem('selectedExamSessionId')
    if (savedId) {
      selectedExamSessionId = parseInt(savedId)
    }
    loadExamSessions()
  })

</script>

<div class="container">
  <header>
    <h1>📚 Study Tracker</h1>
    <div class="header-controls">
      {#if selectedExamSession}
        <div class="exam-info">
          <span class="exam-badge">{selectedExamSession.name}</span>
        </div>
      {/if}
      <button class="btn btn-secondary" on:click={() => { showExamManager = !showExamManager; showExamCreator = false; showSessionsList = false; showForm = false }}>
        ⚙️ Manage
      </button>
      <button class="btn btn-secondary" on:click={() => showExamCreator = !showExamCreator}>
        + New Exam
      </button>
      <button class="btn btn-primary" on:click={() => { showSessionsList = !showSessionsList; showForm = false }}>
        📋 Sessions
      </button>
      <button class="btn btn-primary" on:click={toggleForm}>
        + Add Session
      </button>
    </div>
  </header>

  {#if showExamCreator}
    <ExamSelector onExamCreated={handleExamCreated} onSelectExam={(exam) => selectedExamSession = exam} bind:examSessions onClose={() => showExamCreator = false} />
  {/if}

  {#if showExamManager}
    <ExamSessionManager {examSessions} onExamUpdated={handleExamUpdated} onExamDeleted={handleExamDeleted} onClose={() => showExamManager = false} />
  {/if}

  {#if showSessionsList && selectedExamSession}
    <SessionsList examSessionId={selectedExamSession.id} dateRange={getDateRange()} onClose={() => showSessionsList = false} />
  {/if}

  {#if showForm && selectedExamSession}
    <SessionForm examSessionId={selectedExamSession.id} onSessionAdded={handleSessionAdded} onClose={() => showForm = false} />
  {/if}

  {#if !selectedExamSession}
    <div class="empty-state">
      <h2>📕 No Exam Sessions Yet</h2>
      <p>Create your first exam session to start tracking study time.</p>
      <button class="btn btn-primary" on:click={() => showExamCreator = true}>
        + Create Exam Session
      </button>
    </div>
  {:else}
    <div class="controls">
      <div class="period-selector">
        <label for="period-select">Time Period:</label>
        <select id="period-select" bind:value={selectedPeriod}>
          {#each periods as period}
            <option value={period.value}>{period.label}</option>
          {/each}
        </select>
      </div>
      <div class="exam-selector">
        <label for="exam-select">Exam Session:</label>
        <select id="exam-select" bind:value={selectedExamSession}>
          {#each examSessions as exam}
            <option value={exam}>{exam.name}</option>
          {/each}
        </select>
      </div>
    </div>

    <WeeklyHourlyChart examSessionId={selectedExamSession.id} dateRange={getDateRange()} />

    <!-- Hidden for now
    <div key={refreshKey} class="charts-grid">
      <DailyChart examSessionId={selectedExamSession.id} dateRange={getDateRange()} />
      <HourlyChart examSessionId={selectedExamSession.id} dateRange={getDateRange()} />
    </div>
    -->

    <Stats examSessionId={selectedExamSession.id} examSession={selectedExamSession} dateRange={getDateRange()} />
  {/if}
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
    padding: 20px 30px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    flex-wrap: wrap;
    gap: 20px;
  }

  h1 {
    font-size: 28px;
    margin: 0;
  }

  .header-controls {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .exam-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .exam-badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
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

  .btn-secondary {
    background: white;
    color: #667eea;
    border: 2px solid #667eea;
  }

  .btn-secondary:hover {
    background: #667eea;
    color: white;
  }

  .empty-state {
    background: white;
    padding: 60px 30px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
  }

  .empty-state h2 {
    font-size: 24px;
    margin: 0 0 12px 0;
    color: #333;
  }

  .empty-state p {
    font-size: 16px;
    color: #666;
    margin: 0 0 20px 0;
  }

  .controls {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    align-items: center;
  }

  .period-selector,
  .exam-selector {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .period-selector label,
  .exam-selector label {
    font-weight: 600;
    color: #333;
  }

  .period-selector select,
  .exam-selector select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    background: white;
    cursor: pointer;
  }

  .period-selector select:hover,
  .exam-selector select:hover {
    border-color: #667eea;
  }

  .charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 30px;
    margin-top: 30px;
    margin-bottom: 30px;
  }

  @media (max-width: 768px) {
    header {
      flex-direction: column;
      gap: 12px;
    }

    .header-controls {
      flex-direction: column;
      width: 100%;
    }

    .header-controls button {
      width: 100%;
    }

    .controls {
      flex-direction: column;
    }

    .period-selector,
    .exam-selector {
      width: 100%;
    }

    .period-selector select,
    .exam-selector select {
      flex: 1;
    }

    .charts-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
