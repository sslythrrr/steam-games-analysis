# Steam Games Data Crawler and Analysis Pipeline

A Python-based project designed to efficiently scrape current player count and metadata for a comprehensive list of games available on the Steam platform. The collected raw data is saved into an Excel file for subsequent analysis.

***

## Key Features

* **Full Steam App List Fetching**: Synchronously retrieves the entire list of applications and games from the official Steam Web API.
* **Active Player Count Retrieval**: Asynchronously fetches the current number of players for each active game using the Steam Web API.
* **Store Metadata Scraping**: Asynchronously gathers essential game details from the Steam Store API, including **price**, **free-to-play status**, **genres**, and **release date**.
* **High Concurrency**: Utilizes `asyncio` and `aiohttp` to manage thousands of concurrent requests, maximizing scraping speed while respecting API rate limits using semaphores.
* **Data Persistence**: Collects all gathered information and saves the structured dataset into a timestamped Excel file for easy data analysis.

***

## Technologies Used

This project is built primarily with Python and leverages several libraries for network operations, asynchronous processing, and data handling:

| Category | Technology/Library | Purpose |
| :--- | :--- | :--- |
| **Language** | Python | Primary programming language. |
| **Networking** | `aiohttp`, `requests` | Handles asynchronous and synchronous HTTP requests to Steam APIs. |
| **Asynchrony** | `asyncio`, `nest-asyncio` | Enables concurrent execution and nested asynchronous operations. |
| **Data Handling** | `pandas`, `openpyxl` | Manages data structures (DataFrame) and exports the final dataset to an Excel (`.xlsx`) file. |
| **Utility** | `tqdm` | Provides progress bar visualization for long-running asynchronous tasks. |

The required packages and their minimum versions are listed in `requirements.txt`:

## Prerequisites

Before running the crawler, ensure you have the following:

1.  **Python**: (Version 3.8 or higher recommended).
2.  **Steam Web API Key**: A personal API key is required to access the Steam Web API endpoints. You can obtain one from the [Steam Community Developer API Key](https://steamcommunity.com/dev/apikey).

***

## Installation and Setup

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/sslythrrr/steam-games-analysis.git](https://github.com/sslythrrr/steam-games-analysis.git)
    cd steam-games-analysis
    ```

2.  **Install dependencies**:
    Install all required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key**:
    You must provide your Steam Web API Key. This is typically done by editing the `config.py` file and setting the `Config.STEAM_API_KEY` variable.

    *Note: The `config.py` file also allows configuring parameters like maximum concurrent requests and request timeouts.*

***

## Usage Example

To start the data scraping process, simply run the main crawler script:

```bash
python steam_crawler.py
