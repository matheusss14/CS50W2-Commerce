from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Categories(models.Model):
    category = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.category}"

class Product(models.Model):
    name = models.CharField(max_length=64)
    desc = models.TextField()
    startingBid = models.DecimalField(max_digits=100, decimal_places=2)
    image = models.URLField(null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name='prodC')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products", null=True, blank=True)
    watchlist = models.ManyToManyField(User, blank=True, null=True, related_name="watchlisted")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}: {self.desc}, owned by {self.owner}. Starting bid: {self.startingBid}, category: {self.category}, image: {self.image}"
    
class Bids(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="bid")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="biddedOn")
    bid = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return f"{self.product} recieved bid of {self.bid} from {self.bidder}"
    
class Comments(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentedOn")
    comment = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} said {self.comment} on {self.product} at {self.time}"
