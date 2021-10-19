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
srb2kartwebsite> python kartsite.py
```
In production, use gunicorn instead:
```
python3 -m gunicorn --bind 0.0.0.0:5000 wsgi:app
```
Gunicorn is a WSGI interface which is meant to serve the site in a more stable and efficient way than the flask development server is able to (supposedly).
