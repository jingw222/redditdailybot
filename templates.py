from jinja2 import Template


body_template = Template("""
    <html>
        <head><meta charset="utf-8" name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body>
           {% for subreddit in data.keys() %}
            <h3><a href="https://www.reddit.com/r/{{ subreddit }}">/r/{{ subreddit }}</a></h3>
                <p>
                  {% for post in data[subreddit] %}
                  <ul>
                    <p>{{ post['ups'] }}&#x1F44F; {{ post['comments' ]}}&#x1F476; <br> 
                    <a href="{{ post['link' ]}}">{{ post['title' ]}}</a><p/> 
                  </ul>
                  {% endfor %}
                </p>
            {% endfor %}
        </body>
    </html>
    """
)

