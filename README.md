# Gusta30 - Passeggiata Gastronomica 🍷🧀

Gusta30 is a modern, responsive web application designed for a gastronomic walk event in Avegno, Switzerland. It provides participants with real-time updates on event stages, including menus, locations, and hosts.

## 🌟 Features

-   **Dynamic Stages**: Interactive "tappe" (stages) that unlock automatically based on time or manually via the admin panel.
-   **Premium UI**: Modern, mobile-first design with glassmorphism, smooth animations, and Inter typography.
-   **Security**: Secrets managed via environment variables and session-based administrator authentication.
-   **State Persistence**: Manual unlocks are persisted in a JSON database (`data.json`), ensuring no progress is lost on server restarts.
-   **Countdown**: Live countdown to the event start.
-   **Responsive**: Optimized for both mobile devices (used during the walk) and desktop.

## 🛠️ Technology Stack

-   **Backend**: Python / Flask
-   **Frontend**: Vanilla JS, Modern CSS (Glassmorphism), HTML5
-   **Persistence**: JSON-based state storage
-   **Security**: `python-dotenv` for configuration

## 🚀 Getting Started

### Prerequisites

-   Python 3.8+
-   Pip (Python package manager)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/nicolastoira/Gusta_30.git
    cd Gusta_30
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file based on `.env.example`:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and set your own `APP_SECRET_KEY`, `ADMIN_PASSWORD`, and `API_TOKEN`.

4.  **Run the application**:
    ```bash
    python app.py
    ```
    The site will be available at `http://localhost:5000`.

## 📂 Project Structure

-   `app.py`: Main application logic and route handlers.
-   `data.json`: Local database for persistent state (manually unlocked stages).
-   `static/`:
    -   `css/style.css`: Premium design styles.
    -   `js/main.js`: Frontend logic for dynamic content loading.
    -   `images/`: Event logos, QR codes, and popups.
-   `templates/`: Jinja2 HTML templates for the site and admin panel.

## 🔐 Admin Panel

Access the admin panel at `/admin` to manually unlock or lock stages. The password is set in your `.env` file (locally) or via Fly.io secrets.

## 🚀 Fly.io Deployment

The application is configured to be deployed on [Fly.io](https://fly.io) with persistent storage.

### 1. Persistent Volume
Fly.io uses an ephemeral filesystem. To ensure your `data.json` persists, you must create a volume:
```bash
fly volumes create gusta30_data --size 1 --region fra
```

### 2. Configuration (`fly.toml`)
The repository includes a `fly.toml` that mounts the volume to `/data`. The application automatically detects this and stores `data.json` at `/data/data.json`.

### 3. Secrets
Set your environment variables as Fly secrets:
```bash
fly secrets set APP_SECRET_KEY=... ADMIN_PASSWORD=... API_TOKEN=...
```

### 4. Deploy
Simply run:
```bash
fly deploy
```

---
*Created for the Gusta30 event in Avegno.*
