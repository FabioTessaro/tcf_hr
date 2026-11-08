### TCF HR

System layer for Human Resources Management

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app tcf_hr
```

### HR app (`/hrms`)

Vue 3 SPA in `frontend/`, served at `/hrms` (replaces the hrms employee app and roster; `/hr` redirects to `/hrms/roster`).

- Backend: `tcf_hr/api/session.py` (bootstrap + capabilities), `tcf_hr/api/gateway.py` (allowlisted document API, configured in `tcf_hr/config/gateway.json`), `tcf_hr/policy.py` (per-employee rules such as `can_check_in`).
- Build: `bench build --app tcf_hr` runs `yarn install` and `yarn build`; output goes to `tcf_hr/public/frontend` and `tcf_hr/www/hrms.html` (both gitignored). Commit `frontend/yarn.lock`.
- Dev: `cd frontend && VITE_SITE=http://<site>:8000 yarn dev` (proxies Frappe so the session cookie works).
- Check-in addresses: `tcf_hr/geocoding.py` looks addresses up on the server through a Nominatim-compatible service (default: public OpenStreetMap Nominatim, light use only). Set `tcf_hr_geocoder` in the site config to use LocationIQ or a self-hosted instance; see the module docstring.
- Brand tokens come from tcf_web (`/assets/tcf_web/components/tokens/tokens.css`).

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/tcf_hr
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

agpl-3.0
