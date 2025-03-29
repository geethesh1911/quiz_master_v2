<template>
  <div class="student-dashboard">
    <h1>Available Quizzes</h1>

    <div class="quiz-grid">
      <div v-for="quiz in quizzes" :key="quiz.id" class="quiz-card">
        <div class="quiz-header">
          <h3>
            {{ quiz.subject }} - {{ quiz.chapter }}
            <span v-if="isQuizTaken(quiz.id)" class="completed-badge">✓</span>
          </h3>
        </div>

        <div class="quiz-details">
          <div class="detail-item">
            <span>Questions:</span>
            <span>{{ quiz.total_questions }}</span>
          </div>
          <div class="detail-item">
            <span>Duration:</span>
            <span>{{ quiz.duration }} mins</span>
          </div>
          <div class="detail-item">
            <span>Scheduled Date:</span>
            <span>{{ formatDate(quiz.date) }}</span>
          </div>
        </div>

        <button
          @click="handleQuizAction(quiz.id)"
          :class="[
            'quiz-button',
            isQuizTaken(quiz.id) ? 'results-button' : 'take-test-button',
          ]"
        >
          {{ isQuizTaken(quiz.id) ? "Show Results" : "Take Test" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      quizzes: [],
      results: [],
    };
  },
  async created() {
    await this.fetchQuizzes();
    await this.fetchResults();
  },
  methods: {
    async fetchQuizzes() {
      try {
        const response = await axios.get(
          "http://localhost:5000/student/quizzes/available",
          {
            headers: { Authorization: sessionStorage.getItem("token") },
          }
        );
        this.quizzes = response.data.map((quiz) => ({
          ...quiz,
          date: new Date(quiz.date_of_quiz).toLocaleDateString(),
        }));
      } catch (error) {
        console.error("Error fetching quizzes:", error);
      }
    },
    async fetchResults() {
      try {
        const response = await axios.get(
          "http://localhost:5000/student/results",
          {
            headers: { Authorization: sessionStorage.getItem("token") },
          }
        );
        this.results = response.data;
      } catch (error) {
        console.error("Error fetching results:", error);
      }
    },
    isQuizTaken(quizId) {
      return this.results.some((result) => result.quiz_id === quizId);
    },
    formatDate(dateString) {
      const options = { year: "numeric", month: "long", day: "numeric" };
      return new Date(dateString).toLocaleDateString(undefined, options);
    },
    handleQuizAction(quizId) {
      if (this.isQuizTaken(quizId)) {
        this.showResults(quizId);
      } else {
        this.startQuiz(quizId);
      }
    },
    async startQuiz(quizId) {
      try {
        const quiz = this.quizzes.find((q) => q.id === quizId);
        if (!quiz) throw new Error("Quiz not found");

        this.$router.push({
          name: "StudentExamPortal",
          params: { quizId: quizId },
          query: { duration: quiz.duration },
        });
      } catch (error) {
        console.error("Error starting quiz:", error);
        alert("Failed to start quiz. Please try again.");
      }
    },
    showResults(quizId) {
      const result = this.results.find((r) => r.quiz_id === quizId);
      this.$router.push({
        name: "ExamResult",
        params: { quizId },
        state: { result },
      });
    },
  },
};
</script>

<style scoped>
.student-dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.quiz-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.quiz-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.completed-badge {
  color: #22c55e;
  font-size: 1.2rem;
  margin-left: 0.5rem;
}

.quiz-details {
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  color: #4b5563;
}

.quiz-button {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.2s;
}

.take-test-button {
  background-color: #3b82f6;
  color: white;
}

.results-button {
  background-color: #10b981;
  color: white;
}

.quiz-button:hover {
  opacity: 0.9;
}
</style>
