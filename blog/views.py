from django.http import HttpResponse
from django.shortcuts import render
from .models import BlogPost
from django.db.models import Min, Max

# Create your views here.
def index(request):
    blogs = BlogPost.objects.all()
    parmas = {"blogs" : blogs}
    return render(request,'blog/index.html',parmas)

def blogpost(request,blog_id):
    try:
        blog = BlogPost.objects.get(blog_id=blog_id)
        id_bounds = BlogPost.objects.aggregate(min_id=Min('blog_id'), max_id=Max('blog_id'))

        context = {
            'blog': blog,
            'min_id': id_bounds['min_id'],
            'max_id': id_bounds['max_id']
        }
        return render(request,'blog/blogpost.html',context)
    except:\
        return render(request, 'blog/blogpost.html', {'no_id': True})
