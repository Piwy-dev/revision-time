<script>
  import { onMount } from 'svelte'
  import { Chart, registerables } from 'chart.js'

  Chart.register(...registerables)

  export let examSessionId = null
  export let dateRange = { start: '', end: '' }

  let canvas
  let chart
  let loading = true
  let error = ''

  const dayColors = [
    'rgba(255, 99, 132, 1)',    // Red
    'rgba(54, 162, 235, 1)',    // Blue
    'rgba(75, 192, 192, 1)',    // Teal
    'rgba(255, 206, 86, 1)',    // Yellow
    'rgba(153, 102, 255, 1)',   // Purple
    'rgba(255, 159, 64, 1)',    // Orange
    'rgba(201, 203, 207, 1)',   // Gray
  ]

  function formatDate(dateString) {
    const [year, month, day] = dateString.split('-')
    return `${day}/${month}/${year}`
  }

  async function fetchAndProcessData() {
    if (!examSessionId) return

    try {
      loading = true
      error = ''

      // Calculate the actual last 7 days (not week boundaries)
      const today = new Date()
      const sevenDaysAgo = new Date(today)
      sevenDaysAgo.setDate(today.getDate() - 6)
      
      const startDate = sevenDaysAgo.toISOString().split('T')[0]
      const endDate = today.toISOString().split('T')[0]

      // Fetch daily stats for last 7 days
      const statsResponse = await fetch(
        `/api/stats/daily?exam_session_id=${examSessionId}&start_date=${startDate}&end_date=${endDate}`
      )
      if (!statsResponse.ok) throw new Error('Failed to fetch stats')
      const statsData = await statsResponse.json()

      // Keep all data (already last 7 days)
      const last7Days = statsData

      // For each day, we need to fetch the sessions and calculate cumulative minutes by hour
      const dayDataPromises = last7Days.map(async (dayStats) => {
        const date = dayStats.date
        const dayOfWeek = dayStats.day_of_week

        // Get all sessions for this day (use same date for start and end)
        const sessionsResponse = await fetch(
          `/api/sessions?exam_session_id=${examSessionId}&start_date=${date}&end_date=${date}`
        )
        if (!sessionsResponse.ok) throw new Error('Failed to fetch sessions')
        const sessions = await sessionsResponse.json()

        // Calculate cumulative minutes for each hour (0-23)
        const hourlyData = new Array(24).fill(0)
        sessions.forEach((session) => {
          const [startHour, startMin] = session.start_time.split(':').map(Number)
          const [endHour, endMin] = session.end_time.split(':').map(Number)

          // Distribute minutes across hours
          if (startHour === endHour) {
            hourlyData[startHour] += session.duration_minutes
          } else {
            // Minutes in start hour
            hourlyData[startHour] += 60 - startMin
            // Full hours between
            for (let h = startHour + 1; h < endHour; h++) {
              hourlyData[h] += 60
            }
            // Minutes in end hour
            hourlyData[endHour] += endMin
          }
        })

        // Convert to cumulative data
        let cumulative = 0
        const cumulativeData = hourlyData.map((minutes) => {
          cumulative += minutes
          return cumulative
        })

        return {
          dayOfWeek,
          date,
          targetMinutes: dayStats.target_minutes,
          cumulativeData,
        }
      })

      const dayDataArray = await Promise.all(dayDataPromises)
      renderChart(dayDataArray)
    } catch (err) {
      error = err.message || 'Error loading data'
    } finally {
      loading = false
    }
  }

  function renderChart(dayDataArray) {
    if (!canvas) return

    const labels = Array.from({ length: 24 }, (_, i) => `${i}:00`)

    const datasets = dayDataArray.map((dayData, index) => ({
      label: formatDate(dayData.date),
      data: dayData.cumulativeData,
      borderColor: dayColors[index % dayColors.length],
      backgroundColor: dayColors[index % dayColors.length].replace('1)', '0.1)'),
      borderWidth: 2,
      fill: false,
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: dayColors[index % dayColors.length],
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointHoverRadius: 6,
    }))

    // Add a target line (horizontal at daily target)
    datasets.push({
      label: 'Daily Target',
      data: Array.from({ length: 24 }, (_, i) => {
        const dailyTarget = dayDataArray.length > 0 ? dayDataArray[0].targetMinutes : 0
        return dailyTarget
      }),
      borderColor: 'rgba(46, 204, 113, 1)',
      borderWidth: 2,
      fill: false,
      tension: 0.4,
      pointBackgroundColor: 'rgba(46, 204, 113, 1)',
      pointRadius: 3,
      borderDash: [5, 5],
    })

    if (chart) chart.destroy()

    chart = new Chart(canvas, {
      type: 'line',
      data: {
        labels,
        datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 15,
            },
          },
          title: {
            display: true,
            text: 'Cumulative Study Time (Last 7 Days)',
            font: { size: 16, weight: 'bold' },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Hour of Day',
              font: { weight: 'bold' },
            },
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Cumulative Minutes Studied',
              font: { weight: 'bold' },
            },
          },
        },
      },
    })
  }

  $: if (examSessionId) fetchAndProcessData()

  onMount(() => {
    if (examSessionId) fetchAndProcessData()
  })
</script>

<div class="card">
  <h3>📈 Cumulative Study Time (Last 7 Days)</h3>
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
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    grid-column: 1 / -1;
  }

  h3 {
    margin: 0 0 15px 0;
    font-size: 16px;
    color: #333;
  }

  .chart-container {
    position: relative;
    width: 100%;
    height: 600px;
  }

  .loading {
    text-align: center;
    padding: 20px;
    color: #666;
    background: #f5f5f5;
    border-radius: 8px;
  }

  .error {
    text-align: center;
    padding: 20px;
    color: #c00;
    background: #fee;
    border-radius: 8px;
  }
</style>
