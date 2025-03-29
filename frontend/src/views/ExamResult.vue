<template>
  <div class="result-container">
    <h1>Exam Results</h1>
    <div class="score-card">
      <div class="score-header">
        <h2>{{ score.quiz.chapter.name }}</h2>
        <p>{{ score.timestamp }}</p>
      </div>
      <div class="score-body">
        <div class="score-item">
          <span>Correct Answers</span>
          <span class="score-value">{{ score.total_scored }}</span>
        </div>
        <div class="score-item">
          <span>Total Questions</span>
          <span class="score-value">{{ score.total_questions }}</span>
        </div>
        <div class="score-item highlight">
          <span>Percentage</span>
          <span class="score-value">{{ percentage }}%</span>
        </div>
      </div>
      <button @click="$router.push('/student/dashboard')" class="return-btn">
        Return to Dashboard
      </button>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      score: {
        quiz: {
          chapter: {
            name: "",
          },
        },
        total_scored: 0,
        total_questions: 0,
        timestamp: "",
      },
    };
  },
  computed: {
    percentage() {
      return (
        (this.score.total_scored / this.score.total_questions) *
        100
      ).toFixed(1);
    },
  },
  async created() {
    await this.fetchResults();
  },
  methods: {
    async fetchResults() {
      try {
        const response = await axios.get(
          `http://127.0.0.1:5000/student/results/${this.$route.params.quizId}`,
          { headers: { Authorization: sessionStorage.getItem("token") } }
        );
        this.score = response.data;
      } catch (error) {
        console.error("Error fetching results:", error);
      }
    },
  },
};
</script>

<style scoped>
.result-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 20px;
}

.score-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.score-header {
  text-align: center;
  margin-bottom: 25px;
}

.score-body {
  display: grid;
  gap: 20px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.highlight {
  background: #e3f2fd;
  font-weight: bold;
}

.score-value {
  color: #007bff;
}

.return-btn {
  margin-top: 25px;
  width: 100%;
  padding: 12px;
  background: #28a745;
  color: white;
}
</style>
