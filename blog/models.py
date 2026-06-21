from django.db import models

# Create your models here.
class BlogPost(models.Model):
    blog_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=500,default="")
    heading_1 = models.CharField(max_length=500,default="")
    heading_1_content = models.CharField(max_length=5000,default="")
    heading_2 = models.CharField(max_length=500,default="")
    heading_2_content = models.CharField(max_length=5000)
    sub_heading = models.CharField(max_length=500,default="")
    sub_heading_content = models.CharField(max_length=5000)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="blog/images",default="")

    def __str__(self):
        return self.title