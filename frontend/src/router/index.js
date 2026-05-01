import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import Login from "../views/Login.vue";
import PasswordReset from "../views/PasswordReset.vue";
import PasswordResetConfirm from "../views/PasswordResetConfirm.vue";
import Profile from "../views/Profile.vue";

const routes = [
  { path: "/", component: Login },
  { path: "/password-reset", component: PasswordReset },
  { path: "/password-reset-confirm/:uid/:token", component: PasswordResetConfirm },
  { path: "/dashboard", component: Dashboard, meta: { requiresAuth: true } },
  { path: "/profile", component: Profile, meta: { requiresAuth: true } },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 🔐 Protect dashboard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("access");

  if (to.meta.requiresAuth && !token) {
    next("/");
  } else {
    next();
  }
});

export default router;
