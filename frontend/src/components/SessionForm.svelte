<script>
  export let onSessionAdded = () => {}

  let date = new Date().toISOString().split('T')[0]
  let startTime = '09:00'
  let endTime = '10:00'
  let loading = false
  let error = ''

  async function handleSubmit() {
    if (!date || !startTime || !endTime) {
      error = 'Please fill in all fields'
      return
    }

    if (endTime <= startTime) {
      error = 'End time must be after start time'
      return
    }

    loading = true
    error = ''

    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date,
          start_time: startTime,
          end_time: endTime,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to add session')
      }

      // Reset form
      date = new Date().toISOString().split('T')[0]
      startTime = '09:00'
      endTime = '10:00'
      error = ''
      onSessionAdded()
    } catch (err) {
      error = err.message || 'Error adding session'
    } finally {
      loading = false
    }
  }
</script>

<div class="form-card">
  <h2>Add Study Session</h2>
  
  <div class="form-group">
    <label for="date">Date</label>
    <input type="date" id="date" bind:value={date} />
  </div>

  <div class="form-row">
    <div class="form-group">
      <label for="start">Start Time</label>
      <input type="time" id="start" bind:value={startTime} />
    </div>
    <div class="form-group">
      <label for="end">End Time</label>
      <input type="time" id="end" bind:value={endTime} />
    </div>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <button class="btn btn-primary" on:click={handleSubmit} disabled={loading}>
    {loading ? 'Adding...' : 'Add Session'}
  </button>
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

  input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
  }

  input:focus {
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

  @media (max-width: 500px) {
    .form-row {
      grid-template-columns: 1fr;
    }
  }
</style>
