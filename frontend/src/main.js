import axios from "axios";
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

axios.defaults.baseURL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

createApp(App).use(router).mount("#app");