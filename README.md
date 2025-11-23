## Archived!

Since the developer of [Kitshn](https://github.com/aimok04/kitshn) has implemented a direct way to import social media posts to tandoor, I will no longer maintain this repo!

<p align="center">
    <img src="./images/icon-512.png" alt="App Icon" width="100" />
</p>

# Social Media -> Tandoor / Mealie

Since I often browse Instagram or TikTok for recipes, I wanted a way to save them to my own recipe collection on [Tandoor](https://github.com/TandoorRecipes/recipes). Getting an Instagram / TikTok API took me too long, so I decided to use [Selenium](https://github.com/SeleniumHQ/selenium) to scrape the recipe from a provided Instagram / TikTok post. Since everyone writes their recipes differently and it's almost impossible to parse them all into the required JSON format, I decided to use an LLM. My notebook is not powerful enough to use [Ollama](https://ollama.com/) for this, so I decided to use [DuckAi](https://duck.ai). To automate the query process, I also used Selenium to interact with the website.
When I get all the necessary JSON parts, I combine them and send them to Tandoor using the implemented API.

The problem with LLM's is that they are not deterministic, so the output can be variable in quality. Sometimes you have to adjust the output manually, but in most cases it's good enough to use as is.

## 💪 Features

- [x] Scrape Instagram / TikTok posts (with images)
- [x] Use DuckAi to generate recipe JSON
- [x] Upload recipe to Tandoor / Mealie
- [x] Docker support
- [x] WebUi

## 🖼️ Impressions

<p align="center">
    <img src="./images/web_ui_start.png" alt="WebUi start" width="32%"/>
    <img src="./images/web_ui_job.png" alt="WebUi job" width="32%" />
    <img src="./images/web_ui_history.png" alt="WebUi history" width="32%" />
</p>

## 📦 Installation using Docker:

Make sure you have docker installed on your system.

```
git clone https://github.com/doen1el/instagram-to-tandoor.git instagram-to-tandoor
cd instagram-to-tandoor
```

### Preparation:

You need to edit the docker-compose file and change the ENV variables to your needs.

#### Tandoor

```
BASE_URL_TANDOOR=https://YOUR_TANDOOR_URL
TOKEN_TANDOOR=YOUR_TANDOOR_TOKEN
LANGUAGE_CODE=de (or en, etc.)
```

You can retrieve your tandoor token by

1. Visiting `https://YOUR_TANDOOR_URL/settings/#api`.
2. Creating a new token using the `write read bookmarklet` and a name of your choice
3. Copy the token and add it to the `.env` file

---

#### Mealie

```
BASE_URL_MEALIE=https://YOUR_MEALIE_URL
TOKEN_MEALIE=YOUR_MEALIE_TOKEN
LANGUAGE_CODE=de (or en, etc.)
```

You can retrieve your tandoor token by

1. Visiting `https://YOUR_TANDOOR_URL/user/profile`.
2. Creating a new api token with a name of your choice
3. Copy the token and add it to the `.env` file

### Build and run the container:

```
docker compose up -d
```

### Usage:

Visit `http://localhost:5000` in your browser and use the web interface to add a new recipe.

## 📦 Installation without Dockers:

Make sure you have python 3.x installed on your system.

Without venv:

```
git clone https://github.com/doen1el/instagram-to-tandoor.git instagram-to-tandoor
cd instagram-to-tandoor
pip install -r requirements.txt
```

With venv:

```
git clone https://github.com/doen1el/instagram-to-tandoor.git instagram-to-tandoor
cd instagram-to-tandoor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Preparation:

Create an `.env` file in the root directory of the project and add the following

#### Tandoor

```
BASE_URL_TANDOOR=https://YOUR_TANDOOR_URL
TOKEN_TANDOOR=YOUR_TANDOOR_TOKEN
LANGUAGE_CODE=de (or en, etc.)
```

You can retrieve your tandoor token by

1. Visiting `https://YOUR_TANDOOR_URL/settings/#api`.
2. Creating a new token using the `write read bookmarklet` and a name of your choice
3. Copy the token and add it to the `.env` file

---

#### Mealie

```
BASE_URL_MEALIE=https://YOUR_MEALIE_URL
TOKEN_MEALIE=YOUR_MEALIE_TOKEN
LANGUAGE_CODE=de (or en, etc.)
```

You can retrieve your tandoor token by

1. Visiting `https://YOUR_TANDOOR_URL/user/profile`.
2. Creating a new api token with a name of your choice
3. Copy the token and add it to the `.env` file

---

### Change Browser

The script uses Selenium to interact with the installed web browser. The browser is hidden by default, so don't worry if nothing pops up. You can check if your installed browser is compatible by checking the [Selenium documentation](https://www.selenium.dev/documentation/webdriver/browsers/). The default browser is `Firefox`. To change the browser, add the following to your `.env' file

```
BROWSER=chrome
```

other possible values are `edge`, `safari`, `firefox`. If you do not add this line, the default browser is `Firefox`.

### Usage:

#### WebUi:

```
python3 app.py
```

#### Command Line:

```
python3 main.py -url [https://www.instagram.com/...] -mode [mealie (m) | tandoor (t)] -platform [instagram (i) | tiktok (t)]
```

or use

```
python3 main.py -help
```

for more information.

## 🚀 Contributing

Feel free to open an issue, pull request, or simply fork the project.

## ⚠️ Disclaimer:

By using this application you accept [DuckDuckGo AI Chat ToS](https://duckduckgo.com/aichat/privacy-terms)

## 🚧 Roadmap

- [x] Add TikTok support
- [x] Dockerize the project
- [x] Create a GUI
- [x] Optimize prompting

## 📜 Credits

- [Tandoor](https://github.com/TandoorRecipes/recipes)
- [Selenium](https://github.com/SeleniumHQ/selenium)
- [BeautfiulSoup4](https://github.com/wention/BeautifulSoup4?tab=readme-ov-file)
