<template>
  <div class="analytics-container">
    <div class="header-section">
      <h2>Performance Overview</h2>
      <button
        @click="exportQuizHistory"
        class="export-btn"
        :disabled="isExporting"
      >
        <span v-if="!isExporting">
          <i class="fas fa-file-export"></i> Export to CSV
        </span>
        <span v-else>
          <span class="spinner-border spinner-border-sm" role="status"></span>
          Exporting...
        </span>
      </button>
    </div>

    <div class="chart-grid">
      <div class="chart-card">
        <h3>Overall Progress</h3>
        <div class="chart-wrapper">
          <canvas ref="overviewChart"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <h3>Subject-wise Accuracy</h3>
        <div class="chart-wrapper">
          <canvas ref="subjectChart"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <h3>Recent Quiz Scores</h3>
        <div class="chart-wrapper">
          <canvas ref="timelineChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from "chart.js";
import axios from "axios";
Chart.register(...registerables);

export default {
  data() {
    return {
      performanceData: null,
      charts: {
        overview: null,
        subjects: null,
        timeline: null,
      },
      isExporting: false,
    };
  },
  async mounted() {
    await this.fetchData();
    this.renderCharts();
  },
  methods: {
    async fetchData() {
      try {
        const response = await axios.get("/student/performance", {
          headers: { Authorization: sessionStorage.getItem("token") },
        });
        this.performanceData = response.data;
      } catch (error) {
        console.error("Error fetching performance data:", error);
      }
    },

    async exportQuizHistory() {
      this.isExporting = true;
      try {
        const response = await axios.post(
          "/student/export",
          {},
          {
            headers: {
              Authorization: sessionStorage.getItem("token"),
            },
          }
        );

        // Handle successful response
        const successMessage =
          response.data?.message ||
          "Export started! You'll receive an email when ready.";
        this.$toast.success(successMessage);
      } catch (error) {
        // Completely safe error handling
        let errorMessage = "Export failed. Please try again later.";

        // First check if it's an Error object at all
        if (error instanceof Error) {
          // Check for Axios-specific error structure
          if (error.isAxiosError) {
            // Server responded with error status
            if (error.response) {
              errorMessage =
                error.response.data?.error ||
                error.response.data?.message ||
                error.response.statusText ||
                `Server error (${error.response.status})`;
            }
            // Request made but no response received
            else if (error.request) {
              errorMessage =
                "No response from server. Please check your network connection.";
            }
          }
          // Regular JavaScript Error
          else {
            errorMessage = error.message;
          }
        }

        this.$toast.error(errorMessage);
        console.error("Export error details:", {
          error: error,
          name: error?.name,
          message: error?.message,
          stack: error?.stack,
          response: error?.response?.data,
        });
      } finally {
        this.isExporting = false;
      }
    },

    renderCharts() {
      if (!this.performanceData) return;

      Object.values(this.charts).forEach((chart) => chart?.destroy());

      this.charts.overview = new Chart(this.$refs.overviewChart, {
        type: "doughnut",
        data: {
          labels: ["Correct Answers", "Incorrect Answers"],
          datasets: [
            {
              data: [
                this.performanceData.overview.total_correct,
                this.performanceData.overview.total_attempted -
                  this.performanceData.overview.total_correct,
              ],
              backgroundColor: ["#4CAF50", "#FF5252"],
            },
          ],
        },
      });

      this.charts.subjects = new Chart(this.$refs.subjectChart, {
        type: "bar",
        data: {
          labels: this.performanceData.subjects.map((s) => s.name),
          datasets: [
            {
              label: "Accuracy (%)",
              data: this.performanceData.subjects.map((s) => s.accuracy),
              backgroundColor: "#2196F3",
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
            },
          },
        },
      });

      if (this.performanceData.recent_attempts?.length > 0) {
        this.charts.timeline = new Chart(this.$refs.timelineChart, {
          type: "line",
          data: {
            labels: this.performanceData.recent_attempts.map(
              (a) => `${a.chapter} (${a.date})`
            ),
            datasets: [
              {
                label: "Score %",
                data: this.performanceData.recent_attempts.map(
                  (a) => a.percentage
                ),
                borderColor: "#FF9800",
                backgroundColor: "rgba(255, 152, 0, 0.1)",
                fill: true,
                tension: 0.1,
              },
            ],
          },
          options: {
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
              },
            },
          },
        });
      } else {
        this.$refs.timelineChart.innerHTML =
          '<p class="no-data">No quiz attempts yet</p>';
      }
    },
  },
  beforeUnmount() {
    Object.values(this.charts).forEach((chart) => chart?.destroy());
  },
};
</script>

<style scoped>
.analytics-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.export-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.3s;
}

.export-btn:hover {
  background-color: #3e8e41;
}

.export-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-wrapper {
  position: relative;
  height: 300px;
}

h3 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.spinner-border {
  margin-right: 0.5rem;
}
</style>
