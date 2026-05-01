<template>
  <div class="profile-page">
    <header class="topbar">
      <button class="back-button" type="button" @click="$router.push('/dashboard')">
        Back
      </button>
      <h1>Profile</h1>
    </header>

    <main class="profile-shell">
      <section class="profile-card">
        <div class="avatar">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4Z" />
            <path d="M4 20c.82-3.45 3.95-6 8-6s7.18 2.55 8 6" />
          </svg>
        </div>

        <h2>{{ displayName }}</h2>
        <p class="muted">{{ user.email || "No email saved" }}</p>

        <div class="details">
          <div>
            <span>Username</span>
            <strong>{{ user.username || "Unknown" }}</strong>
          </div>
          <div>
            <span>Email</span>
            <strong>{{ user.email || "Unknown" }}</strong>
          </div>
          <div>
            <span>Member Since</span>
            <strong>{{ joinedDate }}</strong>
          </div>
        </div>

        <div class="actions">
          <button type="button" @click="goToResetPassword">
            Reset Password
          </button>
          <button class="secondary" type="button" @click="logout">
            Logout
          </button>
        </div>

        <p v-if="error" class="error">{{ error }}</p>
      </section>
    </main>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      user: {},
      error: "",
    };
  },

  computed: {
    displayName() {
      return this.user.username || this.user.email || "User";
    },

    joinedDate() {
      if (!this.user.date_joined) return "Unknown";

      return new Date(this.user.date_joined).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    },
  },

  methods: {
    getAuthHeader() {
      return {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access")}`,
        },
      };
    },

    async fetchUser() {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/me/",
          this.getAuthHeader()
        );

        this.user = response.data;
      } catch (err) {
        this.error = "Unable to load profile details.";

        if (err.response?.status === 401) {
          this.logout();
        }
      }
    },

    goToResetPassword() {
      this.$router.push({
        path: "/password-reset",
        query: { email: this.user.email },
      });
    },

    logout() {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      this.$router.push("/");
    },
  },

  mounted() {
    this.fetchUser();
  },
};
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f8fafd;
  color: #202124;
}

.topbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 28px;
  background: #ffffff;
  border-bottom: 1px solid #e8eaed;
}

.topbar h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 500;
}

.back-button,
button {
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.back-button {
  padding: 9px 12px;
  background: #f1f3f4;
  color: #3c4043;
}

.profile-shell {
  display: flex;
  justify-content: center;
  padding: 48px 20px;
}

.profile-card {
  width: min(520px, 100%);
  padding: 32px;
  background: #ffffff;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(60, 64, 67, 0.16);
  text-align: center;
}

.avatar {
  display: grid;
  place-items: center;
  width: 76px;
  height: 76px;
  margin: 0 auto 18px;
  border-radius: 50%;
  background: #1a73e8;
  color: #ffffff;
}

.avatar svg {
  width: 36px;
  height: 36px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

h2 {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 500;
}

.muted {
  color: #5f6368;
  font-size: 14px;
}

.details {
  display: grid;
  gap: 12px;
  margin: 28px 0;
  text-align: left;
}

.details div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 14px;
  background: #f8fafd;
  border: 1px solid #e8eaed;
  border-radius: 8px;
}

.details span {
  color: #5f6368;
  font-size: 13px;
}

.details strong {
  color: #202124;
  font-size: 14px;
  text-align: right;
  word-break: break-word;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.actions button {
  padding: 12px;
  background: #1a73e8;
  color: #ffffff;
}

.actions .secondary {
  background: #f1f3f4;
  color: #3c4043;
}

.error {
  margin-top: 14px;
  color: #ea4335;
  font-size: 13px;
}

@media (max-width: 640px) {
  .topbar {
    padding: 16px;
  }

  .profile-card {
    padding: 24px;
  }

  .actions {
    grid-template-columns: 1fr;
  }

  .details div {
    flex-direction: column;
    gap: 6px;
  }

  .details strong {
    text-align: left;
  }
}
</style>
