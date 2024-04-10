# minidash

A minimal Dash app for testing purposes. app.py source from https://dash.plotly.com/minimal-app

## Deployment

- Internal Server: http://w0lxprconn01.worldbank.org:3939/
- External Server: https://datanalytics.worldbank.org/

Ensure you have an RStudio Connect account, if not [request here](https://worldbankgroup.service-now.com/wbg?id=ticket&table=sc_req_item&sys_id=fbb93028476502d09169d03fe16d4309). Upon account provisioning, generate API key(s) on the target server's UI.

Check which python version is supported by the server with:

```bash
rsconnect content search --server [server URL] --api-key [your API key] | jq -c '.[] | {py_version}' | sort | uniq
```

As of writing both the internal and external server supports 3.8.14 so that's the version we are going to use for building & deploying the dash app. If you are using `pyenv` this repo's python version has configured to use 3.8.14. If the target server uses a different version, feel free to switch using `pyenv local 3.x.x`.

To verify the app works locally:

```bash
pip install -r requirements.txt
python app.py
open http://127.0.0.1:8050/
```
You should see a single chart app.

To deploy:

```bash
rsconnect deploy dash --server [server URL] --api-key [your API key] ./
```
