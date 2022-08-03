from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db import Categories, Site
from src.settings import config
from sqlalchemy import select


my_sql = config['mysql']
url_db = f"mysql+pymysql://{my_sql['user']}:{my_sql['password']}@{my_sql['host']}/{my_sql['database']}"

engine = create_engine(url_db, echo=False)

DBSession = sessionmaker(bind=engine)
session = DBSession()


def main(site_name: str, domen: str, categories_name: str, categories_url: str):
    site_exist_chek = select(Site).filter(Site.domen == domen)
    site_exist = session.execute(site_exist_chek).scalar()
    if site_exist:
        pass
    else:
        site = Site(name=site_name, domen=domen)
        session.add(site)
        session.commit()

    site_query_id = select(Site).filter(Site.name == site_name)
    site_id = session.execute(site_query_id).scalar()
    categories = Categories(site_id=site_id.id, categories_name=categories_name,
                            categories_url=categories_url)
    session.add(categories)
    session.commit()
    session.close()


if __name__ == '__main__':
    main('Citrus', 'ctrs.com.ua', 'Notebook', 'noutbuki-i-ultrabuki/')
    main('Citrus', 'ctrs.com.ua', 'Telephone', 'smartfony/')
    main('Rozetka', 'rozetka.com.ua', 'Notebook', 'notebooks/c80004/sell_status=available;seller=rozetka/')
    main('Rozetka', 'rozetka.com.ua', 'Telephone', 'mobile-phones/c80003/sell_status=available;seller=rozetka/')
