<template>
  <div class="container mt-5">
    <h1 class="text-center">This is the Student Dashboard</h1>
    <p class="text-center">Welcome, Student! 🎓</p>
  </div>
</template>

<script>
export default {
  mounted() {
    const role = localStorage.getItem("userRole");
    if (role !== "student") {
      this.$router.push("/"); // Redirect if not a student
    }
  },
};
</script>

<style>
.container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
}
</style>
