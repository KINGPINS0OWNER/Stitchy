# Stitchy

Stitchy is a web app for cross-stitchers to manage their pattern collection and floss (thread) inventory. It helps you track which patterns you can stitch based on the floss you have, and lets you upload and organize your patterns.

## Features

- **User Accounts:** Register, log in, and log out securely.
- **Pattern Management:** Add patterns with required floss colors.
- **Floss Inventory:** Track your floss codes and lengths.
- **Stitchable Patterns:** See which patterns you can make with your current floss.
- **PDF Upload:** Upload PDF patterns (future: extract thread info from PDFs).
- **Modern UI:** Clean, responsive HTML/CSS interface.

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/Stitchy.git
   cd Stitchy
   ```

2. **Install Dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the App:**

    ```sh
    python app.py
    ```
    The app will be avialble at http://localhost:5001

    **OR**

    Run with Docker:
    ```sh
    docker compose up --build
    ```

### How It Works

    - Authentication: Uses Flask-Login and password hashing.
    - Patterns: Stored in a JSON file (patterns.json), each with a name and required floss codes.
    - Floss Inventory: (Currently placeholder) Add and track floss by code and length.
    - Stitchable Patterns: (Planned) Will show patterns you can complete with your floss.
    - PDF Upload: Upload PDF patterns (parsing not yet implemented).

### Contributing
    Pull requests are welcome! For major changes, please open an issue first.

### License
    MIT License

---

   *This project is in active development. Feedback and suggestions are appreciated!*
