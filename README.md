# Smarth Tracker — Timesheet Automation

> Automates the full monthly timesheet registration process on the **Bold Brasil** platform using **Selenium WebDriver** and **Python**.

---

## Overview

Instead of manually filling in dozens of timesheet entries day by day, this script does the entire month in a single run. It opens a Chrome window, logs in to the platform, navigates to the *Registrar Atividades no Timesheet* module, and automatically registers two work sessions (morning + afternoon) for every weekday from the 1st of the current month up to today.

Running the script once on any working day will **backfill all working days** from the 1st up to that day — no manual input required.

---

## How It Works

### Flow

1. **Login** — Authenticates on the platform using the credentials defined in `.env`.
2. **Navigate** — Waits for the loading screen to disappear, clicks the main menu and opens the *Registrar Atividades no Timesheet* module.
3. **Apply filters** — Sets Cost Center, Contract and Activity Type filters, and configures the date range to cover the full current month.
4. **Iterate over weekdays** — Builds a list of all weekdays (Monday–Friday) from the 1st of the month up to today.
5. **Register each day** — For each working day, registers **two sessions**:
   - **Morning** — `09:XX → 12:XX` (exactly **3 hours**)
   - **Afternoon** — `13:XX → 18:XX` (exactly **5 hours**)
   - Both sessions use a small random minute offset (0–5 min) so entries don't look identical.
6. **Fill the form** — Each entry fills: Cost Center, Client (auto-detected), Contract, Activity Type, Date, Start Time, End Time, Total Hours and Description.
7. **Save** — Clicks *Salvar*, confirms the success modal and opens the next entry form with *Incluir*.
8. **Repeat** — Continues until all working days of the month are registered.

### Project Structure

```
smarth-tracker/
├── main.py          # Entry point — loads .env and starts the automation
├── Ponto.py         # Core automation class (Ponto) with all Selenium logic
├── driver.py        # Custom Chrome WebDriver wrapper with helper methods
└── requirements.txt # Python dependencies
```

### Key Classes & Methods

| Class / Method | Description |
|---|---|
| `Driver` (`driver.py`) | Extends `selenium.webdriver.Chrome` with helpers for localStorage, waits and canvas comparison |
| `Ponto.__init__` | Receives driver, credentials and form codes |
| `Ponto.logar()` | Navigates to the platform URL and performs login |
| `Ponto.listar()` | Dismisses modals, applies filters and clicks *Incluir* to open the form |
| `Ponto.cadastrar_mes()` | Main loop — iterates over weekdays and registers morning + afternoon sessions |
| `Ponto._cadastrar_sessao()` | Fills and saves a single timesheet entry |
| `Ponto._clicar_incluir()` | Clicks the *Incluir* button to open a fresh entry form |
| `Ponto._preencher_campo_consulta()` | Types a code into a lookup field (form), waits for Angular to resolve it |
| `Ponto._preencher_input_consulta_js()` | Sets a lookup field value via JS (used only in the filter panel) |

---

## Requirements

- Python 3.10+
- Google Chrome (any recent version — Selenium 4 manages ChromeDriver automatically)
- Dependencies in `requirements.txt`

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```env
USER=your_username
PASSWORD=your_password
CONTRATO=280
CENTRO_CUSTO=3
```

| Variable | Description |
|---|---|
| `USER` | Platform login username |
| `PASSWORD` | Platform login password |
| `CONTRATO` | Contract code selected in the registration form |
| `CENTRO_CUSTO` | Cost Center / Unit code selected in the registration form (default: `3`) |

---

## Usage

```bash
python main.py
```

The script will:
1. Open a maximized Chrome window.
2. Log in and navigate to the timesheet module.
3. Print progress for every step directly to the console.
4. Register all working days of the current month up to today.
5. Print a summary when done: `=== Cadastro do mês concluído! X registros inseridos ===`

---

## Chrome Options

The driver is configured with the following Chrome flags (see `driver.py`):

| Flag | Purpose |
|---|---|
| `--start-maximized` | Opens the browser maximized |
| `--disable-gpu` | Disables GPU hardware acceleration |
| `--no-sandbox` | Disables the Chrome sandbox (useful in CI/restricted environments) |
| `--window-size=1250,1095` | Sets a fixed window size as fallback |
| Custom `--user-agent` | Spoofs a standard Windows/Chrome user-agent string |

To run in **headless mode** (no visible browser window), uncomment the `--headless` line in `driver.py`.

---

## Author

| [<img src="https://avatars1.githubusercontent.com/u/46221221?s=460&u=0d161e390cdad66e925f3d52cece6c3e65a23eb2&v=4" width=115><br><sub>@jacksonn455</sub>](https://github.com/jacksonn455) |
| :---: |
