<template>
  <div class="admin-dashboard">
    <!-- Header with Add Subject Button -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Admin Dashboard</h1>
      <button @click="showSubjectModal(null)" class="btn btn-primary">
        Add Subject
      </button>
    </div>

    <!-- Subjects Grid -->
    <div class="subjects-grid">
      <div v-for="subject in subjects" :key="subject.id" class="subject-card">
        <div class="card-header">
          <h3 @click="viewSubject(subject)">{{ subject.name }}</h3>
          <div class="subject-actions">
            <button @click="showSubjectModal(subject)" class="icon-btn">
              ✏️
            </button>
            <button @click="deleteSubject(subject.id)" class="icon-btn">
              🗑️
            </button>
          </div>
        </div>

        <!-- Chapters Table -->
        <table class="chapters-table">
          <thead>
            <tr>
              <th>Chapter Name</th>
              <th>Questions</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="chapter in subject.chapters" :key="chapter.id">
              <td @click="viewChapter(chapter)">{{ chapter.name }}</td>
              <td>{{ chapter.total_questions }}</td>
              <td>
                <button @click="showChapterModal(chapter)" class="icon-btn">
                  ✏️
                </button>
                <button @click="deleteChapter(chapter.id)" class="icon-btn">
                  🗑️
                </button>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="3">
                <button
                  @click="showChapterModal(null, subject.id)"
                  class="add-btn"
                >
                  + Add Chapter
                </button>
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>

    <!-- Add/Edit Subject Modal -->
    <div v-if="isSubjectModalOpen" class="modal">
      <div class="modal-content">
        <h3>{{ editingSubject ? "Edit" : "Add" }} Subject</h3>
        <form @submit.prevent="saveSubject">
          <label>
            Subject Name:
            <input v-model="currentSubject.name" required />
          </label>
          <label>
            Description:
            <textarea v-model="currentSubject.description"></textarea>
          </label>
          <div class="modal-actions">
            <button type="button" @click="closeModals">Cancel</button>
            <button type="submit">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add/Edit Chapter Modal -->
    <div v-if="isChapterModalOpen" class="modal">
      <div class="modal-content">
        <h3>{{ editingChapter ? "Edit" : "Add" }} Chapter</h3>
        <form @submit.prevent="saveChapter">
          <label>
            Chapter Name:
            <input v-model="currentChapter.name" required />
          </label>
          <label>
            Description:
            <textarea v-model="currentChapter.description"></textarea>
          </label>
          <div class="modal-actions">
            <button type="button" @click="closeModals">Cancel</button>
            <button type="submit">Save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Subject Modal -->
    <div v-if="isViewSubjectModalOpen" class="modal">
      <div class="modal-content view-modal">
        <div class="modal-header">
          <h3>Subject Details</h3>
          <button @click="closeViewModals" class="close-icon">×</button>
        </div>
        <div class="details-content">
          <div class="detail-row">
            <span class="detail-label">Name:</span>
            <span class="detail-value">{{ viewingSubject.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Description:</span>
            <span
              v-if="viewingSubject.description"
              class="detail-value description-text"
            >
              {{ viewingSubject.description }}
            </span>
            <span v-else class="detail-value no-description"
              >No description available</span
            >
          </div>
        </div>
      </div>
    </div>

    <!-- View Chapter Modal -->
    <div v-if="isViewChapterModalOpen" class="modal">
      <div class="modal-content view-modal">
        <div class="modal-header">
          <h3>Chapter Details</h3>
          <button @click="closeViewModals" class="close-icon">×</button>
        </div>
        <div class="details-content">
          <div class="detail-row">
            <span class="detail-label">Name:</span>
            <span class="detail-value">{{ viewingChapter.name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Description:</span>
            <span
              v-if="viewingChapter.description"
              class="detail-value description-text"
            >
              {{ viewingChapter.description }}
            </span>
            <span v-else class="detail-value no-description"
              >No description available</span
            >
          </div>
          <div class="detail-row">
            <span class="detail-label">Questions:</span>
            <span class="detail-value">{{
              viewingChapter.total_questions || 0
            }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      subjects: [],
      isSubjectModalOpen: false,
      isChapterModalOpen: false,
      isViewSubjectModalOpen: false,
      isViewChapterModalOpen: false,
      currentSubject: { name: "", description: "" },
      currentChapter: { name: "", description: "", subject_id: null },
      viewingSubject: { name: "", description: "" },
      viewingChapter: { name: "", description: "", total_questions: 0 },
      editingSubject: null,
      editingChapter: null,
    };
  },
  async created() {
    Object.keys(localStorage).forEach((key) => {
      if (key.startsWith("exam_")) {
        localStorage.removeItem(key);
      }
    });

    await this.fetchSubjects();
  },
  methods: {
    async fetchSubjects() {
      try {
        const response = await axios.get(
          "http://localhost:5000/admin/subjects",
          {
            headers: { Authorization: sessionStorage.getItem("token") },
          }
        );
        this.subjects = await Promise.all(
          response.data.map(async (subject) => ({
            ...subject,
            chapters: await this.fetchChapters(subject.id),
          }))
        );
      } catch (error) {
        console.error("Error fetching subjects:", error);
      }
    },
    async fetchChapters(subjectId) {
      try {
        const response = await axios.get(
          `http://localhost:5000/admin/subjects/${subjectId}/chapters`,
          {
            headers: { Authorization: sessionStorage.getItem("token") },
          }
        );
        return response.data.map((chapter) => ({
          ...chapter,
          total_questions: chapter.questions_count || 0,
        }));
      } catch (error) {
        console.error("Error fetching chapters:", error);
        return [];
      }
    },
    async saveSubject() {
      try {
        const url = this.editingSubject
          ? `http://127.0.0.1:5000/admin/subjects/${this.editingSubject.id}`
          : "http://127.0.0.1:5000/admin/subjects";

        await axios({
          method: this.editingSubject ? "PUT" : "POST",
          url,
          data: this.currentSubject,
          headers: {
            Authorization: sessionStorage.getItem("token"),
          },
        });

        await this.fetchSubjects();
        this.closeModals();
      } catch (error) {
        console.error("Error saving subject:", error);
      }
    },
    async deleteSubject(subjectId) {
      if (confirm("Are you sure you want to delete this subject?")) {
        try {
          await axios.delete(
            `http://127.0.0.1:5000/admin/subjects/${subjectId}`,
            {
              headers: {
                Authorization: sessionStorage.getItem("token"),
              },
            }
          );
          await this.fetchSubjects();
        } catch (error) {
          console.error("Error deleting subject:", error);
        }
      }
    },
    async saveChapter() {
      try {
        const url = this.editingChapter
          ? `http://127.0.0.1:5000/admin/chapters/${this.editingChapter.id}`
          : `http://127.0.0.1:5000/admin/subjects/${this.currentChapter.subject_id}/chapters`;

        await axios({
          method: this.editingChapter ? "PUT" : "POST",
          url,
          data: this.currentChapter,
          headers: {
            Authorization: sessionStorage.getItem("token"),
          },
        });

        await this.fetchSubjects();
        this.closeModals();
      } catch (error) {
        console.error("Error saving chapter:", error);
      }
    },
    async deleteChapter(chapterId) {
      if (confirm("Are you sure you want to delete this chapter?")) {
        try {
          await axios.delete(
            `http://127.0.0.1:5000/admin/chapters/${chapterId}`,
            {
              headers: {
                Authorization: sessionStorage.getItem("token"),
              },
            }
          );
          await this.fetchSubjects();
        } catch (error) {
          console.error("Error deleting chapter:", error);
        }
      }
    },
    showSubjectModal(subject) {
      this.editingSubject = subject;
      this.currentSubject = subject
        ? { name: subject.name, description: subject.description }
        : { name: "", description: "" };
      this.isSubjectModalOpen = true;
    },
    showChapterModal(chapter, subjectId) {
      this.editingChapter = chapter;
      this.currentChapter = chapter
        ? { ...chapter }
        : { name: "", description: "", subject_id: subjectId };
      this.isChapterModalOpen = true;
    },
    closeModals() {
      this.isSubjectModalOpen = false;
      this.isChapterModalOpen = false;
      this.editingSubject = null;
      this.editingChapter = null;
    },
    viewSubject(subject) {
      this.viewingSubject = { ...subject };
      this.isViewSubjectModalOpen = true;
    },
    viewChapter(chapter) {
      this.viewingChapter = { ...chapter };
      this.isViewChapterModalOpen = true;
    },
    closeViewModals() {
      this.isViewSubjectModalOpen = false;
      this.isViewChapterModalOpen = false;
    },
  },
};
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
}

.subjects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 20px;
}

.subject-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chapters-table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  margin: 0 3px;
}

.add-btn {
  width: 100%;
  padding: 8px;
  background: #f0f0f0;
  border: none;
  cursor: pointer;
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
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
}

.modal-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>
