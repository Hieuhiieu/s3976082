import pyhtml
def get_page_html(form_data):
    print("About to return page 3")
    #Create the top part of the webpage
    #Note that the drop down list ('select' HTML element) has been given the name "var_star"
    #We will use this same name in our code further below to obtain what the user selected.
    page_html="""<!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Page 3 - Forms, databases and advanced queries</title>
    </head>
    <body>
        <h1>Welcome to Page 3!</h1>
        <p>List the movies based on the star</p>
        <form action="/page3" method="GET">
        
          <label for="var_star">Movie Star</label>
          <select name="var_star" multiple>"""
    #Before you read further, play around with the web-page and note how selecting a star name from the first
    #drop down list populates the second drop down list with the movies in which they have featured.
    
    #Note that although we see the name of the movie star in the first drop down list, when a star is selected and submitted,
    #our program receives the star's ID (primary key).
    
    ################################ Movie star drop down list is generated below ######################################
          

    #Put the query together.
    query = "select * from star;"
    
    #Run the query on the movies.db in the 'database' folder and get the results
    #Note that all results are in the str data type first, even if they had different types in the database.
    results = pyhtml.get_results_from_query("database/movies.db",query)
    
    #Get the value or values in the HTML dropdown list that we named "var_star" or None no data was sent through.
    #If the user selects multiple movie stars on the web_page, we will have multiple values.
    var_star = form_data.get('var_star')
    
    print("var_star selected on webpage is: ",var_star)
    
    #If the user had selected one or more stars on the web-page, convert their IDs to int
    if(var_star!=None):
        #Take the list of strings and convert the items to ints
        var_star = [int(star) for star in var_star]
    
    #Create the drop down list of movie stars
    for row in results:
        #row[0] is the ID/primary key of the movie stars
        page_html+='<option value="'+str(row[0])+'"'
        #If there was a previous selection of a star on the web page, have them selected by default to be user-friendly.
        if var_star!=None and row[0]==var_star[0]:
            page_html+=' selected="selected"'
            
        #row[1] is the name of the star, which is what the user sees in the drop down list.
        page_html+='>'+str(row[1])+'</option>'
        
    page_html+="</select><br><br>"



    ################################ Movies drop down list is generated below ##########################################
    
    page_html+="""<label for="var_movie">Movie</label>
    <select name="var_movie" """

    #We create this drop down list only if a movie star was chosen
    if var_star!=None:
        #Query for getting the list of movie IDs and their titles by star
        query ="""SELECT movie.mvnumb, movie.mvtitle 
        FROM movie 
        JOIN movstar ON movie.mvnumb = movstar.mvnumb """
        query+=f"WHERE movstar.starnumb = {var_star[0]};"

        #Run query and get results
        results = pyhtml.get_results_from_query("database/movies.db",query)
        page_html+=" >"
        #row[0] is the movie ID (primary key) and row[1] is the movie title
        for row in results:
            page_html+='<option value="'+str(row[0])+'"\>'+str(row[1])+'</option>'
    else:
        #If no movie star was chosen, we create a dummy list and make it disabled so the user sees the movie drop down
        #but they can't access it.
        page_html+="disabled>"
        page_html+='<option>Choose a star</option>'
    page_html+="</select><br><br>"

    page_html+="""
    <input type="submit" value="Show starred movies">
    </form>
    <p><a href="/">Go back to home page</a></p>
    </body>
    </html>
    """
    return page_html