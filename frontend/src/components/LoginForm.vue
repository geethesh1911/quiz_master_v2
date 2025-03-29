<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-5">
        <div class="card shadow-lg px-5">
          <div class="card-body">
            <h3 class="text-center my-4">Welcome Back!</h3>
            <form @submit.prevent="login">
              <label for="email" class="form-label">Email</label>
              <input
                type="email"
                v-model="email"
                id="email"
                placeholder="abc@gmail.com"
                class="form-control"
                required
              />

              <label for="password" class="form-label mt-3">Password</label>
              <input
                type="password"
                v-model="password"
                id="password"
                class="form-control"
                required
              />

              <div class="text-center mt-4">
                <button
                  type="submit"
                  class="btn btn-primary w-100"
                  :disabled="loading"
                >
                  {{ loading ? "Logging in..." : "Login" }}
                </button>
                <div class="lead my-2">
                  New user?
                  <router-link to="/signup" style="font-size: 1.2rem"
                    >Sign Up</router-link
                  >
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      email: "",
      password: "",
      loading: false, 
    };
  },
  methods: {
    async login() {
      if (!this.email.includes("@") || this.password.length < 8) {
        alert("Invalid email or password too short!");
        return;
      }

      this.loading = true;

      try {
        const response = await fetch("http://127.0.0.1:5000/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password,
          }),
          credentials: "include", 
        });

        const result = await response.json();
        console.log("Result:", result);

        if (response.ok) {
          alert(result.message);
          console.log("Token:", result.token);
          sessionStorage.setItem("token", result.token);

          if (result.role === "student") {
            this.$router.push("/student-dashboard");
          } else if (result.role === "admin") {
            this.$router.push("/admin-dashboard");
          } else {
            alert("Unknown role, redirecting to home page.");
            this.$router.push("/");
          }
        } else {
          alert(result.error || "Login failed");
        }
      } catch (error) {
        console.error("Error:", error);
        alert("An error occurred");
      } finally {
        this.loading = false; 
      }
    },
  },
};
</script>

<style>
.container {
  max-width: 500px;
}

.card {
  border-radius: 10px;
  padding: 20px;
}
</style>
