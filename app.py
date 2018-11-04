import asyncio

import aiohttp
import argparse
from pyquery import PyQuery as pq
from tabulate import tabulate


def parse_args():
    parser = argparse.ArgumentParser(description="Find top movies by year")
    parser.add_argument("--year", action="append", help="movies release year, multiple allowed")
    parser.add_argument("--search", help="show only movies containing search term in the title")

    return parser.parse_args()


async def get_imdb_html(session, year):
    async with session.get(f"https://www.imdb.com/search/title?year={year}") as response:
        return year, await response.text()


def get_movies(html, search):
    for movie in [pq(item) for item in pq(html).find("div.lister-item-content")]:
        title = movie.find("h3.lister-item-header a").text()

        if search and search not in title.lower():
            continue

        yield {
            "rank": movie.find("span.lister-item-index").text(),
            "title": title,
            "genre": movie.find("span.genre").text(),
            "run_time": movie.find("span.runtime").text(),
            "rating": movie.find("div.ratings-imdb-rating strong").text()
        }


def print_movies(year, movies):
    print(f"\nTop movies in {year}\n" + tabulate(movies, headers="keys", tablefmt="fancy_grid"))


async def main():
    args = parse_args()

    async with aiohttp.ClientSession() as session:
        tasks = [get_imdb_html(session=session, year=year) for year in args.year]

        for year, html in await asyncio.gather(*tasks):
            print_movies(year=year, movies=get_movies(html=html, search=args.search.lower()))


if __name__ == "__main__":
    asyncio.run(main())
