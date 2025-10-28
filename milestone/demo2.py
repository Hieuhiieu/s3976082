import pyhtml
import student_a_level_1
import student_a_level_2
import student_a_level_3

# In the studio project, the other team members would have their pages imported like this.
# import student_b_level_1
# import student_b_level_2
# import student_b_level_3
# import student_c_level_1
# import student_c_level_2
# import student_c_level_3

pyhtml.need_debugging_help = True

# Register pages for the mini web server
pyhtml.MyRequestHandler.pages["/"] = student_a_level_1
pyhtml.MyRequestHandler.pages["/page2"] = student_a_level_2
pyhtml.MyRequestHandler.pages["/page3"] = student_a_level_3

# ✅ Enable query parameter parsing so form_data keeps Antigen / Year / Region values
pyhtml.enable_query_parsing = True

# Host the site
pyhtml.host_site()
