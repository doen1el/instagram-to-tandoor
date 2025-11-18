from abc import ABC, abstractmethod

class RecipeProviderInterface(ABC):
    @staticmethod
    @abstractmethod
    def scrape(url, platform):
        """
        Extracts recipe data from a given URL and platform.
        """
        pass
