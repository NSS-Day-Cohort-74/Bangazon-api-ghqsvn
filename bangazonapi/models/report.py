from django.db import models


class Report(models.Model):
    """
    Report model to store report data.
    """

    title = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "report"
        verbose_name_plural = "reports"

    def __str__(self):
        return self.title
