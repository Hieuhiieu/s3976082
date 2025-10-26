def get_page_html(form_data):
    print("About to return page home page...")
    page_html="""<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Database Web-App Demo</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
        <p>This is the first dynamically generated page!</p>
        <p><a href="/page2">Go to Page 2</a></p>
        <p><a href="/page3">Go to Page 3</a></p>
        <img src="images/rmit.png" style="width: 30%; height: auto;">
    </body>
    </html>
    """
    return page_html