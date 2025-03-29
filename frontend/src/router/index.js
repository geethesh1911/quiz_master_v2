import Vue from "vue";
import VueRouter from "vue-router";
import SignupForm from "@/components/SignupForm.vue";
import LoginForm from "@/components/LoginForm.vue";
import AdminDashboard from "@/views/AdminDashboard.vue";
import StudentDashboard from "@/views/StudentDashboard.vue";
import MainNavbar from "@/components/MainNavbar.vue";
import AdminQuizzes from "@/views/AdminQuizzes.vue";
import StudentExamPortal from "@/views/StudentExamPortal.vue";
Vue.use(VueRouter);

Vue.component("MainNavbar", MainNavbar);

const routes = [
  {
    path: "/signup",
    name: "SignupForm",
    component: SignupForm,
  },
  {
    path: "/login",
    name: "LoginForm",
    component: LoginForm,
  },
  { path: "/admin-dashboard", component: AdminDashboard },
  { path: "/student-dashboard", component: StudentDashboard },
  { path: "/admin-quizzes", component: AdminQuizzes },
  // router.js
  {
    path: "/student/exam/:quizId",
    name: "StudentExamPortal",
    component: StudentExamPortal,
    meta: { requiresAuth: true, role: "student" },
  },
  {
    path: "/student/quiz-result/:quizId",
    name: "ExamResult",
    component: () => import("@/views/ExamResult.vue"),
    meta: { requiresAuth: true, role: "student" },
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
