<template>
  <nav class="navbar navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid">
      <!-- Brand -->
      <router-link class="navbar-brand" to="/">Quiz Master</router-link>

      <!-- Navbar Toggler (for mobile) -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navbar Items -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <!-- Admin Navigation -->
          <template v-if="userRole === 'admin'">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin-dashboard"
                >Dashboard</router-link
              >
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin-quizzes"
                >Quiz Management</router-link
              >
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/reports"
                >Reports</router-link
              >
            </li>
          </template>

          <!-- Student Navigation -->
          <template v-else-if="userRole === 'student'">
            <li class="nav-item">
              <router-link class="nav-link" to="/student/dashboard"
                >Dashboard</router-link
              >
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/quizzes"
                >Available Quizzes</router-link
              >
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/results"
                >My Results</router-link
              >
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/student/profile"
                >Profile</router-link
              >
            </li>
          </template>

          <!-- Guest Navigation -->
          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/signup">Sign Up</router-link>
            </li>
          </template>

          <!-- Logout Option (Only when logged in) -->
          <li v-if="userRole" class="nav-item">
            <a class="nav-link" href="#" @click="logout">Logout</a>
          </li>
        </ul>

        <!-- Profile Icon (Only when logged in) -->
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0" v-if="userRole">
          <li class="nav-item">
            <router-link class="nav-link" to="/profile">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="40"
                height="40"
                fill="currentColor"
                class="bi bi-person"
                viewBox="0 0 16 16"
              >
                <path
                  d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6m2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0m4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4m-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10s-3.516.68-4.168 1.332c-.678.678-.83 1.418-.832 1.664z"
                />
              </svg>
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { jwtDecode } from "jwt-decode";

export default {
  data() {
    return {
      userRole: null,
    };
  },
  watch: {
    $route() {
      this.getUserRole();
    },
  },
  created() {
    this.getUserRole();
    // Add event listener for token changes
    window.addEventListener("storage", this.handleStorageChange);
  },
  beforeUnmount() {
    // Remove event listener to prevent memory leaks
    window.removeEventListener("storage", this.handleStorageChange);
  },
  methods: {
    getUserRole() {
      const token = sessionStorage.getItem("token");
      if (token) {
        try {
          const decoded = jwtDecode(token);
          this.userRole = decoded.role;
          console.log("User role from token:", this.userRole);
        } catch (error) {
          console.error("Error decoding token:", error);
          this.userRole = null;
        }
      } else {
        this.userRole = null;
      }
    },
    handleStorageChange(event) {
      // Check if the changed item is the userToken
      if (event.key === "token") {
        this.getUserRole();
      }
    },
    logout() {
      sessionStorage.removeItem("userToken");
      this.userRole = null;
      this.$router.push("/login");
    },
  },
};
</script>
