# Set up a local web server with ngrok

When using Wagtail Live, especially webhook receivers, you will often need to
register a public URL which messaging apps use to send new updates to your Wagtail site.

In a development environment, ngrok can help us expose a public web server and tunnels requests to our local server.

## Downloading ngrok

Head to [ngrok](https://ngrok.com/download) and download the version that corresponds to your platform.

## Installing ngrok

To install ngrok, we only need to extract the file into a folder.

Extract the ngrok zip file into the folder of your preference. - in `downloads/ngrok_folder` for example -

## Start ngrok server

Navigate to the directory where you extracted ngrok - in our example `downloads/ngrok_folder` - and then start the server as following:
```console
$ cd downloads/ngrok_folder
$ ./ngrok http 8000
```

If all goes well, you should see something like this:

```console
ngrok by @inconshreveable                                     (Ctrl+C to quit)
                                                                                
Session Status            online                           
Update                    update available (version 2.3.40, Ctrl-U to update
Version                   2.35                                  
Web Interface             http://127.0.1:4040                             
Forwarding                http://4e0cd6d40780.ngrok.io -> http:localhost:8000
Forwarding                https://4e0cd6d40780.ngrok.io -> http:localhost:8000
                                                                                
Connections               ttl     opn      rt1     rt5     p50     p90       
                           0       0       0.00    0.00    0.00    0.00
```

**Note:** Most messaging apps will require the one that starts with _https://_.

You can now register a public-facing URL that tunnels to your local server.
