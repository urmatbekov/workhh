from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


def image_size(value):  # add this to some file where you can import it from
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('Image too large. Size should not exceed 2 MiB.')


# Create your models here.
class Image(models.Model):
    user = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images", validators=[image_size])
    created_at = models.DateTimeField(auto_now_add=True)

    def send_to_mail(self):
        message = "{}, {}, {}".format(self.user, self.created_at, self.image)
        self.user.email_user("Image", message, from_email=settings.EMAIL_HOST_USER)

    def __str__(self):
        return str(self.user)


class ImageHistory(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    old_image = models.ImageField(upload_to="images", blank=True, null=True)
    new_image = models.ImageField(upload_to="images", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.image.user


@receiver(post_save, sender=Image)
def image_pre_save(sender, instance, created, *args, **kwargs):
    if not created:
        last_history = ImageHistory.objects.filter(image=instance.id).order_by("-created_at").first()
        if last_history:
            ImageHistory.objects.create(old_image=last_history.new_image, new_image=instance.image, image=instance)
            return
    ImageHistory.objects.create(new_image=instance.image, image=instance)
