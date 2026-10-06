<template>
  <div class="container">
    <div class="card">
      <img src="/icon2.png" class="logo" />

      <h2>Password Reset</h2>
      <p class="description">
        Enter your email and we will send password reset instructions.
      </p>

      <form @submit.prevent="handleReset">
        <input
          v-model="email"
          type="email"
          placeholder="Email"
          required
        />

        <button type="submit" :disabled="loading">
          {{ loading ? "Sending..." : "Send Reset Link" }}
        </button>
      </form>

      <p v-if="message" class="message">{{ message }}</p>
      <p v-if="error" class="error">{{ error }}</p>

      <router-link class="back-link" to="/">
        Back to Login
      </router-link>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      email: "",
      message: "",
      error: "",
      loading: false,
    };
  },

  methods: {
    async handleReset() {
      this.message = "";
      this.error = "";
      this.loading = true;

      try {
        const response = await axios.post(
          "/api/password-reset/",
          { email: this.email }
        );

        this.message = response.data.detail;
        this.email = "";
      } catch (err) {
        this.error = "Unable to send reset instructions. Please try again.";
      } finally {
        this.loading = false;
      }
    },
  },

  mounted() {
    if (this.$route.query.email) {
      this.email = this.$route.query.email;
    }
  },
};
</script>

<style scoped>
.container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f8fafd;
}

.card {
  width: 340px;
  padding: 30px;
  background: white;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(60, 64, 67, 0.16);
}

.logo {
  display: block;
  margin: 0 auto 20px;
  width: 120px;
  height: auto;
}

h2 {
  text-align: center;
  margin-bottom: 10px;
  color: #202124;
  font-weight: 500;
}

.description {
  margin-bottom: 18px;
  color: #5f6368;
  font-size: 13px;
  line-height: 1.4;
  text-align: center;
}

input {
  width: 100%;
  padding: 11px;
  margin-bottom: 12px;
  border: 1px solid #dadce0;
  border-radius: 8px;
}

input:focus {
  border-color: #1a73e8;
  outline: 3px solid rgba(26, 115, 232, 0.14);
}

button {
  width: 100%;
  padding: 11px;
  background: #1a73e8;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

button:hover {
  background: #1967d2;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.message {
  margin-top: 12px;
  color: #188038;
  font-size: 12px;
  line-height: 1.4;
  text-align: center;
}

.error {
  margin-top: 12px;
  color: #ea4335;
  font-size: 12px;
  line-height: 1.4;
  text-align: center;
}

.back-link {
  display: block;
  margin-top: 16px;
  color: #1a73e8;
  font-size: 12px;
  text-align: center;
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}
</style>
