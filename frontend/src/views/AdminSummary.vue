<template>
  <div class="admin-dashboard">
    <h1>Admin Dashboard</h1>

    <div class="stats-grid">
      <!-- Quick Stats Cards -->
      <div class="stat-card">
        <h3>Total Students</h3>
        <div class="stat-value">{{ overview.students }}</div>
      </div>
      <div class="stat-card">
        <h3>Total Quizzes</h3>
        <div class="stat-value">{{ overview.quizzes }}</div>
      </div>
      <div class="stat-card">
        <h3>Avg. Score</h3>
        <div class="stat-value">{{ overview.avg_percentage }}%</div>
      </div>
    </div>

    <!-- Charts Grid -->
    <div class="charts-grid">
      <!-- Subject Performance -->
      <div class="chart-card">
        <h3>Subject Performance</h3>
        <canvas ref="subjectChart"></canvas>
      </div>

      <!-- Quiz Distribution -->
      <div class="chart-card">
        <h3>Quiz Distribution</h3>
        <canvas ref="quizChart"></canvas>
      </div>

      <!-- Recent Activity Table -->
      <div class="chart-card">
        <h3>Recent Activity</h3>
        <table class="activity-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Quiz</th>
              <th>Score</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="activity in recent_activity" :key="activity.timestamp">
              <td>User #{{ activity.user_id }}</td>
              <td>Quiz #{{ activity.quiz_id }}</td>
              <td>{{ activity.score }}/{{ activity.total }}</td>
              <td>{{ formatDate(activity.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";
import axios from "axios";

export default {
  data() {
    return {
      overview: {},
      subjects: [],
      recent_activity: [],
    };
  },
  async mounted() {
    await this.fetchData();
    this.renderCharts();
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get("/admin/dashboard-stats", {
          headers: { Authorization: sessionStorage.getItem("token") },
        });
        this.overview = response.data.overview;
        this.subjects = response.data.subjects;
        this.recent_activity = response.data.recent_activity;
      } catch (error) {
        console.error("Error fetching admin stats:", error);
      }
    },

    renderCharts() {
      // Subject Performance Chart
      new Chart(this.$refs.subjectChart, {
        type: "bar",
        data: {
          labels: this.subjects.map((s) => s.name),
          datasets: [
            {
              label: "Average Score %",
              data: this.subjects.map((s) => s.avg_score),
              backgroundColor: "#4CAF50",
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: { beginAtZero: true, max: 100 },
          },
        },
      });

      // Quiz Distribution Chart
      new Chart(this.$refs.quizChart, {
        type: "doughnut",
        data: {
          labels: this.subjects.map((s) => s.name),
          datasets: [
            {
              label: "Quizzes per Subject",
              data: this.subjects.map((s) => s.quizzes),
              backgroundColor: [
                "#2196F3",
                "#4CAF50",
                "#FF9800",
                "#9C27B0",
                "#E91E63",
                "#607D8B",
              ],
            },
          ],
        },
      });
    },

    formatDate(isoString) {
      return new Date(isoString).toLocaleDateString();
    },
  },
};
</script>

<style scoped>
.admin-dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #2196f3;
  margin-top: 0.5rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 400px;
}

.activity-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.activity-table th,
.activity-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.activity-table th {
  background-color: #f8f9fa;
}
</style>
