from jinja2 import Template


body_template = Template("""
    <html>
        <head><meta charset="utf-8" name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body>
           <center><a href="https://www.reddit.com"><img src="cid:logo" alt="reddit-logo"></a></center>
           {% for subreddit in data.keys() %}
            <h2><a href="https://www.reddit.com/r/{{ subreddit }}">/r/{{ subreddit }}</a></h2>
                <p style="font-size:18px;">
                  {% for post in data[subreddit] %}
                  <ul>
                    <p style="font-weight=900;">{{ post['score'] }}&#x1F44F; {{ post['num_comments'] }}&#x1F476; <br> 
                    <a href="{{ post['shortlink'] }}">{{ post['title'] }}</a><p/> 
                  </ul>
                  {% endfor %}
                </p>
            {% endfor %}
        </body>
    </html>
    """
)

