# UtrehdsCrawler's Documentation

## Set Up

### Env

Create your own venv in the current subdirectory, activate it and run...

```
pip install -r requirements.txt
```

### Docker

Docker must be installed and running. Needed for the dynamic spider. To work run the following command:

```
docker run -p 8050:8050 scrapinghub/splash
```

#### Notes

- Anti-Virus must be turned off

## Scrapy Commands

### Run spider

To run the spiders you must choose between two options, the static and dynamic spiders. The static spider is for statically generated html web pages, and the dynamic spider is for JavaScript generated web pages or dynamic webpages. To run the spider simply enter the command `scrapy crawl` and the choose between the `static` or `dynamic` options.

This will still not be sufficient to run the spider, it needs to be give a profile to be able to receive which selectors it should use to get the data. To select the profile it needs the name of the website, property type, and price type which will be added to the existing command in the previous paragraph. Bellow is an example of a full working command:

```
scrapy crawl static -a name=expats -a property_type=flat -a price_type=sale
```

Add `-o data.json` at the end to save data in `data.json` file.

### Run splash in shell

The shell is used for finding/testing out selectors, makes it faster and easier.

Static:

```
scrapy shell www.example.com
```

Dynamic:

```
scrapy shell 'http://localhost:8050/render.html?url=https://www.sreality.cz/hledani/prodej/byty&timeout=10&wait=0.5'
```
