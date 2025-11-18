import os

from scrapers.scraper_modules.tandoor_provider import TandoorProvider
from scrapers.scraper_modules.mealie_provider import MealieProvider

class ScraperService:
    PROVIDERS = {
        "tandoor": TandoorProvider,
        "mealie": MealieProvider
    }

    @staticmethod
    def get_provider():
        provider_name = os.getenv("RECIPE_PROVIDER", "tandoor").lower()
        provider = ScraperService.PROVIDERS.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown recipe provider: {provider_name}")
        return provider

    @staticmethod
    def scrape_recipe(url, platform):
        provider = ScraperService.get_provider()
        return provider.scrape(url, platform)
