<template>
  <div class="admin-quizzes">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Manage Quizzes</h1>
      <button @click="showQuizModal(null)" class="btn btn-primary">
        Create New Quiz
      </button>
    </div>

    <!-- Quizzes Cards -->
    <div class="quizzes-grid">
      <div v-for="quiz in quizzes" :key="quiz.id" class="quiz-card">
        <div class="quiz-header">
          <h3 @click="showQuizDetails(quiz)">Quiz #{{ quiz.id }}</h3>
          <div class="quiz-meta">
            <span>Chapter: {{ quiz.chapter_id }}</span>
            <span> Duration: {{ quiz.duration }} mins</span>
          </div>
        </div>

        <!-- Questions Table -->
        <table class="questions-table">
          <thead>
            <tr>
              <th>QID</th>
              <th>Question Title</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="question in quiz.questions" :key="question.id">
              <td>{{ question.id }}</td>
              <td>{{ question.title }}</td>
              <td>
                <button @click="editQuestion(question)" class="icon-btn">
                  ✏️
                </button>
                <button @click="deleteQuestion(question.id)" class="icon-btn">
                  🗑️
                </button>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="3">
                <button @click="showQuestionModal(quiz.id)" class="add-btn">
                  + Add Question
                </button>
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Quiz Details Modal -->
    <!-- Add this new modal for quiz details -->
    <div v-if="isQuizDetailsModalOpen" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Quiz Details</h3>
          <button @click="closeQuizDetailsModal" class="close-btn">x</button>
        </div>
        <div class="details-content">
          <div class="detail-row">
            <span class="detail-label">Quiz ID:</span>
            <span class="detail-value">{{ currentQuizDetails.id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Subject:</span>
            <span class="detail-value">{{
              currentQuizDetails.subject_name
            }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Chapter:</span>
            <span class="detail-value">{{
              currentQuizDetails.chapter_name
            }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Duration:</span>
            <span class="detail-value"
              >{{ currentQuizDetails.duration }} minutes</span
            >
          </div>
          <div class="detail-row">
            <span class="detail-label">Date Created:</span>
            <span class="detail-value">{{
              formatDate(currentQuizDetails.date)
            }}</span>
          </div>
          <div class="detail-row" v-if="currentQuizDetails.remarks">
            <span class="detail-label">Remarks:</span>
            <span class="detail-value">{{ currentQuizDetails.remarks }}</span>
          </div>
        </div>
      </div>
    </div>
    <!-- Quiz Creation Modal -->
    <div v-if="isQuizModalOpen" class="modal">
      <div class="modal-content">
        <h3>{{ editingQuiz ? "Edit" : "Create" }} Quiz</h3>
        <form @submit.prevent="saveQuiz">
          <label for="chapter-id">
            Chapter ID:
            <input
              id="chapter-id"
              v-model="currentQuiz.chapter_id"
              type="number"
              name="chapter_id"
              required
            />
          </label>
          <label for="duration">
            Duration (mins):
            <input
              id="duration"
              v-model="currentQuiz.duration"
              type="number"
              name="duration"
              required
            />
          </label>
          <label for="remarks">
            Remarks:
            <textarea
              id="remarks"
              v-model="currentQuiz.remarks"
              name="remarks"
            ></textarea>
          </label>
          <div class="modal-actions">
            <button type="button" @click="closeModals">Cancel</button>
            <button type="submit">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Question Modal -->
    <div v-if="isQuestionModalOpen" class="modal">
      <div class="modal-content">
        <h3>{{ editingQuestion ? "Edit" : "Add" }} Question</h3>
        <form @submit.prevent="saveQuestion">
          <label for="question-title">
            Title:
            <input
              id="question-title"
              v-model="currentQuestion.title"
              name="title"
              required
            />
          </label>
          <label for="question-statement">
            Question Statement:
            <textarea
              id="question-statement"
              v-model="currentQuestion.text"
              name="statement"
              required
            ></textarea>
          </label>
          <div v-for="n in 4" :key="n">
            <label :for="`option-${n}`">
              Option {{ n }}:
              <input
                :id="`option-${n}`"
                v-model="currentQuestion.options[n - 1]"
                :name="`option${n}`"
                required
              />
            </label>
          </div>
          <label for="correct-option">
            Correct Option (1-4):
            <input
              id="correct-option"
              v-model="currentQuestion.correct"
              type="number"
              min="1"
              max="4"
              name="correct_option"
              required
            />
          </label>
          <div class="modal-actions">
            <button type="button" @click="closeModals">Cancel</button>
            <button type="submit">Save</button>
          </div>
        </form>
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
      isQuizModalOpen: false,
      isQuestionModalOpen: false,
      currentQuiz: { chapter_id: null, duration: 30, remarks: "" },
      currentQuestion: {
        title: "",
        text: "",
        options: ["", "", "", ""],
        correct: 1,
        quiz_id: null,
      },
      editingQuiz: null,
      editingQuestion: null,
      isQuizDetailsModalOpen: false,
      currentQuizDetails: {},
    };
  },
  async created() {
    await this.fetchQuizzes();
  },
  methods: {
    async fetchQuizzes() {
      try {
        const response = await axios.get(
          "http://127.0.0.1:5000/admin/quizzes",
          {
            headers: { Authorization: sessionStorage.getItem("token") },
          }
        );
        this.quizzes = response.data;
      } catch (error) {
        console.error("Error fetching quizzes:", error);
      }
    },
    async saveQuiz() {
      try {
        const url = this.editingQuiz
          ? `http://127.0.0.1:5000/admin/quizzes/${this.editingQuiz.id}`
          : "http://127.0.0.1:5000/admin/quizzes";

        const method = this.editingQuiz ? "put" : "post";

        await axios[method](url, this.currentQuiz, {
          headers: { Authorization: sessionStorage.getItem("token") },
        });

        await this.fetchQuizzes();
        this.closeModals();
      } catch (error) {
        console.error("Error saving quiz:", error);
      }
    },
    async saveQuestion() {
      try {
        const url = this.editingQuestion
          ? `http://127.0.0.1:5000/admin/questions/${this.editingQuestion.id}`
          : "http://127.0.0.1:5000/admin/questions";

        const data = {
          ...this.currentQuestion,
          quiz_id: this.currentQuestion.quiz_id,
          options: this.currentQuestion.options,
        };

        await axios({
          method: this.editingQuestion ? "put" : "post",
          url,
          data,
          headers: { Authorization: sessionStorage.getItem("token") },
        });

        await this.fetchQuizzes();
        this.closeModals();
      } catch (error) {
        console.error("Error saving question:", error);
      }
    },
    editQuestion(question) {
      this.showQuestionModal(question.quiz_id, question);
    },
    async deleteQuestion(questionId) {
      if (confirm("Are you sure you want to delete this question?")) {
        try {
          await axios.delete(
            `http://127.0.0.1:5000/admin/questions/${questionId}`,
            {
              headers: { Authorization: sessionStorage.getItem("token") },
            }
          );
          await this.fetchQuizzes();
        } catch (error) {
          console.error("Error deleting question:", error);
        }
      }
    },
    showQuizDetails(quiz) {
      this.currentQuizDetails = quiz;
      this.isQuizDetailsModalOpen = true;
    },

    closeQuizDetailsModal() {
      this.isQuizDetailsModalOpen = false;
    },

    formatDate(dateString) {
      if (!dateString) return "N/A";
      const date = new Date(dateString);
      return date.toLocaleDateString() + " " + date.toLocaleTimeString();
    },
    showQuizModal(quiz = null) {
      this.editingQuiz = quiz;
      this.currentQuiz = quiz
        ? { ...quiz }
        : { chapter_id: null, duration: 30, remarks: "" };
      this.isQuizModalOpen = true;
    },
    showQuestionModal(quizId, question = null) {
      this.editingQuestion = question;
      this.currentQuestion = question
        ? { ...question }
        : {
            title: "",
            text: "",
            options: ["", "", "", ""],
            correct: 1,
            quiz_id: quizId,
          };
      this.isQuestionModalOpen = true;
    },
    closeModals() {
      this.isQuizModalOpen = false;
      this.isQuestionModalOpen = false;
      this.editingQuiz = null;
      this.editingQuestion = null;
    },
  },
};
</script>

<style scoped>
.admin-quizzes {
  padding: 20px;
}

.quizzes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 20px;
}

.quiz-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.quiz-header {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.questions-table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000; /* Ensure this is present */
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}
.details-content {
  padding: 15px 0;
}

.detail-row {
  display: flex;
  margin-bottom: 10px;
}

.detail-label {
  font-weight: bold;
  min-width: 120px;
}

.detail-value {
  flex: 1;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  position: absolute;
  top: 10px;
  right: 10px;
}

.modal-header {
  position: relative;
  padding-right: 30px;
  margin-bottom: 15px;
}
</style>
