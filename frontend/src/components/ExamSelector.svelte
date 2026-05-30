<script>
  export let onExamCreated = () => {}
  export let onSelectExam = () => {}
  export let onClose = null
  export let examSessions = []

  let examName = ''
  let examDescription = ''
  let startDate = new Date().toISOString().split('T')[0]
  let endDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  let targetMinutes = 240  // Default 4 hours
  let loading = false
  let error = ''

  async function handleCreateExam() {
    if (!examName.trim()) {
      error = 'Exam name is required'
      return
    }

    if (new Date(endDate) <= new Date(startDate)) {
      error = 'End date must be after start date'
      return
    }

    if (!targetMinutes || targetMinutes <= 0) {
      error = 'Daily target must be greater than 0'
      return
    }

    loading = true
    error = ''

    try {
      const response = await fetch('/api/exam-sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: examName,
          description: examDescription,
          start_date: startDate,
          end_date: endDate,
          target_minutes: targetMinutes,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create exam session')
      }

      const newExam = await response.json()

      // Reset form
      examName = ''
      examDescription = ''
      startDate = new Date().toISOString().split('T')[0]
      endDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      targetMinutes = 240
      error = ''

      onExamCreated()
      onSelectExam(newExam)
    } catch (err) {
      error = err.message || 'Error creating exam session'
    } finally {
      loading = false
    }
  }
</script>

<div class="form-card">
  <div class="header-row">
    <h2>Create New Exam Session</h2>
    {#if onClose}
      <button class="close-btn" on:click={onClose}>✕</button>
    {/if}
  </div>
  
  <div class="form-group">
    <label for="exam-name">Exam Name</label>
    <input type="text" id="exam-name" placeholder="e.g., Math Final, Python Course" bind:value={examName} />
  </div>

  <div class="form-group">
    <label for="exam-desc">Description (optional)</label>
    <textarea id="exam-desc" placeholder="Add notes about this exam" bind:value={examDescription}></textarea>
  </div>

  <div class="form-row">
    <div class="form-group">
      <label for="start-date">Start Date</label>
      <input type="date" id="start-date" bind:value={startDate} />
    </div>
    <div class="form-group">
      <label for="end-date">End Date</label>
      <input type="date" id="end-date" bind:value={endDate} />
    </div>
  </div>

  <div class="form-group">
    <label for="target-minutes">Daily Study Target (minutes)</label>
    <input type="number" id="target-minutes" placeholder="240" bind:value={targetMinutes} min="1" />
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <button class="btn btn-primary" on:click={handleCreateExam} disabled={loading}>
    {loading ? 'Creating...' : 'Create Exam Session'}
  </button>

  {#if examSessions.length > 0}
    <div class="existing-sessions">
      <h3>Existing Sessions:</h3>
      <div class="sessions-list">
        {#each examSessions as exam}
          <button class="session-item" on:click={() => onSelectExam(exam)}>
            <div class="session-name">{exam.name}</div>
            <div class="session-dates">{exam.start_date} to {exam.end_date || 'Ongoing'}</div>
          </button>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .form-card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    margin-bottom: 24px;
  }

  h2 {
    font-size: 20px;
    margin: 0 0 20px 0;
    color: #333;
  }

  .header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .header-row h2 {
    margin: 0;
  }

  .close-btn {
    padding: 4px 8px;
    border: 1px solid #ddd;
    background: white;
    color: #666;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
    transition: all 0.2s ease;
    min-width: unset;
  }

  .close-btn:hover {
    background: #f5f5f5;
    border-color: #bbb;
    color: #333;
  }

  h3 {
    font-size: 16px;
    margin: 0;
    color: #555;
  }

  .form-group {
    margin-bottom: 16px;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
  }

  label {
    display: block;
    font-weight: 600;
    margin-bottom: 6px;
    color: #555;
    font-size: 14px;
  }

  input,
  textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    font-family: inherit;
  }

  textarea {
    resize: vertical;
    min-height: 80px;
  }

  input:focus,
  textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  .error {
    color: #e74c3c;
    background: #fadbd8;
    padding: 10px;
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 14px;
  }

  .btn {
    padding: 12px 24px;
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
    width: 100%;
  }

  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }

  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .existing-sessions {
    margin-top: 30px;
    padding-top: 24px;
    border-top: 1px solid #eee;
  }

  .sessions-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 12px;
  }

  .session-item {
    background: #f8f9fa;
    border: 1px solid #ddd;
    padding: 12px;
    border-radius: 6px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .session-item:hover {
    background: #ecf0f1;
    border-color: #667eea;
  }

  .session-name {
    font-weight: 600;
    color: #333;
    margin-bottom: 4px;
  }

  .session-dates {
    font-size: 12px;
    color: #999;
  }

  @media (max-width: 500px) {
    .form-row {
      grid-template-columns: 1fr;
    }
  }
</style>
