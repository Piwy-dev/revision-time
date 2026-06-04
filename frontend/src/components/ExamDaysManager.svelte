<script>
  import { onMount } from 'svelte'

  export let examSessionId = null

  let examDays = []
  let loading = false
  let newExamDate = getTodayDate()
  let error = ''
  let success = ''

  function getTodayDate() {
    const today = new Date()
    return today.toISOString().split('T')[0]
  }

  async function loadExamDays() {
    if (!examSessionId) return

    try {
      loading = true
      const response = await fetch(`/api/exam-days?exam_session_id=${examSessionId}`)
      if (!response.ok) throw new Error('Failed to load exam days')
      examDays = await response.json()
    } catch (err) {
      error = err.message || 'Error loading exam days'
    } finally {
      loading = false
    }
  }

  async function addExamDay() {
    if (!newExamDate) {
      error = 'Please select a date'
      return
    }

    try {
      error = ''
      success = ''
      const response = await fetch('/api/exam-days', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exam_session_id: examSessionId,
          date: newExamDate,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to add exam day')
      }

      success = 'Exam day added!'
      newExamDate = ''
      await loadExamDays()
      setTimeout(() => (success = ''), 3000)
    } catch (err) {
      error = err.message || 'Error adding exam day'
    }
  }

  async function deleteExamDay(id) {
    if (!confirm('Remove this exam day?')) return

    try {
      error = ''
      const response = await fetch(`/api/exam-days/${id}`, { method: 'DELETE' })
      if (!response.ok) throw new Error('Failed to remove exam day')
      await loadExamDays()
    } catch (err) {
      error = err.message || 'Error removing exam day'
    }
  }

  $: examSessionId && loadExamDays()

  onMount(() => {
    if (examSessionId) loadExamDays()
  })
</script>

<div class="card">
  <h3>📚 Exam Days</h3>

  {#if error}
    <div class="error">{error}</div>
  {/if}
  {#if success}
    <div class="success">{success}</div>
  {/if}

  <div class="form-group">
    <label for="exam-date">Mark a date as exam day:</label>
    <input type="date" id="exam-date" bind:value={newExamDate} />
    <button on:click={addExamDay}>Add Exam Day</button>
  </div>

  {#if loading}
    <div class="loading">Loading exam days...</div>
  {:else if examDays.length === 0}
    <p class="no-data">No exam days marked yet</p>
  {:else}
    <div class="exam-days-list">
      {#each examDays as day (day.id)}
        <div class="exam-day-item">
          <span class="date">
            {new Date(day.date + 'T00:00:00').toLocaleDateString('en-US', {
              weekday: 'short',
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })}
          </span>
          <button class="delete-btn" on:click={() => deleteExamDay(day.id)}>Remove</button>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .card {
    background: white;
    padding: 24px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-top: 20px;
  }

  h3 {
    margin: 0 0 16px 0;
    font-size: 18px;
    color: #333;
  }

  .form-group {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    align-items: flex-end;
  }

  label {
    font-size: 14px;
    color: #666;
    display: block;
    margin-bottom: 4px;
  }

  input[type='date'] {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
  }

  button {
    padding: 8px 16px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s;
  }

  button:hover {
    background: #5568d3;
  }

  .delete-btn {
    padding: 4px 8px;
    font-size: 12px;
    background: #e74c3c;
  }

  .delete-btn:hover {
    background: #c0392b;
  }

  .error {
    background: #fadbd8;
    color: #e74c3c;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 14px;
  }

  .success {
    background: #d5f4e6;
    color: #27ae60;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 14px;
  }

  .loading {
    text-align: center;
    color: #999;
    padding: 20px;
  }

  .no-data {
    text-align: center;
    color: #999;
    padding: 20px;
    margin: 0;
  }

  .exam-days-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .exam-day-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: #f9f9f9;
    border-left: 4px solid #ffc107;
    border-radius: 4px;
  }

  .date {
    font-weight: 500;
    color: #333;
  }
</style>
