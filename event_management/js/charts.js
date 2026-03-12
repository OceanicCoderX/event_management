// Chart.js helper functions

function drawParticipantsChart(labels, data) {
  const ctx = document.getElementById('participantsChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Participants',
        data,
        backgroundColor: 'rgba(123, 47, 190, 0.8)',
        borderColor: '#7B2FBE',
        borderWidth: 2,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `Participants: ${ctx.raw}`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1, color: '#666' },
          grid: { color: 'rgba(0,0,0,0.05)' }
        },
        x: {
          ticks: { color: '#666', maxRotation: 30 },
          grid: { display: false }
        }
      }
    }
  });
}

function drawStatusChart(data) {
  const ctx = document.getElementById('statusChart');
  if (!ctx) return;
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Pending', 'Approved', 'Rejected'],
      datasets: [{
        data: [data.Pending || 0, data.Approved || 0, data.Rejected || 0],
        backgroundColor: ['#FFB400', '#28A745', '#DC3545'],
        borderWidth: 0,
        hoverOffset: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: { padding: 15, font: { family: 'Inter' } }
        }
      },
      cutout: '65%'
    }
  });
}

function drawLineChart(canvasId, labels, data, label = 'Registrations') {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label,
        data,
        borderColor: '#7B2FBE',
        backgroundColor: 'rgba(123, 47, 190, 0.1)',
        borderWidth: 2,
        pointBackgroundColor: '#7B2FBE',
        pointRadius: 5,
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
        x: { grid: { display: false } }
      }
    }
  });
}

function drawVotesBarChart(canvasId, labels, data) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Votes Received',
        data,
        backgroundColor: [
          'rgba(255, 180, 0, 0.8)',
          'rgba(192, 192, 192, 0.8)',
          'rgba(205, 127, 50, 0.8)',
          'rgba(123, 47, 190, 0.8)',
          'rgba(40, 167, 69, 0.8)'
        ],
        borderWidth: 0,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
        x: { grid: { display: false } }
      }
    }
  });
}
