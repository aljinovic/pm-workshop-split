import asyncio

import aiohttp
import argparse
from pyquery import PyQuery as pq
from tabulate import tabulate

from db import db


def parse_args():
    parser = argparse.ArgumentParser(description="Find top movies by year")
    parser.add_argument("--year", action="append", help="movies release year, multiple allowed")
    parser.add_argument("--search", help="show only movies containing search term in the title")
    parser.add_argument("--download", help="download movies for provided years", action='store_true')
    parser.add_argument("--list", help="show movies for provided years", action='store_true')

    return parser.parse_args()


async def get_imdb_html(session: aiohttp.ClientSession, year: int):
    async with session.get(f"https://www.imdb.com/search/title?year={year}") as response:
        return year, await response.text()


def scrape_movies(html: str, year: int):
    for movie in [pq(item) for item in pq(html).find("div.lister-item-content")]:
        title = movie.find("h3.lister-item-header a").text()

        yield {
            "rank": movie.find("span.lister-item-index").text().replace('.', '') or None,
            "title": title,
            "genre": movie.find("span.genre").text(),
            "run_time": movie.find("span.runtime").text(),
            "rating": movie.find("div.ratings-imdb-rating strong").text() or None,
            "year": year,
        }


def print_movies(movies: list):
    print(f"\nMovies\n" + tabulate(movies, headers="keys", tablefmt="fancy_grid"))


async def main():
    args = parse_args()

    if args.download:
        async with aiohttp.ClientSession() as session:
            tasks = [get_imdb_html(session=session, year=int(year)) for year in args.year]

            for year, html in await asyncio.gather(*tasks):
                for movie in scrape_movies(html, year):
                    db.save_movie(movie=movie)

    if args.list:
        print_movies(movies=db.get_movies(years=args.year, search=args.search or ""))


if __name__ == "__main__":
    asyncio.run(main())
