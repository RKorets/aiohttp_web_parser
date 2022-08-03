********************** Goods Parser site **********************

1. Install all the requirements from "requirements.txt"
2. Init site option as siteparser/site/init_db_site_option.py run
3. Start app -  app.py run
3. Open browser url "localhost:8080/"
4. Use
_______________________________________________________________
OPTIONS:
DB config - config/app_cfg.yaml
_______________________________________________________________
ADD NEW SITE FOR PARSE:
siteparse/site/you_site.py (class interface site_interface.py)
init_db_site_option.py add you site name, domen, query parameters url
import you class site in site_data.py dict SITE
_______________________________________________________________