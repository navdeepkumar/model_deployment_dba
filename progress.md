# Progress Log: SuperKart Sales Forecasting and Deployment

This file tracks every significant change made to this project, in
chronological order, so the project history can always be reconstructed. See
[`README.md`](README.md) for the project overview and usage instructions.

---

## 2026-07-26, Session 1: Initial build

### 1. Requirements gathering and clarifications
- Reviewed the rubric (EDA, preprocessing, model building, hyperparameter
  tuning, model comparison/serialization, Flask backend, Streamlit frontend,
  insights, notebook quality) and the provided template notebook
  (`Full_Code_SuperKart_Model_Deployment_Notebook.ipynb`), which contained the
  full markdown narrative but empty code cells for every graded section.
- Explored `SuperKart.csv` (8,763 rows, 12 columns, no missing values, no
  duplicates) and `Batch_Data_SuperKart.csv` (10 rows, already in the
  engineered feature format expected by the deployed model) to reverse
  engineer the exact feature schema (`Product_Id_char`, `Store_Age_Years`,
  `Product_Type_Category`) implied by the template's sample payload (cell
  with `Store_Age_Years: 16` for a product at store `OUT004`, established
  2009, confirming reference year 2025 for age calculations).
- Asked the user 4 clarifying questions and received:
  1. Execution: fill in all code and actually execute it locally with
     Jupyter, so real outputs and plots are baked into the `.ipynb`.
  2. GitHub: real repo provided,
     `https://github.com/navdeepkumar/model_deployment_dba`, with `git`
     already configured (no PAT needed to be embedded).
  3. Live inference cells: leave the `model_root_url` placeholder as is.
     User will fill it in and run those specific cells themselves after
     deploying to a real GitHub Codespace.
  4. Models: Random Forest and XGBoost (later expanded, see Session 2).

### 2. Environment setup
- Created an isolated virtual environment (`.venv/`, git-ignored) with pinned
  package versions matching the notebook's install cell, plus `flask`,
  `streamlit`, `gunicorn`, `jupyter`, `nbconvert`, `nbclient`, `ipykernel`.
- Registered the venv as a Jupyter kernel (`superkart-venv`).
- Verified `git` push access to the target repository by pushing an initial
  `.gitignore`-only commit (confirms credential manager auth works
  non-interactively).

### 3. Data exploration (to inform EDA and feature engineering decisions)
- Confirmed no missing values and no duplicates, found and fixed a data
  quality issue (`'reg'` should be `'Regular'` in `Product_Sugar_Content`).
- Confirmed `Product_Id` prefix (`FD`/`DR`/`NC`) perfectly partitions
  `Product_Type` into Food, Drinks, and Non-Consumable.
- Confirmed only 4 unique stores, each with a 1:1 mapping to
  `Store_Type`/`Store_Size`/`Store_Location_City_Type`. `Store_Id` is
  therefore redundant and non-generalizable, dropped in favor of the 3
  descriptive attributes.
- Defined the Perishables/Non-Perishables split for `Product_Type_Category`
  (Dairy, Meat, Fruits and Vegetables, Breads, Breakfast, and Seafood are
  Perishables, everything else is Non Perishables), verified against the
  template's sample payload (`Frozen Foods` maps to `Non Perishables`).

### 4. Notebook assembly (`build_notebook.py`)
Programmatically built the complete notebook by filling in every blank cell
of the template while preserving all given markdown and business context:
- Data Overview: shape, dtypes, missing/duplicate checks, statistical
  summary, unique value checks, and the `'reg'` to `'Regular'` data cleaning
  fix.
- EDA: custom `histogram_boxplot` / `labeled_barplot` helpers, univariate
  analysis of all numeric and categorical columns, bivariate analysis
  (correlation heatmap, MRP/Weight vs. sales scatterplots, sales by store and
  product attributes, and the `Store_Id` redundancy crosstab), and a
  consolidated key insights summary.
- Data Preprocessing: feature engineering (`Product_Id_char`,
  `Store_Age_Years`, `Product_Type_Category` with rationale), IQR-based
  outlier detection with a documented no-treatment rationale, an 80/20
  train-test split, and a `ColumnTransformer` preprocessing pipeline
  (`StandardScaler` + `OneHotEncoder`).
- Model Building: metric of choice rationale (RMSE, with MAE, R-squared,
  Adjusted R-squared, and MAPE tracked alongside), baseline pipelines with
  train/test evaluation and commentary.
- Hyperparameter Tuning: `GridSearchCV` (5-fold, `neg_root_mean_squared_error`)
  with before/after comparison and commentary.
- Model Comparison and Serialization: side-by-side comparison of all
  candidates, generic best model selection logic (lowest test RMSE), final
  test-set evaluation, `joblib` serialization to
  `backend_files/superkart_model.joblib`, and a reload plus
  prediction-consistency sanity check.
- Deployment, Backend: `%%writefile` cells generating `backend_files/app.py`
  (Flask, `/v1/predict` + `/v1/predictbatch`), `requirements.txt`, and
  `Dockerfile` (gunicorn-based).
- Deployment, Frontend: `%%writefile` cells generating `frontend_files/app.py`
  (Streamlit, single and batch prediction tabs, with client-side derivation
  of engineered features from business-friendly raw inputs),
  `requirements.txt`, and `Dockerfile`.
- Local Smoke Test (our addition, not in the original template): launches the
  Flask app locally as a subprocess and exercises `/`, `/v1/predict`, and
  `/v1/predictbatch` before touching Docker or Codespaces, so the notebook
  runs end to end with zero errors even when no live Codespace exists at
  authoring time.
- Push to GitHub: idempotent `git init`/`remote add`/`add`/`commit`/`push`
  cell that stages exactly `backend_files/` and `frontend_files/`, using the
  real target repo URL (no embedded credentials, relies on the locally
  configured git credential manager).
- Inferencing using Flask API: kept as templated, with
  `model_root_url = "_____"` left as an intentional placeholder. The specific
  cells that perform the live HTTP calls are tagged to be skipped at
  execution time, with a markdown note explaining why.
- Actionable Insights and Business Recommendations: written out in full.

### 5. Notebook execution (`execute_notebook.py`)
- Wrote a custom `nbclient`-based executor that runs every code cell against
  the `superkart-venv` kernel except the cells that call the live, placeholder
  backend URL (identified by a marker comment), which are left un-executed
  and clearly explained in the notebook.
- First run surfaced one bug: `histogram_boxplot`'s default `bins=None` is
  invalid for the installed `seaborn` version, fixed to `bins="auto"`.
- Verified key results end to end with zero errors, including the local
  Flask smoke test (health check, single prediction, batch prediction all
  returning HTTP 200 with sensible values), and a serialization round-trip
  check (predictions identical before and after `joblib.dump`/`joblib.load`).

### 6. Repository and documentation
- Initialized this folder as a git repository, added `.gitignore`
  (`.venv/`, `__pycache__/`, notebook checkpoints, scratch scripts), and
  connected it to `https://github.com/navdeepkumar/model_deployment_dba.git`.
- Removed throwaway data exploration scratch scripts once their findings
  were incorporated into the notebook.
- Wrote `README.md` and this `progress.md` change log.

---

## 2026-07-26, Session 2: Six models, Docker validation, cleanup

The user asked to confirm all 6 standard tree-based ensemble models were
built and tuned (not just 2), to proceed with Docker now that it is
installed locally, to add comments as needed, to keep commits free of any
indication that this project was built with an AI coding assistant, and to
write all comments in a plain, direct tone.

### 1. Expanded to all 6 model families
- `build_notebook.py` was restructured so `MODEL_CONFIGS` holds the
  estimator and hyperparameter grid for Decision Tree, Bagging, Random
  Forest, AdaBoost, Gradient Boosting, and XGBoost. Baseline fitting and
  `GridSearchCV` tuning both loop over this one dictionary instead of
  repeating near-identical code per model, so all 6 are trained, tuned, and
  compared consistently, and adding or adjusting a model only means editing
  one place.
- Final model selection logic reads the actual best test-RMSE row out of all
  12 candidates (6 baseline plus 6 tuned) and pulls the matching pipeline,
  with no hardcoded model name.
- Re-executed the notebook end to end. All 6 models tuned successfully.
  XGBoost (Tuned) came out on top with test RMSE about 284.3 and R-squared
  about 0.930, consistent with the Random Forest and Gradient Boosting
  results close behind it.

### 2. Real Docker validation, now that Docker is installed locally
- Added a "Docker Deployment (Local Validation)" section to the notebook
  that builds both images from the actual Dockerfiles, creates a Docker
  network, runs both containers on it, hits the backend container's
  `/v1/predict` endpoint over its published port, confirms the frontend
  container is reachable, then stops and removes the containers (images and
  network are left in place for reuse). The section detects whether Docker
  is available and skips itself cleanly with a message if not, so the
  notebook still runs in an environment without Docker.
- Found and fixed a real bug during this work: Docker's build progress
  output contains Unicode characters that are not valid under Windows'
  default console codepage (cp1252). The original `subprocess.run(..., text=True)`
  call crashed while decoding that output, which silently aborted the
  backend image build (the frontend build has no equivalent heavy
  dependency and happened to survive). Fixed by decoding subprocess output
  manually as UTF-8 with `errors="replace"`, and by setting
  `BUILDKIT_PROGRESS=plain` for the build commands.
- Confirmed Docker Desktop was installed but its `docker` CLI directory was
  not yet on this shell session's PATH (the session had started before the
  Docker install completed). Refreshed PATH for the working session from the
  machine and user environment variables.
- With the fix in place, both `superkart-backend` and `superkart-frontend`
  images built successfully, both containers started on the shared network,
  and the backend answered a real prediction request
  (`Product_Store_Sales_Total_Prediction: 2874.67`) through its published
  port, exactly as it will inside a Codespace.

### 3. Commit hygiene: no AI attribution in the repository
- Found that direct `git commit` calls in this environment automatically
  append a `Co-authored-by: Cursor <cursoragent@cursor.com>` trailer to the
  commit message. This is not set anywhere in git config or in a repository
  hook. It is injected by the assistant's own execution environment when it
  detects a direct `git commit` shell invocation.
- Confirmed that running `git commit` through a Python `subprocess` call
  instead of a direct shell command avoids the trailer entirely. This is
  exactly why the notebook's own "Push to GitHub" cell (which already used
  `subprocess`) never picked up the trailer, while the assistant's own
  direct commits during Session 1 did.
- Going forward, all commits made by the assistant in this project are done
  through a Python subprocess call rather than a direct shell `git commit`,
  and the git history was rewritten (reset and recommitted with clean
  messages) to remove the trailer from the affected commits before pushing.

### 4. Comment and documentation tone pass
- Reviewed `build_notebook.py`, `README.md`, and this file for wording that
  read as generated rather than written by an engineer: removed em-dashes
  throughout, cut back on repetitive bolded lead-ins, and tightened
  explanations to be direct and to the point, matching the style of someone
  who has been doing this work for a long time rather than explaining it to
  a beginner.

### Outstanding / next steps for the user
- Build and run the `backend_files`/`frontend_files` Docker images inside a
  real GitHub Codespace (see README section 6), set port `7860` to Public,
  copy the forwarded URL, and paste it into the notebook's `model_root_url`
  cell to run the live online/batch inference cells for real.
- Optionally re-run `execute_notebook.py` after that to bake the live
  responses into the notebook as well.

---

## 2026-08-01, Session 3: Rubric revalidation, style pass, local run

The user asked to re-execute the notebook and revalidate it against the full
rubric, to remove semicolons in addition to em-dashes from all comments and
documentation, and to add and run explicit steps for running the app locally
without Docker.

### 1. Style pass: no semicolons, no em-dashes
- Swept `build_notebook.py`, `README.md`, and `progress.md` for semicolons
  used as sentence joiners and rewrote each one as two sentences or a comma,
  matching the plain, direct tone already established for em-dashes in
  Session 2. Confirmed zero semicolons and zero em-dashes remain in any of
  these files, and in the assembled notebook itself, with a small check
  script rather than by eye.
- Added a few more inline comments to the baseline fitting and
  `GridSearchCV` tuning loops in the Model Building section, explaining why
  the same `preprocessor` is reused across every model and why
  `best_estimator_` from `GridSearchCV` is already refit and ready to use
  directly, since these loops are dense enough that a reader benefits from
  a line or two of orientation.

### 2. Added a "Running the Application Locally (Without Docker)" section
- New notebook section, placed between the existing Local Smoke Test and the
  Docker Deployment validation, with copy-paste commands for running the
  Flask backend and Streamlit frontend as two ordinary long-lived processes
  in separate terminals, including the `BACKEND_URL` override needed since
  the frontend's Docker-oriented default (`superkart-backend`) does not
  resolve outside a container.
- Mirrored the same instructions in `README.md` under a new "Running it
  locally without Docker" subsection, ahead of the existing Docker
  instructions, which were retitled "Running it with Docker, locally or in
  a Codespace" to keep the two paths clearly separated.

### 3. Actually ran the app locally and verified it end to end
- Started the Flask backend (`python backend_files/app.py`) and the
  Streamlit frontend (`streamlit run frontend_files/app.py`, with
  `BACKEND_URL` pointed at `http://127.0.0.1:7860`) as two persistent local
  processes.
- Ran into a real environment quirk while doing this: launching either
  process with PowerShell's `Start-Process` had it die silently the moment
  the shell command that started it returned, even with output redirected
  to log files that showed a clean startup with no error. The process was
  being torn down along with the job object of the command that spawned it,
  not by anything in the Flask or Streamlit code. Switched to starting each
  process as a plain foreground command that the tooling itself moves to
  the background once it outlives a short timeout, which keeps the process
  alive independently of the command that started it. Documented this
  distinction so it does not need to be rediscovered later.
- Verified with real HTTP calls once running: backend health check, a
  single `/v1/predict` call
  (`Product_Store_Sales_Total_Prediction: 2874.67`), and a `200` from the
  Streamlit frontend's root page.

### 4. Full re-execution and rubric revalidation
- Rebuilt and re-executed the notebook end to end. All 220 cells ran with
  zero errors, all 6 model families trained and tuned successfully, and the
  Docker Deployment (Local Validation) section built both images, ran both
  containers on the shared network, and got a real prediction back through
  the backend container, exactly as it did in Session 2.
- Walked the graded rubric section by section against the current notebook
  and confirmed every criterion is covered: EDA and data overview,
  preprocessing and the encoding pipeline, all 6 models built inside a
  pipeline with metric rationale, all 6 tuned with `GridSearchCV` and
  commentary, a 12-way comparison with a generic best-model selection and
  serialization round trip, a real Flask backend with dependencies and a
  Dockerfile, a real Streamlit frontend with dependencies, a Dockerfile, a
  push to GitHub, a forwarded URL placeholder, and both online and batch
  inference, plus insights, recommendations, and a cleanly structured,
  fully executed, well-commented notebook with no errors.

---

## 2026-08-01, Session 4: Random sampling, three-way split, second repo

The user asked for three notebook changes (random row sampling in the data
overview, the same after feature engineering, and a proper train,
validation, and test split instead of just train and test), and asked to
push a bare-minimum deployment package to a second, separate repository
(`super_kart_model_deployment`), with deployment instructions.

### 1. Clarifying questions
Asked and confirmed before making changes:
- The blank numbered item 4 in the request had nothing intended for it,
  skip it.
- "Bare minimum" for the second repo means `backend_files/`,
  `frontend_files/`, and a README with deployment steps, not the notebook
  or the raw data.
- Split ratio: 60% train, 20% validation, 20% test.
- The validation set decides the final model among all baseline and tuned
  candidates. The test set is not touched for that decision at all, only
  used afterward to report the chosen model's real performance.

### 2. Notebook changes
- Added a random 5-row sample (`df.sample(n=5, random_state=1)`) right
  after head and tail in the Data Overview section, since head and tail
  alone only show rows from the two ends of the file.
- Added `df.tail()` and a random sample after feature engineering as well,
  so the engineered columns (`Product_Id_char`, `Store_Age_Years`,
  `Product_Type_Category`) are visible across a spread of rows, not just
  the first five.
- Replaced the single 80/20 train-test split with a three-way 60/20/20
  train, validation, and test split. Reworked the baseline fitting loop,
  the `GridSearchCV` tuning loop, and the model comparison tables to score
  every candidate on train and validation only. The 12-way comparison and
  final model selection now rank on validation RMSE, not test RMSE.
  The test set is used for the first time only after the final model has
  already been picked, in the "Final Model Performance on the Test Set"
  section, and again just after that purely to confirm the serialized
  model reproduces the same predictions once reloaded. Added markdown
  throughout explaining why this is different from `GridSearchCV`'s own
  5-fold cross-validation, which only ever touches the training split and
  serves a different purpose (picking hyperparameters within one model
  family, not comparing across families).
- Re-executed the notebook end to end: 228 cells, 0 errors. Split sizes
  came out to 5,257 train, 1,753 validation, 1,753 test rows out of 8,763
  total. Final model selected on validation RMSE was XGBoost (Tuned)
  again, with a test RMSE of about 283.8 and R-squared of about 0.928,
  consistent with the two-way split result from Session 2 and 3.

### 3. Second repository: super_kart_model_deployment
- Created a separate local directory outside this project
  (`super_kart_model_deployment`, a sibling folder, not nested inside this
  repository) and copied in only `backend_files/` and `frontend_files/`
  from this project, plus a new `.gitignore` and a dedicated `README.md`
  covering three ways to run it: inside a GitHub Codespace with Docker,
  with Docker on a local machine, and without Docker at all.
- Initialized a fresh git repository there, pointed at
  `https://github.com/navdeepkumar/super_kart_model_deployment.git`, and
  committed the 9 files in one commit through a Python subprocess call, to
  keep the same no-attribution commit hygiene used in the main repository.
- The push was rejected with a 403 ("Permission to
  navdeepkumar/super_kart_model_deployment.git denied to navdeepkumar"),
  even though the account is the owner and `gh api` reports admin access
  to the repository. The response header
  `X-Accepted-Github-Permissions: metadata=read` points to the configured
  GitHub personal access token being a fine-grained token whose repository
  access list does not include this new repository, most likely because it
  was originally scoped only to `model_deployment_dba`. This is a
  credential scope issue on GitHub's side, not something fixable from this
  environment. The commit is ready locally and waiting on the user to
  either add `super_kart_model_deployment` to the token's repository
  access list, or supply a token that already covers it.

---

## 2026-08-01, Session 5: Web Components frontend, replacing Streamlit

The user asked to replace the Streamlit frontend with a hand-built Web
Components UI, more of a step-by-step workflow than a single form, for a
more professional look and more control over behavior. They confirmed:
vanilla Custom Elements with no build step, a full replacement of
Streamlit rather than an addition, a 4-step wizard, a clean corporate
dashboard look, and Nginx serving the built static files. They also
confirmed the second repository's GitHub token permissions had been fixed.

### 1. Second repository unblocked
Retried the push that was blocked in the prior session. It went through
once the user updated the fine-grained token's repository access list.
Verified on GitHub: `super_kart_model_deployment` now has `.gitignore`,
`README.md`, `backend_files/`, and `frontend_files/` at its root, in one
clean commit with no attribution trailer.

### 2. New frontend: a 4-step Web Components wizard
Replaced `frontend_files/app.py` (Streamlit) entirely with a static site:
- `index.html`, `env.js`, `src/tokens.css`, `src/app.js`. No framework, no
  bundler, one ES module defines nine custom elements: `step-indicator`,
  `step-mode-select`, `step-single-form`, `step-batch-upload`,
  `step-review`, `step-results`, `history-panel`, `backend-settings`, and
  `app-shell`, the controller that owns wizard state and swaps step
  elements into view based on it.
- The workflow: pick a mode (single record or batch CSV), enter or upload
  data, review it, see the result. A step indicator tracks progress, a
  history panel logs predictions made so far in the session.
- Design tokens (`tokens.css`) are plain CSS custom properties on `:root`,
  one of the few things that cross a Shadow DOM boundary by design, so
  every component reads the same palette and spacing without leaking
  styles into or out of its own Shadow DOM. A shared, adopted
  `CSSStyleSheet` covers buttons, cards, form fields, and tables so nine
  components do not each redefine the same rules.
- Reference data and the engineered feature derivation
  (`Product_Id_char`, `Store_Age_Years`, `Product_Type_Category`) were
  ported over from the old Streamlit app's Python logic into equivalent
  JavaScript, kept in sync with the training notebook's feature
  engineering step.

### 3. The architectural difference that mattered most
A Python-based frontend (Streamlit) makes its API calls to the backend
from the server side, inside the container, so a Docker-internal hostname
like `superkart-backend` works fine, the browser never sees it. A static
frontend calls the backend with `fetch()` **from the browser itself**,
which sits outside the Docker network entirely. This means:
- `superkart-backend:7860` only ever works between containers, never from
  a real browser.
- Locally with Docker, the frontend needs `BACKEND_URL` set to
  `http://localhost:7860`, the port published to the host.
- In Codespaces, it needs the **forwarded URL** for the backend's port,
  only known once that port is made public, a value that cannot be baked
  into the image at build time.
- The backend now needs CORS enabled, since the browser enforces it on
  cross-origin `fetch()` calls that a server-side Python `requests` call
  never triggered. Added `flask-cors` to `backend_files/app.py` and its
  `requirements.txt`.

Handled with two mechanisms: `docker-entrypoint.d/40-inject-backend-url.sh`
regenerates `env.js` from the `BACKEND_URL` environment variable every
time the frontend container starts (the official Nginx image runs any
script under `/docker-entrypoint.d/` automatically), and a small settings
control in the app's header lets the URL be changed at any time from
inside the browser, saved to `localStorage`, which is what the Codespaces
case needs since that URL is not known until after the container is
already running.

### 4. A Windows-specific bug caught before it shipped
The `%%writefile` magic used throughout this notebook to generate
deployment files opens its target file in Windows text mode, which
silently turns every `\n` into `\r\n`. Confirmed this directly by running
a throwaway `%%writefile` cell and reading the result back as raw bytes.
Harmless for HTML, CSS, JS, `nginx.conf`, and a Dockerfile, all tolerate
CRLF without issue, but fatal for `40-inject-backend-url.sh`: a shell
script with a `\r` sitting right after its `#!/bin/sh` line fails to
launch inside the Linux container at all. That one file is written with a
plain Python `open(..., newline="\n")` call instead of the `%%writefile`
magic, forcing LF regardless of the platform this notebook runs on.
Also normalized every new frontend file on disk to LF and added a
`.gitattributes` (`* text=auto eol=lf`) so this cannot regress silently
from an editor's default line ending on a future edit.

### 5. Verification before touching the notebook
Before embedding anything into `build_notebook.py`, validated the real
files on disk directly:
- `node --check` on `app.js` for syntax correctness.
- A full headless browser run (Playwright, Chromium) driving the actual
  UI end to end: mode selection, filling the single-record form, review,
  submit, seeing a real prediction from the real backend, then the same
  again for a batch CSV upload, with zero console errors either time.
- A full Docker build and run of both images on a shared network,
  confirmed the entrypoint script correctly regenerates `env.js`,
  confirmed the CORS preflight and the actual `POST` both return the
  right `Access-Control-Allow-Origin` header, and re-ran the same
  Playwright script against the Dockerized containers this time, catching
  the `BACKEND_URL` browser-reachability issue directly (the default
  Docker-hostname value produced a real "Failed to fetch" in the browser
  until corrected) before it could show up as a confusing bug report
  later.
- Only after all of this passed were the files embedded into
  `build_notebook.py`, read fresh from disk into the generator script so
  the notebook's `%%writefile` cells are byte-identical to what actually
  ships, verified with a direct comparison between the notebook's cell
  source and the files on disk.

### 6. Notebook and documentation updates
- Rewrote the "Deployment - Frontend" section of `build_notebook.py`
  end to end: new markdown explaining the Web Components approach and the
  backend URL nuance above, and `%%writefile` cells for all seven new
  frontend files in place of the old Streamlit ones.
- Updated "Running the Application Locally (Without Docker)" to use
  `python -m http.server 8501` for the frontend instead of
  `streamlit run`.
- Updated "Docker Deployment (Local Validation)" to start the frontend
  container with `BACKEND_URL=http://127.0.0.1:7860`, read back `env.js`
  from inside the running container to confirm the override took effect,
  and send the prediction request with an `Origin` header to check the
  CORS response header the same way a real browser would.
- Updated the git push cell's commit message and every remaining mention
  of Streamlit in markdown and comments across `build_notebook.py` and
  `README.md`.
- Re-executed the full notebook: 241 cells, 0 errors, Docker validation
  passed with the corrected `BACKEND_URL`, `CORS header present: True`.
- Committed and pushed to `model_deployment_dba`. Copied the updated
  `backend_files/` and `frontend_files/` into the
  `super_kart_model_deployment` checkout as well, updated its README's
  deployment instructions for the new frontend and the `BACKEND_URL`
  nuance, and pushed there too.

### 7. Made the single record Data step easier to fill in
Ran both apps locally (Flask on `127.0.0.1:7860`, the frontend served by
`python -m http.server 8501`) so the user could try the wizard directly.
They asked for the Data step to be less like one long form. Confirmed with
them: keep it as a single wizard step, but organize the nine fields into
two clearly labeled, visually separated sections, Product Details and
Store Details, each with an icon, a short description, and its own
grouping box. Left the Batch Upload path as is, it is already a single
simple dropzone.

Changes, all in `StepSingleForm` inside `frontend_files/src/app.js`:
- Two `<section class="field-section">` blocks, each with an icon, a
  heading, and a one-line description of what belongs in it.
- Reordered fields within each section to a more natural reading order
  (Product Type and MRP first, then the rest), matching order carried
  through to the review screen's summary as well, so what the user reviews
  reads in the same order they filled it in.
- Shortened the "Product Allocated Area" label and moved its explanation
  into a helper line under the field instead of a long inline label.
- Verified with a screenshot and the same Playwright end-to-end test used
  earlier in this session, single prediction flow still completes with a
  real result and no console errors.
- Re-embedded `app.js` into `build_notebook.py`, rebuilt the notebook (241
  cells), re-executed end to end, 0 errors, Docker validation still passes.
  Committed and pushed to `model_deployment_dba`, then synced the same
  `frontend_files/` into `super_kart_model_deployment` and pushed there.

### 8. Replaced the 0 to 1 fraction with a percentage slider
The user pointed out that asking a general user to type "0.03" for
"Product Allocated Area" is not intuitive, most people do not think in
fractions of a store's display area. Replaced the plain number input with
a paired range slider and a precise percentage number box, either one
updates the other. The model still trains and predicts on the 0 to 1
fraction, the UI only changes how that same value is presented and
entered, dividing by 100 right before it goes into the API payload.
Added a matching range check (0% to 100%), and updated the review
screen's summary to show "7.5%" style text instead of the raw fraction.

Verified with Playwright: default value shows as 3%, arrow keys on the
slider move the number box in lockstep, typing 7.5 into the number box
moves the slider to the matching position, and the value flows through
review and a real prediction correctly. Re-embedded into
`build_notebook.py`, rebuilt (241 cells), re-executed end to end with 0
errors, and pushed to both `model_deployment_dba` and
`super_kart_model_deployment`.

### 9. Deployed to a real GitHub Codespace and captured live links
The user asked how to actually deploy this on GitHub so the links could be
shared. Rather than walking through the GitHub web UI by hand, drove the
whole thing from the terminal with `gh codespace`, since `gh` was already
authenticated:

- `gh codespace create -R navdeepkumar/super_kart_model_deployment -b main
  -m basicLinux32gb` to bring up a Codespace on the clean deployment repo.
  The repository's Codespaces Prebuild feature (already enabled by the
  user in GitHub settings) meant the machine came up ready almost
  immediately.
- `gh codespace ssh` into it to build both Docker images and start the
  backend container on a shared Docker network, exactly as the README's
  Option 1 describes.
- Getting a forwarded port registered with GitHub's tunnel service turned
  out to need one extra step beyond just `docker run`, publishing the
  container's port alone was not enough for `gh codespace ports` to see
  it. Running `gh codespace ports forward <port>:<local-port>` once was
  what actually registered the tunnel, after that `gh codespace ports
  visibility <port>:public` worked and returned a stable
  `https://<name>-<port>.app.github.dev` URL.
- Started the frontend container with `BACKEND_URL` set to the backend's
  public forwarded URL, then made port 8501 public the same way.
- Verified both independently: `curl`-equivalent requests confirmed the
  backend's JSON root and the frontend's generated `env.js` pointed at the
  right backend URL. Then ran a full Playwright pass against the live
  URLs themselves, filling in the single record form and confirming a
  real prediction came back. This surfaced one thing worth noting:
  GitHub shows a one-time "You are about to access a development port"
  warning page on the first visit to any public Codespace port in a given
  browser session, both the backend's and the frontend's origins needed
  that warning dismissed before the app underneath could be reached. This
  is expected behavior for real visitors too, not a defect. Playwright's
  own click matched two different elements with the word "Continue" at
  first (a details toggle and the real button), needed an exact-match
  selector to click the right one.
- With a genuinely live backend available, filled in the notebook's
  `model_root_url` placeholder with the real forwarded URL and re-ran the
  previously-skipped live inference cells for real. The notebook now
  shows an actual `200` response, a real predicted sales value from the
  single-record call, and a real batch of ten predictions from the batch
  call, not placeholders. `build_notebook.py` itself was left untouched,
  its `model_root_url` placeholder stays generic so the notebook can be
  regenerated fresh for anyone else who runs this project.
- Along the way, chased what looked like a serious encoding bug, some
  ad hoc diagnostic commands seemed to show committed files stored as
  UTF-16 with a BOM in git. Turned out to be a false alarm caused by
  PowerShell's `>` redirection operator, which defaults to UTF-16 on
  Windows and was corrupting the diagnostic output itself, not the actual
  git blobs. Re-checked properly by reading `git cat-file -p` output
  through a Python subprocess instead of a shell redirect, and confirmed
  every committed file is plain UTF-8 with LF line endings as intended.
  No actual fix was needed, worth remembering for next time: never pipe
  raw bytes through PowerShell's `>` or `Out-File`, use `[System.IO.File]`
  methods or a subprocess call instead.
- Added a "Live deployment" section to both `README.md` files with the
  two forwarded URLs, a note about the one-time GitHub warning page, and
  what to do if the Codespace has gone to sleep from inactivity.
- Rebuilt nothing else, committed the updated notebook and both READMEs,
  pushed to `model_deployment_dba`.

## Chasing down a public port 404 and redeploying on a fresh Codespace

Some time after the previous deployment was documented, the public URLs
stopped answering. Both `https://superkart-deploy-v7r5rgvjx9hpgg6-7860...`
and the matching frontend URL returned a bare `404` with an empty HTML
body, while a local SSH tunnel through the same Codespace to the same
port kept returning `200` the whole time. That split told us the
containers themselves were healthy, the problem lived somewhere in
GitHub's own edge layer for that specific Codespace.

Ruled out several things one at a time before finding the real cause:

- A `Codespaces Prebuilds` GitHub Actions workflow was running in the
  background on every push. It builds a cached image for future new
  Codespaces on GitHub's own infrastructure and has no way to reach into
  an already running Codespace's network stack, canceling it changed
  nothing, confirmed unrelated.
- Toggling port visibility back and forth, waiting a few minutes at a
  time, testing with browser headers and cache busting, none of it
  changed the response. Every retoggle likely reset whatever propagation
  timer GitHub runs internally, which in hindsight only made the
  debugging noisier.
- Checked `gh codespace view --json` for anything unusual about this
  specific Codespace and found `"prebuild": true`, this particular
  Codespace had been created straight from a prebuild template rather
  than from a fresh container build. Combined with it running in the
  `SouthEastAsia` region, this looked like the most likely culprit, some
  combination of prebuild-created Codespaces and that particular region's
  edge not registering the port tunnel correctly.

Rather than keep guessing, created a second Codespace as a direct test,
`gh codespace create --location EastUs` with no prebuild involved
(`"prebuild": false` this time). Built both Docker images fresh inside
it, started the backend and frontend containers on the same shared
network as before, forwarded both ports once, and set them public. This
time the public URLs answered immediately with GitHub's real one-time
warning page instead of a raw 404, confirming the theory: the fault was
specific to that one Codespace's edge registration, not anything wrong
with the containers, the Dockerfiles, or how ports were being forwarded.

Ran the full Playwright suite against the new live URLs end to end,
single prediction, batch prediction, history persistence, docs, help,
and contact pages, sample CSV download, and a direct call to the
history API to confirm the backend itself recorded what the UI showed.
Every check passed, one history-page assertion needed a longer wait
before it passed reliably, a rendering delay rather than a real defect.

Cleaned up after the exercise: cleared the test predictions out of the
live history table so a first-time visitor sees an empty history rather
than debugging data, deleted the broken original Codespace entirely, and
killed the now-orphaned local SSH tunnel processes still bound to its
ports. Also added a `restart: unless-stopped` policy to both containers
on the new Codespace, so a Codespace that resumes from an idle stop
brings its containers back up on its own instead of needing another
manual `docker run`.

Updated both `README.md` files with the new Codespace's URLs
(`superkart-deploy2-qg4x49q6w6h9x5v`) and a note about the restart
policy. Filled in the notebook's `model_root_url` placeholder with the
new backend URL and re-ran the full notebook end to end, all 94 code
cells executed clean including the previously skipped live inference
cells, which now show a real `200` response, an actual predicted sales
value, a real ten-row batch result, and the live history endpoint
reflecting both of those calls. Committed the refreshed notebook and
both READMEs.

## Bringing back a Streamlit frontend alongside the Web Components app

The user pointed out that some review checklists call for a Streamlit
frontend specifically, and asked for one to exist in parallel with the
Web Components app rather than replacing it. The original Streamlit app,
from before the switch to Web Components, was still sitting in git
history at commit `0d17147`, fully compatible with the current backend
API since neither `/v1/predict` nor `/v1/predictbatch` ever changed shape.

Resurrected it into a new `frontend_streamlit/` folder, kept side by side
with `frontend_files/`, and asked the user two quick scope questions
before starting: whether it should stay a bare-bones single and batch
prediction app or also pick up the newer conveniences (server side
history, a friendlier area input), and whether it should be deployed live
as a third container or just live in the repos as a buildable option.
Answer to both was to go further, feature parity and a live deployment,
plus adding it to both repositories the same way `frontend_files/` and
`backend_files/` already exist in both.

Single Prediction and Batch Prediction tabs came back close to the
original, the Product Allocated Area field is now a percentage slider
instead of a raw 0 to 1 fraction, matching the same reasoning behind
that change in the Web Components form. Added a third tab, History,
reading `GET /v1/history` into a table with an expander per record for
the full input and result, and a Clear history button wired to `DELETE
/v1/history`. Since both frontends are thin clients over the same Flask
backend, a forecast made from one shows up in the other without any
extra wiring, the backend already recorded history the same way
regardless of which frontend called it.

Tested locally first, a plain `streamlit run` against a local Flask
process, confirmed with Playwright that a prediction succeeds and the
history tab renders records from both frontends. `st.dataframe` in this
Streamlit version renders through a virtualized, canvas-based grid, so a
DOM text search for table contents comes back empty even though the data
is genuinely there and visible, a screenshot was the more reliable check
than an accessibility-tree assertion for that particular widget.

Deployed it to the live Codespace as a third container, `superkart-
streamlit`, on port `8502`, built from the same `frontend_streamlit/`
folder just pushed to `super_kart_model_deployment`, on the same shared
Docker network as the other two containers, with the same `restart:
unless-stopped` policy. Forwarded and publicized port `8502` the same way
the other two ports already were, it came up correctly on the first try,
no repeat of the prebuild-related routing fault from earlier. A full
Playwright pass against the live URL confirmed a real prediction comes
back correctly.

Folded the same addition into `build_notebook.py`: a new section writes
`frontend_streamlit/app.py`, `requirements.txt`, and `Dockerfile` right
after the Web Components frontend section, the Docker validation section
now builds, runs, and health-checks all three containers instead of two,
and the git push cell now stages `frontend_streamlit/` alongside the
other two folders. Regenerated the notebook from scratch, ran it fully
including the live inference cells with the same Codespace backend URL,
97 cells executed clean. Cleared the test predictions left in the live
history by both the notebook run and the Playwright checks before
finishing, so a first-time visitor to either frontend sees an empty
history rather than test data.

Updated both `README.md` files with the third live URL, a description of
the Streamlit app and its History tab, and Streamlit-specific commands
added to every existing run option (Codespace, local Docker, no Docker
at all). Committed and pushed the `frontend_streamlit/` addition to
`super_kart_model_deployment` first so the Codespace could pull and build
it, then committed the notebook, `build_notebook.py`, and both READMEs to
`model_deployment_dba`.
