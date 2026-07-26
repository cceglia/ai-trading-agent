import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "./views/Dashboard.vue";
import Detail from "./views/Detail.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "dashboard", component: Dashboard },
    { path: "/run/:symbol/:year/:month/:day/:file", name: "detail", component: Detail },
  ],
});

export default router;
