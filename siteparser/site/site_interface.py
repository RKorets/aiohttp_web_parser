from abc import abstractmethod, ABCMeta


class Interface(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def get_pages_in_categories(site: str, categories: str) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def get_page_data(request, session, category: str, link) -> str:
        pass
