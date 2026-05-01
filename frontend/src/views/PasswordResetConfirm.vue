<template>
  <div class="container">
    <div class="card">
      <img src="/icon2.png" class="logo" />

      <h2>Set New Password</h2>
      <p class="description">
        Choose a new password for your account.
      </p>

      <form @submit.prevent="handleConfirm">
        <input
          v-model="newPassword"
          :type="showPassword ? 'text' : 'password'"
          placeholder="New Password"
          required
        />

        <input
          v-model="confirmPassword"
          :type="showPassword ? 'text' : 'password'"
          placeholder="Confirm Password"
          required
        />

        <div class="toggle">
          <label>
            <input type="checkbox" v-model="showPassword" />
            Show Password
          </label>
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? "Saving..." : "Reset Password" }}
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
      newPassword: "",
      confirmPassword: "",
      showPassword: false,
      message: "",
      error: "",
      loading: false,
    };
  },

  methods: {
    async handleConfirm() {
      this.message = "";
      this.error = "";

      if (this.newPassword !== this.confirmPassword) {
        this.error = "Passwords do not match.";
        return;
      }

      this.loading = true;

      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/api/password-reset-confirm/",
          {
            uid: this.$route.params.uid,
            token: this.$route.params.token,
            new_password: this.newPassword,
          }
        );

        this.message = response.data.detail;
        this.newPassword = "";
        this.confirmPassword = "";
      } catch (err) {
        const data = err.response?.data;
        this.error = data?.non_field_errors?.[0]
          || data?.new_password?.[0]
          || "Unable to reset password. The link may be invalid or expired.";
      } finally {
        this.loading = false;
      }
    },
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

.toggle {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 12px;
  font-size: 12px;
  color: #5f6368;
}

.toggle input {
  width: auto;
  margin-right: 6px;
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
