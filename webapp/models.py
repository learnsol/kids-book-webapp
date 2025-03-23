from django.db import models

class Story(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Illustration(models.Model):
    story = models.ForeignKey(Story, related_name='illustrations', on_delete=models.CASCADE)
    image_url = models.URLField()
    description = models.TextField()

    def __str__(self):
        return f'Illustration for {self.story.title}'