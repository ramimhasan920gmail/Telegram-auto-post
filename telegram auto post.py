import requests
import time
from bs4 import BeautifulSoup

# ========= CONFIG =========
BLOG_ID = "1587234114407540772"
API_KEY = "AIzaSyA0W0U63tWbYF7gXiAxO3cqwrCOG520f84"

BOT_TOKEN = "8552068201:AAHwXAyaxarJG6eVY0lk8u-x_ELRyS_X5so"
CHANNEL_ID = "@Moviedroop1"

CHECK_INTERVAL = 30  # ৫ মিনিট
# ===========================


def extract_movie_details(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Movie Card Div
    movie_card = soup.find("div", class_="movie-card-vertical")
    if not movie_card:
        return "Movie card not found in post.", None

    # Title
    title_tag = movie_card.find("h2")
    title = title_tag.text.strip() if title_tag else "N/A"

    # Poster
    poster_tag = movie_card.find("div", class_="poster")
    image_url = poster_tag.find("img")["src"] if poster_tag and poster_tag.find("img") else None

    # Info Grid
    info_grid = movie_card.find("div", class_="info-grid")

    genre = info_grid.find("span", class_="movie-genre").text.strip() if info_grid and info_grid.find("span", class_="movie-genre") else "N/A"
    imdb = info_grid.find("span", class_="imdb-rating").text.strip() if info_grid and info_grid.find("span", class_="imdb-rating") else "N/A"
    release = info_grid.find("span", class_="movie-release").text.strip() if info_grid and info_grid.find("span", class_="movie-release") else "N/A"
    language = info_grid.find("span", class_="movie-language").text.strip() if info_grid and info_grid.find("span", class_="movie-language") else "N/A"
    director = info_grid.find("span", class_="movie-director").text.strip() if info_grid and info_grid.find("span", class_="movie-director") else "N/A"
    budget = info_grid.find("span", class_="movie-budget").text.strip() if info_grid and info_grid.find("span", class_="movie-budget") else "N/A"

    # Cast
    cast_tag = movie_card.find("span", class_="movie-cast")
    cast = cast_tag.text.strip() if cast_tag else "N/A"

    # Plot
    plot_tag = movie_card.find("span", class_="movie-plot")
    plot = plot_tag.text.strip() if plot_tag else "N/A"

    # Formatted Message
    message = f"""
🎬 {title}

⭐ IMDb: {imdb}
📅 Release Date: {release}
🎭 Genre: {genre}
🌍 Language: {language}
🎬 Director: {director}
💰 Budget: {budget}
🎭 Cast: {cast}

📝 Plot:
{plot}
"""

    return message, image_url


def get_latest_post():
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts"
    params = {"key": API_KEY, "maxResults": 1}

    response = requests.get(url, params=params)
    print("Blogger Status:", response.status_code)

    if response.status_code != 200:
        print("Blogger Error:", response.text)
        return None

    data = response.json()

    if "items" not in data:
        print("No posts found.")
        return None

    return data["items"][0]


def send_to_telegram(message, image_url):
    if image_url:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        data = {
            "chat_id": CHANNEL_ID,
            "photo": image_url,
            "caption": message
        }
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHANNEL_ID,
            "text": message
        }

    response = requests.post(url, data=data)
    print("Telegram Response:", response.text)


# ========= AUTO LOOP =========
sent_links = set()

print("Auto Poster Started...")

while True:
    post = get_latest_post()

    if post:
        link = post["url"]

        if link not in sent_links:
            content = post["content"]
            details, image_url = extract_movie_details(content)

            final_message = f"{details}\n🔗 Downlod Now: {link}"

            send_to_telegram(final_message, image_url)
            sent_links.add(link)
            print("Posted:", post["title"])
        else:
            print("No new post.")

    time.sleep(CHECK_INTERVAL)