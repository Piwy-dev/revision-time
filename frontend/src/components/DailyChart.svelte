<script>
  import { onMount } from 'svelte'
  import { Chart, registerables } from 'chart.js'

  Chart.register(...registerables)

  export let examSessionId = null
  export let dateRange = { start: '', end: '' }

  let canvas
  let chart
  let data = []
  let loading = true
  let error = ''

  async function fetchData() {
    if (!examSessionId) return

    try {
      loading = true
      error = ''
      const response = await fetch(
        `/api/stats/daily?exam_session_id=${examSessionId}&start_date=${dateRange.start}&end_date=${dateRange.end}`
      )
      if (!response.ok) throw new Error('Failed to fetch data')
      data = await response.json()
    } catch (err) {
      error = err.message || 'Error loading data'
    } finally {
      loading = false
    }
  }

  function renderChart() {
    if (!canvas || !data.length) return

    const labels = data.map((d) => {
      const date = new Date(d.date + 'T00:00:00')
      return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    })

    const totalMinutes = data.map((d) => d.total_minutes)
    const targetMinutes = data.map((d) => d.target_minutes)

    if (chart) chart.destroy()

    chart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Study Time (minutes)',
            data: totalMinutes,
            backgroundColor: 'rgba(102, 126, 234, 0.8)',
            borderColor: 'rgba(102, 126, 234, 1)',
            borderWidth: 1,
            borderRadius: 6,
          },
          {
            label: 'Daily Target',
            data: targetMinutes,
            borderColor: 'rgba(46, 204, 113, 1)',
            borderWidth: 2,
            fill: false,
            type: 'line',
            tension: 0.4,
            pointBackgroundColor: 'rgba(46, 204, 113, 1)',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: 'Daily Study Time',
            font: { size: 16, weight: 'bold' },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Minutes',
            },
          },
        },
      },
    })
  }

  $: examSessionId && dateRange && fetchData()
  $: data && renderChart()

  onMount(() => {
    if (examSessionId) fetchData()
  })
</script>

<div class="card">
  <h3>Daily Study Time</h3>
  {#if loading}
    <div class="loading">Loading...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <div class="chart-container">
      <canvas bind:this={canvas}></canvas>
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
    margin: 0 0 16px 0;
    font-size: 18px;
    color: #333;
  }

  .chart-container {
    position: relative;
    height: 400px;
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
