import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

// `yarn dev` proxies Frappe on VITE_SITE (e.g. http://tcf.local:8000) so the session cookie works.
const site = process.env.VITE_SITE || "http://localhost:8000";

export default defineConfig({
	plugins: [vue()],
	resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
	server: {
		port: 8081,
		proxy: {
			"^/(api|assets|files|private|login|socket.io)": { target: site, changeOrigin: true },
		},
	},
	build: {
		outDir: "../tcf_hr/public/frontend",
		emptyOutDir: true,
		target: "es2020",
	},
});
