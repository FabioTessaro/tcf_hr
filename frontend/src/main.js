import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./styles/base.css";

try {
	window.boot = JSON.parse(document.getElementById("boot").textContent);
} catch {
	window.boot = {}; // `yarn dev`: the Jinja placeholder is not rendered
}

createApp(App).use(createPinia()).use(router).mount("#app");
