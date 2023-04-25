from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    s = sum(1, 3)
    # return HttpResponse(f"Search Index! Sum: {s}")

    # Get user input field from form on HTML page
    user_input = request.POST.get('user_input')

    # Pass in data to the html page (sum and user input)
    return render(request, "index.html", {"sum": s, "user_input": user_input})

# Test function, shows how to use other functions within view
def sum(num1, num2):
    return num1 + num2