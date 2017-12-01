# InfoTelegramBot
Telegram Bot, which sends out information from Vkontakte, Facebook, Twitter and Youtube.<br>
The essence of the work lies in the work of the Flask-server and the independent Python-parser.


[![Deploy to heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)


<h1>To get started</h1>
To get started, you need to install the package specified in the *requirements.txt* <br>
Also, you should install <a href="https://nodejs.org/en/download/package-manager/">*NodeJS*</a> and <a href="https://www.npmjs.com/package/phantomjs">*PhantomJS*</a> - the benefit of this is the manuals and I do not have to describe all this here.<br>
To check up working capacity it is possible a command (in a project root):<code>python3 index.py</code><br>
The same goes for the work of the parser, just try to run it by going to the folder `/parser`: <code>python3 index.py</code>
<br>
<h1> Flask-server </h1>
<br>
When the server starts, Telegram Webhook is initialized. Also, it has a list of methods that process and issue certain data.<br>
<h3>Methods</h3>
<ol>
  <li> <i>/getsubs</i> - Provides subscriptions in the form of serialized json data</li>
  <li> <i>/setupdates</i> - Accepts GET data from the parser and updates the state in the database + sends the posts to clients.</li>
</ol>

# Parser
Runs every n seconds (the default value is 120).<br>
Sends a POST request to the server; when you receive data - starts to run through the links. <br>
Forms a json update list for each group - when new data is received, it sends to the server.<br>
Now only <a href="https://vk.com">Vkontakte</a> support is added.<br>
