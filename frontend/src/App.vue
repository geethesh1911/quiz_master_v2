<template>
  <div id="app">
    <MainNavbar />
    <router-view />
  </div>
</template>

<script>
import MainNavbar from "@/components/MainNavbar.vue"; // Adjust the path if needed

export default {
  components: {
    MainNavbar,
  },
};
</script>

<style>
body {
  margin: 0;
  font-family: Arial, sans-serif;
}
</style>
