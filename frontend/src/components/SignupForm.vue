<template>
  <div
    class="container d-flex justify-content-center align-items-center vh-100"
  >
    <div
      class="card p-4 shadow-lg rounded-4"
      style="width: 100%; max-width: 450px"
    >
      <h2 class="text-center fw-bold text-primary mb-4">
        Welcome to Quiz Master
      </h2>
      <form @submit.prevent="register">
        <div class="mb-3">
          <label class="form-label fw-semibold">Name</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-person"></i></span>
            <input
              type="text"
              class="form-control"
              v-model="name"
              placeholder="Enter your name"
              required
            />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold">Email</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-envelope"></i></span>
            <input
              type="email"
              class="form-control"
              v-model="email"
              placeholder="Enter your email"
              required
            />
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold">Password</label>
          <div class="input-group">
            <span class="input-group-text"><i class="bi bi-lock"></i></span>
            <input
              type="password"
              class="form-control"
              v-model="password"
              placeholder="Enter password"
              required
            />
          </div>
          <small
            v-if="password.length > 0 && password.length < 8"
            class="text-danger"
          >
            Password must be at least 8 characters long.
          </small>
        </div>

        <div class="mb-3">
          <label class="form-label fw-semibold">Confirm Password</label>
          <div class="input-group">
            <span class="input-group-text"
              ><i class="bi bi-check-circle"></i
            ></span>
            <input
              type="password"
              class="form-control"
              v-model="confirmPassword"
              placeholder="Re-enter password"
              required
            />
          </div>
          <small
            v-if="confirmPassword && password !== confirmPassword"
            class="text-danger"
          >
            Passwords do not match.
          </small>
        </div>

        <button type="submit" class="btn btn-primary rounded-pill fw-bold">
          Sign Up
        </button>
      </form>

      <p class="text-center mt-3">
        Already have an account?
        <router-link
          to="/login"
          class="text-decoration-none text-primary fw-semibold"
          >Login</router-link
        >
      </p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
    };
  },
  methods: {
    async register() {
      if (this.password.length < 8) {
        alert("Password must be at least 8 characters long");
        return;
      }
      if (this.password !== this.confirmPassword) {
        alert("Passwords do not match");
        return;
      }

      try {
        const response = await fetch("http://127.0.0.1:5000/auth/signup", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: this.name,
            email: this.email,
            password: this.password,
          }),
        });

        const result = await response.json();
        if (response.ok) {
          alert("Signup successful!");
          this.$router.push("/login");
        } else {
          alert(result.error || "Signup failed");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred");
      }
    },
  },
};
</script>

<style>
/* Responsive Design */
@media (max-width: 768px) {
  .container {
    padding: 20px;
  }
}

/* Additional Styling */
.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
}

.input-group .form-control {
  border-left: none;
}

.card {
  border: none;
}
</style>
