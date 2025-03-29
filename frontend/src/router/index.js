import Vue from "vue";
import VueRouter from "vue-router";
import SignupForm from "@/components/SignupForm.vue";
import LoginForm from "@/components/LoginForm.vue";
import AdminDashboard from "@/views/AdminDashboard.vue";
import StudentDashboard from "@/views/StudentDashboard.vue";
import MainNavbar from "@/components/MainNavbar.vue";
import AdminQuizzes from "@/views/AdminQuizzes.vue";
Vue.use(VueRouter);

// Register the MainNavbar component globally
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
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
