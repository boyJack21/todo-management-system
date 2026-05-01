<template>
  <div class="dashboard-page" @click="closeUserMenu">
    <div class="toast-stack">
      <div v-for="toast in toasts" :key="toast.id" class="toast" :class="toast.type">
        {{ toast.message }}
      </div>
    </div>

    <header class="app-header">
      <div>
        <p class="eyebrow">Todo Management</p>
        <h1>Workspace</h1>
      </div>

      <div class="user-menu" @click.stop>
        <button class="user-button" type="button" @click="toggleUserMenu">
          <span class="user-avatar">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4Z" />
              <path d="M4 20c.82-3.45 3.95-6 8-6s7.18 2.55 8 6" />
            </svg>
          </span>
          <span class="user-copy">
            <strong>{{ displayName }}</strong>
            <small>{{ user.email || "Account" }}</small>
          </span>
          <svg class="chevron-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="m6 9 6 6 6-6" />
          </svg>
        </button>

        <div v-if="isUserMenuOpen" class="dropdown">
          <div class="dropdown-user">
            <strong>{{ displayName }}</strong>
            <span>{{ user.email || "Signed in" }}</span>
          </div>
          <button type="button" @click="goToProfile">Profile</button>
          <button type="button" @click="goToResetPassword">Reset Password</button>
          <button type="button" @click="logout">Logout</button>
        </div>
      </div>
    </header>

    <main class="dashboard-shell">
      <section class="summary-grid">
        <div class="summary-card">
          <span>Total</span>
          <strong>{{ todos.length }}</strong>
        </div>
        <div class="summary-card">
          <span>Open</span>
          <strong>{{ activeCount }}</strong>
        </div>
        <div class="summary-card">
          <span>Done</span>
          <strong>{{ completedCount }}</strong>
        </div>
        <div class="summary-card warning">
          <span>Overdue</span>
          <strong>{{ overdueCount }}</strong>
        </div>
      </section>

      <section class="progress-panel">
        <div>
          <h2>{{ progressPercent }}% complete</h2>
          <p>{{ completedCount }} of {{ todos.length }} tasks done</p>
        </div>
        <div class="progress-track" aria-hidden="true">
          <span :style="{ width: progressPercent + '%' }"></span>
        </div>
      </section>

      <section class="workspace-panel">
        <div class="workspace-top">
          <div class="view-tabs">
            <button
              v-for="view in views"
              :key="view.value"
              type="button"
              :class="{ active: activeView === view.value }"
              @click="activeView = view.value"
            >
              {{ view.label }}
            </button>
          </div>

          <label class="search-field">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <path d="m16 16 4 4" />
            </svg>
            <input v-model.trim="searchQuery" placeholder="Search tasks, notes, projects..." />
          </label>
        </div>

        <div class="projects-row">
          <button
            type="button"
            class="project-chip"
            :class="{ active: selectedProjectId === 'all' }"
            @click="selectedProjectId = 'all'"
          >
            All Projects
          </button>
          <button
            v-for="project in projects"
            :key="project.id"
            type="button"
            class="project-chip"
            :class="{ active: selectedProjectId === project.id }"
            @click="selectedProjectId = project.id"
          >
            <span :style="{ background: project.color }"></span>
            {{ project.name }}
          </button>
        </div>

        <form class="project-form" @submit.prevent="addProject">
          <input v-model.trim="newProjectName" placeholder="New project..." />
          <input v-model="newProjectColor" type="color" aria-label="Project color" />
          <button type="submit" :disabled="!newProjectName">Add Project</button>
        </form>

        <form class="add-form" @submit.prevent="addTodo">
          <input
            v-model.trim="newTodo"
            placeholder='Try "Submit report tomorrow urgent"'
            @input="applySmartSuggestions"
          />
          <select v-model="newProjectId" aria-label="Project">
            <option value="">No Project</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.name }}
            </option>
          </select>
          <select v-model="newStatus" aria-label="Status">
            <option value="backlog">Backlog</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
          <select v-model="newPriority" aria-label="Priority">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <input v-model="newDueDate" type="date" aria-label="Due date" />
          <select v-model="newRecurrence" aria-label="Recurrence">
            <option value="none">No Repeat</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
          <input v-model="newReminderAt" type="datetime-local" aria-label="Reminder" />
          <textarea v-model.trim="newNotes" placeholder="Notes or links..."></textarea>
          <button type="submit" :disabled="!newTodo">Add Task</button>
        </form>

        <p v-if="error" class="error">{{ error }}</p>

        <section v-if="activeView === 'list'" class="list-view">
          <div v-if="groupedSections.length" class="task-sections">
            <section v-for="section in groupedSections" :key="section.key" class="task-section">
              <div class="section-title">
                <h3>{{ section.label }}</h3>
                <span>{{ section.todos.length }}</span>
              </div>
              <article v-for="todo in section.todos" :key="todo.id" class="task-card">
                <TaskCard
                  :todo="todo"
                  :projects="projects"
                  @toggle="toggleTodo"
                  @delete="deleteTodo"
                  @save="saveTodo"
                  @subtask-add="addSubtask"
                  @subtask-toggle="toggleSubtask"
                />
              </article>
            </section>
          </div>
          <EmptyState v-else :title="emptyTitle" :message="emptyMessage" @focus="focusNewTask" />
        </section>

        <section v-if="activeView === 'kanban'" class="kanban-view">
          <div
            v-for="column in kanbanColumns"
            :key="column.value"
            class="kanban-column"
            @dragover.prevent
            @drop="dropTodo(column.value)"
          >
            <div class="column-title">
              <h3>{{ column.label }}</h3>
              <span>{{ todosByStatus(column.value).length }}</span>
            </div>
            <article
              v-for="todo in todosByStatus(column.value)"
              :key="todo.id"
              class="kanban-card"
              draggable="true"
              @dragstart="dragTodoId = todo.id"
            >
              <strong>{{ todo.title }}</strong>
              <small>{{ projectName(todo) }} - {{ dueLabel(todo) }}</small>
              <span class="priority-badge" :class="todo.priority || 'medium'">
                {{ priorityLabel(todo.priority) }}
              </span>
            </article>
          </div>
        </section>

        <section v-if="activeView === 'calendar'" class="calendar-view">
          <div v-for="day in calendarDays" :key="day.date" class="calendar-day" :class="{ muted: !day.currentMonth }">
            <strong>{{ day.day }}</strong>
            <button
              v-for="todo in day.todos"
              :key="todo.id"
              type="button"
              class="calendar-task"
              :class="todo.priority"
              @click="activeView = 'list'"
            >
              {{ todo.title }}
            </button>
          </div>
        </section>

        <section v-if="activeView === 'analytics'" class="analytics-view">
          <div class="analytics-card">
            <span>Completion Rate</span>
            <strong>{{ progressPercent }}%</strong>
          </div>
          <div class="analytics-card">
            <span>High Priority Open</span>
            <strong>{{ highPriorityOpen }}</strong>
          </div>
          <div class="analytics-card">
            <span>Recurring Tasks</span>
            <strong>{{ recurringCount }}</strong>
          </div>
          <div class="analytics-card">
            <span>With Subtasks</span>
            <strong>{{ tasksWithSubtasks }}</strong>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<script>
import axios from "axios";
import { defineComponent } from "vue";

const ACTIVITY_KEY = "todo_activity";

const EmptyState = defineComponent({
  props: {
    title: { type: String, required: true },
    message: { type: String, required: true },
  },
  emits: ["focus"],
  template: `
    <div class="empty-state">
      <div class="empty-icon">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M8 6h13" />
          <path d="M8 12h13" />
          <path d="M8 18h13" />
          <path d="m3 6 1 1 2-2" />
          <path d="m3 12 1 1 2-2" />
          <path d="m3 18 1 1 2-2" />
        </svg>
      </div>
      <h3>{{ title }}</h3>
      <p>{{ message }}</p>
      <button type="button" @click="$emit('focus')">Create Task</button>
    </div>
  `,
});

const TaskCard = defineComponent({
  props: {
    todo: { type: Object, required: true },
    projects: { type: Array, required: true },
  },
  emits: ["toggle", "delete", "save", "subtask-add", "subtask-toggle"],
  data() {
    return {
      editing: false,
      title: this.todo.title,
      notes: this.todo.notes || "",
      projectId: this.todo.project?.id || "",
      status: this.todo.status || "backlog",
      priority: this.todo.priority || "medium",
      dueDate: this.todo.due_date || "",
      recurrence: this.todo.recurrence || "none",
      reminderAt: this.toLocalInput(this.todo.reminder_at),
      subtaskTitle: "",
    };
  },
  methods: {
    toLocalInput(value) {
      if (!value) return "";
      const date = new Date(value);
      const offset = date.getTimezoneOffset();
      return new Date(date.getTime() - offset * 60 * 1000).toISOString().slice(0, 16);
    },
    save() {
      this.$emit("save", {
        todo: this.todo,
        payload: {
          title: this.title,
          notes: this.notes,
          project_id: this.projectId || null,
          status: this.status,
          completed: this.status === "done",
          priority: this.priority,
          due_date: this.dueDate || null,
          recurrence: this.recurrence,
          reminder_at: this.reminderAt ? new Date(this.reminderAt).toISOString() : null,
        },
      });
      this.editing = false;
    },
    addSubtask() {
      if (!this.subtaskTitle) return;
      this.$emit("subtask-add", { todo: this.todo, title: this.subtaskTitle });
      this.subtaskTitle = "";
    },
  },
  template: `
    <div>
      <template v-if="editing">
        <div class="edit-grid">
          <input v-model.trim="title" placeholder="Task title" />
          <select v-model="projectId">
            <option value="">No Project</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">{{ project.name }}</option>
          </select>
          <select v-model="status">
            <option value="backlog">Backlog</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
          <select v-model="priority">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <input v-model="dueDate" type="date" />
          <select v-model="recurrence">
            <option value="none">No Repeat</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
          <input v-model="reminderAt" type="datetime-local" />
          <textarea v-model.trim="notes" placeholder="Notes"></textarea>
          <div class="edit-actions">
            <button type="button" @click="save">Save</button>
            <button type="button" class="muted-button" @click="editing = false">Cancel</button>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="task-card-main">
          <label class="todo-check">
            <input type="checkbox" :checked="todo.completed" @change="$emit('toggle', todo)" />
            <span>
              <strong :class="{ done: todo.completed }">{{ todo.title }}</strong>
              <small>{{ todo.project?.name || "No Project" }} - {{ todo.due_date || "No due date" }}</small>
            </span>
          </label>
          <div class="task-actions">
            <span class="priority-badge" :class="todo.priority || 'medium'">{{ todo.priority || "medium" }}</span>
            <button type="button" @click="editing = true">Edit</button>
            <button type="button" class="danger-button" @click="$emit('delete', todo)">Delete</button>
          </div>
        </div>
        <p v-if="todo.notes" class="task-notes">{{ todo.notes }}</p>
        <div class="subtasks">
          <label v-for="subtask in todo.subtasks" :key="subtask.id">
            <input type="checkbox" :checked="subtask.completed" @change="$emit('subtask-toggle', subtask)" />
            <span :class="{ done: subtask.completed }">{{ subtask.title }}</span>
          </label>
          <form @submit.prevent="addSubtask">
            <input v-model.trim="subtaskTitle" placeholder="Add subtask..." />
            <button type="submit">Add</button>
          </form>
        </div>
      </template>
    </div>
  `,
});

export default {
  components: { EmptyState, TaskCard },
  data() {
    return {
      todos: [],
      projects: [],
      user: {},
      error: "",
      searchQuery: "",
      selectedProjectId: "all",
      activeView: "list",
      dragTodoId: null,
      isUserMenuOpen: false,
      newTodo: "",
      newProjectId: "",
      newProjectName: "",
      newProjectColor: "#1a73e8",
      newPriority: "medium",
      newStatus: "backlog",
      newDueDate: "",
      newRecurrence: "none",
      newReminderAt: "",
      newNotes: "",
      toasts: [],
      toastId: 0,
      views: [
        { label: "List", value: "list" },
        { label: "Kanban", value: "kanban" },
        { label: "Calendar", value: "calendar" },
        { label: "Analytics", value: "analytics" },
      ],
      kanbanColumns: [
        { label: "Backlog", value: "backlog" },
        { label: "In Progress", value: "in_progress" },
        { label: "Done", value: "done" },
      ],
    };
  },
  computed: {
    displayName() {
      return this.user.username || this.user.email || "User";
    },
    completedCount() {
      return this.todos.filter((todo) => todo.completed).length;
    },
    activeCount() {
      return this.todos.length - this.completedCount;
    },
    overdueCount() {
      return this.todos.filter((todo) => this.isOverdue(todo)).length;
    },
    highPriorityOpen() {
      return this.todos.filter((todo) => todo.priority === "high" && !todo.completed).length;
    },
    recurringCount() {
      return this.todos.filter((todo) => todo.recurrence && todo.recurrence !== "none").length;
    },
    tasksWithSubtasks() {
      return this.todos.filter((todo) => todo.subtasks?.length).length;
    },
    progressPercent() {
      if (!this.todos.length) return 0;
      return Math.round((this.completedCount / this.todos.length) * 100);
    },
    visibleTodos() {
      const query = this.searchQuery.toLowerCase();
      return this.todos.filter((todo) => {
        const projectMatches = this.selectedProjectId === "all"
          || todo.project?.id === this.selectedProjectId;
        const textMatches = !query
          || todo.title.toLowerCase().includes(query)
          || (todo.notes || "").toLowerCase().includes(query)
          || (todo.project?.name || "").toLowerCase().includes(query);
        return projectMatches && textMatches;
      });
    },
    groupedSections() {
      const groups = [
        { key: "overdue", label: "Overdue", todos: [] },
        { key: "today", label: "Today", todos: [] },
        { key: "upcoming", label: "Upcoming", todos: [] },
        { key: "no-date", label: "No Due Date", todos: [] },
        { key: "completed", label: "Completed", todos: [] },
      ];
      this.visibleTodos.forEach((todo) => {
        if (todo.completed) groups[4].todos.push(todo);
        else if (!todo.due_date) groups[3].todos.push(todo);
        else if (this.isOverdue(todo)) groups[0].todos.push(todo);
        else if (todo.due_date === this.todayString()) groups[1].todos.push(todo);
        else groups[2].todos.push(todo);
      });
      return groups.filter((group) => group.todos.length);
    },
    calendarDays() {
      const now = new Date();
      const year = now.getFullYear();
      const month = now.getMonth();
      const first = new Date(year, month, 1);
      const start = new Date(first);
      start.setDate(first.getDate() - first.getDay());
      return Array.from({ length: 42 }, (_, index) => {
        const date = new Date(start);
        date.setDate(start.getDate() + index);
        const value = this.toDateString(date);
        return {
          date: value,
          day: date.getDate(),
          currentMonth: date.getMonth() === month,
          todos: this.visibleTodos.filter((todo) => todo.due_date === value),
        };
      });
    },
    emptyTitle() {
      return this.searchQuery ? "No matching tasks" : "No tasks yet";
    },
    emptyMessage() {
      return this.searchQuery
        ? "Try a different search or project filter."
        : "Create a task with a project, priority, due date, and subtasks.";
    },
  },
  methods: {
    getAuthHeader() {
      return { headers: { Authorization: `Bearer ${localStorage.getItem("access")}` } };
    },
    async fetchUser() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/me/", this.getAuthHeader());
        this.user = response.data;
      } catch (err) {
        this.handleRequestError(err, "Unable to load user details.");
      }
    },
    async fetchProjects() {
      const response = await axios.get("http://127.0.0.1:8000/api/projects/", this.getAuthHeader());
      this.projects = response.data;
    },
    async fetchTodos() {
      const response = await axios.get("http://127.0.0.1:8000/api/todos/", this.getAuthHeader());
      this.todos = response.data;
    },
    async addProject() {
      try {
        await axios.post(
          "http://127.0.0.1:8000/api/projects/",
          { name: this.newProjectName, color: this.newProjectColor },
          this.getAuthHeader()
        );
        this.newProjectName = "";
        await this.fetchProjects();
        this.showToast("Project added", "success");
      } catch (err) {
        this.handleRequestError(err, "Unable to add project.");
      }
    },
    async addTodo() {
      try {
        await axios.post(
          "http://127.0.0.1:8000/api/todos/",
          {
            title: this.newTodo,
            notes: this.newNotes,
            project_id: this.newProjectId || null,
            status: this.newStatus,
            completed: this.newStatus === "done",
            priority: this.newPriority,
            due_date: this.newDueDate || null,
            recurrence: this.newRecurrence,
            reminder_at: this.newReminderAt ? new Date(this.newReminderAt).toISOString() : null,
          },
          this.getAuthHeader()
        );
        this.newTodo = "";
        this.newNotes = "";
        this.newPriority = "medium";
        this.newStatus = "backlog";
        this.newDueDate = "";
        this.newRecurrence = "none";
        this.newReminderAt = "";
        await this.fetchTodos();
        this.recordActivity("created", "Task added");
        this.showToast("Task added", "success");
      } catch (err) {
        this.handleRequestError(err, "Unable to add task.");
      }
    },
    async saveTodo({ todo, payload }) {
      try {
        await axios.patch(`http://127.0.0.1:8000/api/todos/${todo.id}/`, payload, this.getAuthHeader());
        await this.fetchTodos();
        this.recordActivity("updated", `Updated ${payload.title}`);
        this.showToast("Task updated", "success");
      } catch (err) {
        this.handleRequestError(err, "Unable to update task.");
      }
    },
    async toggleTodo(todo) {
      await this.saveTodo({
        todo,
        payload: {
          completed: !todo.completed,
          status: !todo.completed ? "done" : "backlog",
        },
      });
    },
    async deleteTodo(todo) {
      try {
        await axios.delete(`http://127.0.0.1:8000/api/todos/${todo.id}/`, this.getAuthHeader());
        await this.fetchTodos();
        this.recordActivity("deleted", `Deleted ${todo.title}`);
        this.showToast("Task deleted", "success");
      } catch (err) {
        this.handleRequestError(err, "Unable to delete task.");
      }
    },
    async addSubtask({ todo, title }) {
      try {
        await axios.post(
          "http://127.0.0.1:8000/api/subtasks/",
          { todo: todo.id, title },
          this.getAuthHeader()
        );
        await this.fetchTodos();
      } catch (err) {
        this.handleRequestError(err, "Unable to add subtask.");
      }
    },
    async toggleSubtask(subtask) {
      try {
        await axios.patch(
          `http://127.0.0.1:8000/api/subtasks/${subtask.id}/`,
          { completed: !subtask.completed },
          this.getAuthHeader()
        );
        await this.fetchTodos();
      } catch (err) {
        this.handleRequestError(err, "Unable to update subtask.");
      }
    },
    async dropTodo(status) {
      const todo = this.todos.find((item) => item.id === this.dragTodoId);
      if (!todo) return;
      await this.saveTodo({
        todo,
        payload: { status, completed: status === "done" },
      });
      this.dragTodoId = null;
    },
    todosByStatus(status) {
      return this.visibleTodos.filter((todo) => (todo.status || "backlog") === status);
    },
    applySmartSuggestions() {
      const text = this.newTodo.toLowerCase();
      if (text.includes("urgent") || text.includes("high")) this.newPriority = "high";
      if (text.includes("low priority")) this.newPriority = "low";
      if (text.includes("today")) this.newDueDate = this.todayString();
      if (text.includes("tomorrow")) {
        const date = new Date();
        date.setDate(date.getDate() + 1);
        this.newDueDate = this.toDateString(date);
      }
      if (text.includes("daily")) this.newRecurrence = "daily";
      if (text.includes("weekly")) this.newRecurrence = "weekly";
      if (text.includes("monthly")) this.newRecurrence = "monthly";
    },
    projectName(todo) {
      return todo.project?.name || "No Project";
    },
    priorityLabel(priority) {
      return ({ low: "Low", medium: "Medium", high: "High" }[priority] || "Medium");
    },
    dueLabel(todo) {
      if (!todo.due_date) return "No due date";
      if (this.isOverdue(todo)) return `Overdue ${todo.due_date}`;
      return `Due ${todo.due_date}`;
    },
    isOverdue(todo) {
      return Boolean(!todo.completed && todo.due_date && todo.due_date < this.todayString());
    },
    todayString() {
      return this.toDateString(new Date());
    },
    toDateString(date) {
      const offset = date.getTimezoneOffset();
      return new Date(date.getTime() - offset * 60 * 1000).toISOString().slice(0, 10);
    },
    focusNewTask() {
      document.querySelector(".add-form input")?.focus();
    },
    recordActivity(type, message) {
      const saved = JSON.parse(localStorage.getItem(ACTIVITY_KEY) || "[]");
      const activity = [{ id: Date.now(), type, message, createdAt: new Date().toISOString() }, ...saved].slice(0, 12);
      localStorage.setItem(ACTIVITY_KEY, JSON.stringify(activity));
    },
    showToast(message, type = "success") {
      const id = ++this.toastId;
      this.toasts.push({ id, message, type });
      setTimeout(() => {
        this.toasts = this.toasts.filter((toast) => toast.id !== id);
      }, 4200);
    },
    showPendingToast() {
      const pendingToast = sessionStorage.getItem("toast");
      if (!pendingToast) return;

      sessionStorage.removeItem("toast");

      try {
        const toast = JSON.parse(pendingToast);
        this.showToast(toast.message, toast.type);
      } catch (err) {
        this.showToast("Action completed.", "success");
      }
    },
    handleRequestError(err, message) {
      this.error = message;
      this.showToast(message, "error");
      if (err.response?.status === 401) this.logout();
    },
    toggleUserMenu() {
      this.isUserMenuOpen = !this.isUserMenuOpen;
    },
    closeUserMenu() {
      this.isUserMenuOpen = false;
    },
    goToProfile() {
      this.$router.push("/profile");
    },
    goToResetPassword() {
      this.$router.push({ path: "/password-reset", query: { email: this.user.email } });
    },
    logout() {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      this.$router.push("/");
    },
  },
  async mounted() {
    this.showPendingToast();
    await Promise.all([this.fetchUser(), this.fetchProjects(), this.fetchTodos()]);
  },
};
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: #f8fafd;
  color: #202124;
}

svg {
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.toast-stack {
  position: fixed;
  top: 18px;
  right: 18px;
  z-index: 30;
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
}

.toast.error {
  border-left-color: #ea4335;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 14px 28px;
  background: #ffffff;
  border-bottom: 1px solid #e8eaed;
  box-shadow: none;
}

.eyebrow {
  margin: 0 0 4px;
  color: #5f6368;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1,
h2,
h3,
p {
  margin: 0;
}

h1,
h2,
h3 {
  color: #202124;
}

h1 {
  font-size: 24px;
  font-weight: 500;
}

.user-menu {
  position: relative;
}

.user-button {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 240px;
  padding: 8px 10px;
  background: #ffffff;
  border: 1px solid #dadce0;
  border-radius: 8px;
  color: #202124;
  cursor: pointer;
}

.user-button:hover {
  background: #f8fafd;
  box-shadow: 0 1px 2px rgba(60, 64, 67, 0.14);
}

.user-avatar {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #1a73e8;
  color: #ffffff;
}

.user-avatar svg {
  width: 21px;
  height: 21px;
}

.user-copy {
  display: grid;
  min-width: 0;
  text-align: left;
}

.user-copy strong,
.user-copy small,
.dropdown-user strong,
.dropdown-user span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-copy strong {
  font-size: 14px;
}

.user-copy small,
.dropdown-user span {
  color: #5f6368;
  font-size: 12px;
}

.chevron-icon {
  width: 18px;
  height: 18px;
  margin-left: auto;
  color: #5f6368;
}

.dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 250px;
  padding: 8px;
  background: #ffffff;
  border: 1px solid #dadce0;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(60, 64, 67, 0.18);
}

.dropdown-user {
  display: grid;
  gap: 3px;
  padding: 10px 12px 12px;
  margin-bottom: 6px;
  border-bottom: 1px solid #e8eaed;
}

.dropdown button {
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: #202124;
  cursor: pointer;
  font-size: 14px;
  text-align: left;
}

.dropdown button:hover {
  background: #f1f3f4;
}

.dashboard-shell {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 24px 0 48px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.summary-card,
.progress-panel,
.workspace-panel {
  background: #ffffff;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  box-shadow: none;
}

.summary-card {
  position: relative;
  overflow: hidden;
  padding: 16px;
}

.summary-card::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: #4285f4;
}

.summary-card:nth-child(2)::before {
  background: #fbbc04;
}

.summary-card:nth-child(3)::before {
  background: #34a853;
}

.summary-card:nth-child(4)::before {
  background: #ea4335;
}

.summary-card span,
.analytics-card span {
  display: block;
  margin-bottom: 8px;
  color: #5f6368;
  font-size: 13px;
  font-weight: 500;
}

.summary-card strong,
.analytics-card strong {
  color: #202124;
  font-size: 28px;
  line-height: 1;
  font-weight: 500;
}

.summary-card.warning strong {
  color: #ea4335;
}

.progress-panel {
  display: grid;
  grid-template-columns: minmax(180px, 240px) 1fr;
  align-items: center;
  gap: 18px;
  padding: 16px;
  margin-bottom: 12px;
}

.progress-panel h2 {
  margin-bottom: 4px;
  font-size: 18px;
  font-weight: 500;
}

.progress-panel p,
.empty-state p {
  color: #5f6368;
  font-size: 14px;
}

.progress-track {
  overflow: hidden;
  height: 8px;
  background: #e8f0fe;
  border-radius: 999px;
}

.progress-track span {
  display: block;
  height: 100%;
  background: #1a73e8;
  border-radius: inherit;
}

.workspace-panel {
  padding: 18px;
}

.workspace-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 16px;
}

.view-tabs,
.projects-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.view-tabs {
  padding: 4px;
  background: #f1f3f4;
  border-radius: 8px;
}

.view-tabs button,
.project-chip {
  border: none;
  border-radius: 7px;
  cursor: pointer;
  font-weight: 500;
}

.view-tabs button {
  padding: 9px 12px;
  background: transparent;
  color: #5f6368;
}

.view-tabs button.active {
  background: #ffffff;
  color: #1a73e8;
  box-shadow: 0 1px 2px rgba(60, 64, 67, 0.16);
}

.search-field {
  display: flex;
  align-items: center;
  gap: 10px;
  width: min(420px, 100%);
  padding: 0 14px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: #f1f3f4;
}

.search-field:focus-within {
  background: #ffffff;
  border-color: #dadce0;
  box-shadow: 0 1px 6px rgba(60, 64, 67, 0.2);
}

.search-field svg {
  width: 18px;
  height: 18px;
  color: #5f6368;
}

.search-field input {
  width: 100%;
  min-width: 0;
  padding: 13px 0;
  border: none;
  background: transparent;
  outline: none;
}

.projects-row,
.project-form,
.add-form {
  margin-bottom: 14px;
}

.project-chip {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid #dadce0;
  color: #3c4043;
}

.project-chip span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.project-chip.active {
  background: #e8f0fe;
  border-color: #d2e3fc;
  color: #1967d2;
}

.project-form {
  display: grid;
  grid-template-columns: minmax(180px, 1fr) 54px 132px;
  gap: 10px;
}

.add-form {
  display: grid;
  grid-template-columns: minmax(220px, 1.4fr) repeat(6, minmax(120px, 1fr)) 110px;
  gap: 10px;
}

.add-form textarea {
  grid-column: 1 / -2;
  min-height: 72px;
  resize: vertical;
}

input,
select,
textarea {
  min-width: 0;
  padding: 12px 13px;
  border: 1px solid #dadce0;
  border-radius: 8px;
  background: #ffffff;
  color: #202124;
  font: inherit;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #1a73e8;
  outline: 3px solid rgba(26, 115, 232, 0.14);
}

button {
  font: inherit;
}

.project-form button,
.add-form button,
.edit-actions button,
.empty-state button,
.subtasks button,
.task-actions button {
  padding: 11px 12px;
  background: #1a73e8;
  border: none;
  border-radius: 8px;
  color: #ffffff;
  cursor: pointer;
  font-weight: 500;
}

.project-form button:hover,
.add-form button:hover,
.edit-actions button:hover,
.empty-state button:hover,
.subtasks button:hover,
.task-actions button:hover {
  background: #1967d2;
  box-shadow: 0 1px 2px rgba(60, 64, 67, 0.2);
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.task-sections {
  display: grid;
  gap: 20px;
}

.task-section {
  display: grid;
  gap: 10px;
}

.section-title,
.column-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.section-title h3,
.column-title h3 {
  font-size: 15px;
  font-weight: 500;
}

.section-title span,
.column-title span {
  padding: 4px 8px;
  background: #f1f3f4;
  border-radius: 999px;
  color: #5f6368;
  font-size: 12px;
  font-weight: 500;
}

.task-card,
.kanban-card,
.analytics-card {
  padding: 14px;
  background: #ffffff;
  border: 1px solid #e8eaed;
  border-radius: 8px;
}

.task-card:hover,
.kanban-card:hover,
.analytics-card:hover {
  box-shadow: 0 1px 3px rgba(60, 64, 67, 0.18);
}

.task-card-main {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.todo-check {
  display: flex;
  gap: 11px;
  min-width: 0;
  cursor: pointer;
}

.todo-check input {
  width: 18px;
  height: 18px;
  margin-top: 3px;
  accent-color: #1a73e8;
}

.todo-check span {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.todo-check strong {
  overflow-wrap: anywhere;
  color: #202124;
  font-weight: 500;
}

.done {
  color: #5f6368;
  text-decoration: line-through;
}

.todo-check small,
.kanban-card small {
  color: #5f6368;
  font-size: 12px;
}

.task-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.task-actions button {
  padding: 8px 10px;
}

.task-actions .danger-button {
  background: #fce8e6;
  border: 1px solid #fad2cf;
  color: #a50e0e;
}

.task-actions .danger-button:hover {
  background: #fad2cf;
}

.priority-badge {
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.priority-badge.low {
  background: #e6f4ea;
  color: #137333;
}

.priority-badge.medium {
  background: #fef7e0;
  color: #b06000;
}

.priority-badge.high {
  background: #fce8e6;
  color: #a50e0e;
}

.task-notes {
  margin: 10px 0;
  color: #5f6368;
  font-size: 14px;
  line-height: 1.45;
}

.subtasks {
  display: grid;
  gap: 8px;
  margin-top: 10px;
  padding-left: 30px;
}

.subtasks label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #5f6368;
  font-size: 13px;
}

.subtasks form {
  display: grid;
  grid-template-columns: minmax(140px, 1fr) 70px;
  gap: 8px;
}

.edit-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(120px, 1fr));
  gap: 10px;
}

.edit-grid textarea {
  grid-column: 1 / -1;
  min-height: 80px;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.edit-actions .muted-button {
  background: #f1f3f4;
  color: #3c4043;
}

.kanban-view {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.kanban-column {
  display: grid;
  align-content: start;
  gap: 10px;
  min-height: 360px;
  padding: 12px;
  background: #f8fafd;
  border: 1px solid #e8eaed;
  border-radius: 8px;
}

.kanban-card {
  display: grid;
  gap: 8px;
  cursor: grab;
}

.calendar-view {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border: 1px solid #e8eaed;
  border-radius: 8px;
  overflow: hidden;
}

.calendar-day {
  min-height: 118px;
  padding: 10px;
  background: #ffffff;
  border-right: 1px solid #e8eaed;
  border-bottom: 1px solid #e8eaed;
}

.calendar-day.muted {
  background: #f8fafd;
  color: #9aa0a6;
}

.calendar-task {
  display: block;
  width: 100%;
  margin-top: 7px;
  padding: 7px;
  border: none;
  border-radius: 6px;
  background: #e8f0fe;
  color: #1967d2;
  cursor: pointer;
  font-size: 12px;
  text-align: left;
}

.calendar-task.high {
  background: #fce8e6;
  color: #a50e0e;
}

.calendar-task.low {
  background: #e6f4ea;
  color: #137333;
}

.analytics-view {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}

.empty-state {
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 42px 16px;
  background: #ffffff;
  border: 1px dashed #dadce0;
  border-radius: 8px;
  text-align: center;
}

.empty-icon {
  display: grid;
  place-items: center;
  width: 54px;
  height: 54px;
  background: #e8f0fe;
  border-radius: 50%;
  color: #1a73e8;
}

.empty-icon svg {
  width: 28px;
  height: 28px;
}

.error {
  margin: 0 0 14px;
  color: #ea4335;
  font-size: 13px;
}

@media (max-width: 1100px) {
  .summary-grid,
  .analytics-view {
    grid-template-columns: repeat(2, 1fr);
  }

  .add-form,
  .edit-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .add-form textarea {
    grid-column: 1 / -1;
  }

  .kanban-view {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .app-header,
  .workspace-top,
  .task-card-main,
  .progress-panel {
    align-items: stretch;
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .summary-grid,
  .analytics-view,
  .project-form,
  .add-form,
  .edit-grid,
  .calendar-view {
    grid-template-columns: 1fr;
  }

  .user-button,
  .search-field {
    width: 100%;
    min-width: 0;
  }

  .dropdown {
    left: 0;
    right: auto;
    width: 100%;
  }

  .task-actions {
    justify-content: space-between;
  }
}
</style>
