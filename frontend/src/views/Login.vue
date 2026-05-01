<template>
  <div class="container">
    <div class="toast-stack">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="toast.type"
      >
        {{ toast.message }}
      </div>
    </div>

    <div class="card">

      <!-- 🔥 LOGO -->
      <img src="/icon2.png" class="logo" />

      <!-- Dynamic heading -->
      <h2>{{ heading }}</h2>

      <form @submit.prevent="handleSubmit">

        <input
          v-model="email"
          type="email"
          placeholder="Email"
          @blur="checkEmail"
        />

        <input
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          placeholder="Password"
        />
        <div class="toggle">
          <label>
            <input type="checkbox" v-model="showPassword" />
            Show Password
          </label>
        </div>

        <button type="submit" class="btn mb-2">
          {{ isExistingUser ? "Login" : "Register" }}
        </button>

        <router-link class="forgot-link" to="/password-reset">
          Forgot password?
        </router-link>
      </form>
      
      

      <p v-if="error" class="error">{{ error }}</p>

    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      email: "",
      password: "",
      heading: "Welcome",
      error: "",
      isExistingUser: true, // controls login/register
      showPassword: false,
      toasts: [],
      toastId: 0,
    };
  },

  methods: {
    async checkEmail() {
      if (!this.email) {
        this.heading = "Welcome";
        return;
      }

      try {
        const res = await axios.get(
          "http://127.0.0.1:8000/api/email-exists/",
          {
            params: { email: this.email },
          }
        );

        if (res.data.exists) {
          this.heading = "Welcome Back";
          this.isExistingUser = true;
        } else {
          this.heading = "Create Account";
          this.isExistingUser = false;
        }
      } catch (err) {
        this.heading = "Welcome";
      }
    },

    async handleSubmit() {
      this.error = "";

      if (this.isExistingUser) {
        await this.login();
      } else {
        await this.register();
      }
    },

    async login() {
      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/api/token/",
          {
            username: this.email,
            password: this.password,
          }
        );

        localStorage.setItem("access", response.data.access);
        localStorage.setItem("refresh", response.data.refresh);

        sessionStorage.setItem(
          "toast",
          JSON.stringify({
            message: "Welcome back. You are signed in.",
            type: "success",
          })
        );
        this.$router.push("/dashboard");

      } catch (err) {
        this.error = "Invalid credentials";
        this.showToast("Invalid email or password.", "error");
      }
    },

    async register() {
      try {
        await axios.post(
          "http://127.0.0.1:8000/api/register/",
          {
            username: this.email,
            email: this.email,
            password: this.password,
          }
        );

        this.showToast("Account created. You can log in now.", "success");
        this.isExistingUser = true;
        this.heading = "Welcome Back";

      } catch (err) {
        this.error = "Registration failed";
        this.showToast("Registration failed. Please try again.", "error");
      }
    },

    showToast(message, type = "success") {
      const id = ++this.toastId;
      this.toasts.push({ id, message, type });

      setTimeout(() => {
        this.toasts = this.toasts.filter((toast) => toast.id !== id);
      }, 4200);
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

.toast-stack {
  position: fixed;
  top: 18px;
  right: 18px;
  z-index: 20;
  display: grid;
  gap: 10px;
  width: min(320px, calc(100vw - 36px));
}

.toast {
  padding: 14px 16px;
  background: #ffffff;
  border: 1px solid #dadce0;
  border-left: 4px solid #34a853;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(60, 64, 67, 0.22);
  color: #202124;
  font-size: 14px;
  line-height: 1.35;
  text-align: left;
}

.toast.error {
  border-left-color: #ea4335;
}

.card {
  width: 340px;
  padding: 30px;
  background: white;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(60, 64, 67, 0.16);
}

/* 🔥 LOGO */
.logo {
  display: block;
  margin: 0 auto 20px;
  width: 120px;
  height: auto;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #202124;
  font-weight: 500;
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

.error {
  color: #ea4335;
  font-size: 12px;
  text-align: center;
  margin-top: 10px;
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

.forgot-link {
  display: block;
  margin-top: 14px;
  color: #1a73e8;
  font-size: 12px;
  text-align: center;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}
</style>
