<template>
  <div class="exam-portal">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading Exam Questions...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Error Loading Exam</h3>
      <p>{{ error }}</p>
      <button @click="initializeExam" class="retry-button">Retry</button>
    </div>

    <!-- Exam Content -->
    <template v-else>
      <div class="exam-header">
        <div class="progress">
          Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}
        </div>
        <div class="timer">⏳ Time Left: {{ formattedTime }}</div>
      </div>

      <div class="question-container" v-if="currentQuestion">
        <h3 class="question-text">{{ currentQuestion.question }}</h3>

        <div class="options">
          <div
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            class="option"
          >
            <input
              type="radio"
              :id="`option-${currentQuestion.id}-${index}`"
              :value="index + 1"
              v-model="selectedAnswer"
            />
            <label :for="`option-${currentQuestion.id}-${index}`">
              {{ option }}
            </label>
          </div>
        </div>

        <div class="navigation-controls">
          <button
            @click="prevQuestion"
            :disabled="currentQuestionIndex === 0"
            class="nav-button prev-button"
          >
            ← Previous
          </button>

          <button
            v-if="!isLastQuestion"
            @click="nextQuestion"
            class="nav-button next-button"
          >
            Save & Next →
          </button>

          <button
            v-else
            @click="confirmSubmit"
            class="nav-button submit-button"
          >
            Submit Exam
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "StudentExamPortal",
  data() {
    return {
      loading: true,
      error: null,
      questions: [],
      answers: {},
      currentQuestionIndex: 0,
      timeLeft: 0,
      timerInterval: null,
      selectedAnswer: null,
    };
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentQuestionIndex] || null;
    },
    isLastQuestion() {
      return this.currentQuestionIndex === this.questions.length - 1;
    },
    formattedTime() {
      const minutes = Math.floor(this.timeLeft / 60);
      const seconds = this.timeLeft % 60;
      return `${minutes}:${seconds.toString().padStart(2, "0")}`;
    },
    storageKey() {
      return `exam_${this.$route.params.quizId}`;
    },
  },
  watch: {
    selectedAnswer(newVal) {
      this.saveAnswer(newVal);
    },
  },
  async mounted() {
    await this.initializeExam();
    this.startTimer();

    window.addEventListener("beforeunload", this.handleBeforeUnload);
  },
  beforeUnmount() {
    clearInterval(this.timerInterval);
    window.removeEventListener("beforeunload", this.handleBeforeUnload);
  },
  methods: {
    handleBeforeUnload(e) {
      if (this.timeLeft > 0) {
        this.saveExamState();
        e.preventDefault();
        e.returnValue =
          "Your exam progress will be saved. Are you sure you want to leave?";
      }
    },

    async initializeExam() {
      try {
        this.loading = true;
        this.error = null;

        const savedState = localStorage.getItem(this.storageKey);
        if (savedState) {
          const { questions, answers, currentQuestionIndex, timeLeft } =
            JSON.parse(savedState);

          if (timeLeft > 0) {
            this.questions = questions;
            this.answers = answers;
            this.currentQuestionIndex = currentQuestionIndex;
            this.timeLeft = timeLeft;
            this.selectedAnswer =
              answers[questions[currentQuestionIndex]?.id] || null;
            console.log("Restored timeLeft:", this.timeLeft);
            this.loading = false;
            return;
          } else {
            localStorage.removeItem(this.storageKey);
          }
        }

        const quizId = this.$route.params.quizId;
        const response = await axios.get(`/student/quizzes/${quizId}/start`, {
          headers: { Authorization: sessionStorage.getItem("token") },
        });

        if (!response.data?.questions || !response.data?.duration) {
          throw new Error("Invalid quiz data format from server");
        }

        this.questions = response.data.questions;
        this.timeLeft = response.data.duration * 60;
        this.answers = this.questions.reduce((acc, q) => {
          acc[q.id] = null;
          return acc;
        }, {});

        this.saveExamState();
      } catch (error) {
        console.error("Exam initialization error:", error);
        this.error =
          error.response?.data?.error || error.message || "Failed to load quiz";
      } finally {
        this.loading = false;
      }
    },

    saveExamState() {
      const state = {
        questions: this.questions,
        answers: this.answers,
        currentQuestionIndex: this.currentQuestionIndex,
        timeLeft: this.timeLeft, // Store remaining time instead of start time
      };
      localStorage.setItem(this.storageKey, JSON.stringify(state));
    },

    startTimer() {
      if (this.timerInterval) return; // Prevent multiple timers
      console.log("Timer started with:", this.timeLeft);

      this.timerInterval = setInterval(() => {
        if (this.timeLeft > 0) {
          this.timeLeft--;
          console.log("Time left:", this.timeLeft);
          if (this.timeLeft % 30 === 0) {
            this.saveExamState();
          }
        } else {
          this.autoSubmit();
        }
      }, 1000);
    },

    saveAnswer(answer) {
      if (this.currentQuestion) {
        this.answers[this.currentQuestion.id] = answer;
        this.saveExamState();
      }
    },

    prevQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--;
        this.selectedAnswer = this.answers[this.currentQuestion?.id] || null;
        this.saveExamState();
      }
    },

    nextQuestion() {
      if (this.currentQuestionIndex < this.questions.length - 1) {
        this.currentQuestionIndex++;
        this.selectedAnswer = this.answers[this.currentQuestion?.id] || null;
        this.saveExamState();
      }
    },

    confirmSubmit() {
      if (confirm("Are you sure you want to submit your answers?")) {
        this.submitQuiz();
      }
    },

    async autoSubmit() {
      clearInterval(this.timerInterval);
      console.log("Auto-submitting due to timer expiry!");
      await this.submitQuiz();
      alert("Time is up! Your answers have been submitted automatically.");
    },

    async submitQuiz() {
      try {
        const payload = { answers: this.answers };
        await axios.post(
          `/student/quizzes/${this.$route.params.quizId}/submit`,
          payload,
          { headers: { Authorization: sessionStorage.getItem("token") } }
        );

        localStorage.removeItem(this.storageKey);

        this.$router.push({
          name: "ExamResult",
          params: { quizId: this.$route.params.quizId },
        });
      } catch (error) {
        console.error("Submission error:", error);
        alert(
          error.response?.data?.error ||
            "Error submitting quiz. Please try again."
        );
      }
    },
  },
};
</script>

<style scoped>
.exam-portal {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading-state {
  text-align: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-state {
  text-align: center;
  padding: 30px;
  background: #ffe6e6;
  border-radius: 8px;
  color: #dc3545;
}

.error-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.retry-button {
  padding: 8px 20px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 15px;
}

.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 15px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.timer {
  color: #dc3545;
  font-weight: bold;
  font-size: 1.1em;
}

.question-container {
  background: white;
  padding: 25px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.question-text {
  color: #2c3e50;
  margin-bottom: 25px;
}

.options {
  display: grid;
  gap: 12px;
}

.option {
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  transition: all 0.2s;
}

.option:hover {
  border-color: #007bff;
  background: #f8f9ff;
}

input[type="radio"] {
  margin-right: 12px;
}

.navigation-controls {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  margin-top: 25px;
}

.nav-button {
  padding: 12px 25px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-button:disabled {
  background: #e9ecef;
  color: #6c757d;
  cursor: not-allowed;
}

.prev-button {
  background: #6c757d;
  color: white;
}

.next-button {
  background: #007bff;
  color: white;
}

.submit-button {
  background: #28a745;
  color: white;
}

.nav-button:hover:not(:disabled) {
  opacity: 0.9;
}
</style>
