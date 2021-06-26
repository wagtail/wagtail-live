# Set up a local web server with ngrok

When using Wagtail Live, especially webhook receivers, you will often need to
register a public URL which messaging apps use to send new updates to your Wagtail site.

In a development environment, ngrok can help us expose a public web server and tunnels requests to our local server.

## Downloading ngrok

Head to [ngrok](https://ngrok.com/download) and download the version that corresponds to your platform.

## Installing ngrok

To install ngrok, we need to extract the file into a folder and run it from there.

You can extract it into the folder of your preference. In that configuration, you will need to navigate to the folder where you unzipped ngrok whenever you want to start it.

If you want to run ngrok from any path on the command line, you will have to extract the ngrok file on your system's `$PATH` directory.

To get your system's `$PATH`, type from the command line:
```console
$ echo $PATH
```

## Start ngrok server

if ngrok is on your `$PATH`, type:
```console
$ ngrok http 8000
```

If the above doesn't work or you extracted ngrok in another directory (like `home/downloads/ngrok_folder`), navigate to that directory and then start the server as following:
```console
$ cd home/downloads/ngrok_folder
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