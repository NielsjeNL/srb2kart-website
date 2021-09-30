# SRB2Kart Website
This repo contains the SRB2Kart website hosted on https://srb2kart.aqua.fyi.
It is tailored to fit the needs of the Aqua's Karthouse community.

To give the website your own style, fork the repo and customize the files to your needs.

### Running the website
First install the necessary requirements:
```Python
pip install -r requirements.txt
```
Then setup `config.json` inside the `srb2kartwebsite` folder. There's an example file that can help you.

When ready, launch the code as follows in a testing environment:
```
srb2kart-website> python srb2kartwebsite/kartsite.py
```

If you want to run this app in a production environment (so something less testy and more realy) take a look at hosting this app through a WSGI interface. The Flask documentation gives enough examples to get started.
