from django.db import models

# Create your models here.
class Movie_detail(models.Model):
    name = models.CharField(max_length=50)
    director = models.CharField(max_length=50)
    image = models.CharField(max_length=200)
    rating = models.IntegerField()

    def __str__(self):
        return f"{self.name}, {self.director}, ({self.image})"


class Comment(models.Model):
    movie = models.ForeignKey(Movie_detail, on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.movie}, <{self.comment}>"
    
class Audio_store(models.Model):
    record=models.FileField(upload_to='documents/')
    class Meta:
        db_table='Audio_store'