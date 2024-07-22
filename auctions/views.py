from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import *

class CreateProd(forms.Form):
    name = forms.CharField()
    desc = forms.CharField(widget=forms.Textarea)
    startingBid = forms.DecimalField(decimal_places=2)
    category = forms.ModelChoiceField(queryset=Categories.objects.all())
    image = forms.URLField(required=False)

class EnterBid(forms.Form):
    value = forms.DecimalField(decimal_places=2)

class Comment(forms.Form):
    comments = forms.CharField(widget=forms.Textarea)

def index(request):
    listingss = Product.objects.filter(active=True) 
    categories = Categories.objects.all()
    bids = Bids.objects.all().order_by('bid')
    return render(request, "auctions/index.html", {
        "listings": listingss,
        "categories": categories,
        "bids": bids
    })

@login_required
def create(request):
    form = CreateProd(request.POST)
    if request.method == "POST":
        if form.is_valid():
            n1 = form.data['name']
            d1 = form.data['desc']
            sB = form.data['startingBid']
            c1 = form.data['category']
            cate = Categories.objects.get(pk=c1)
            img = form.data['image']

            final = Product(name=n1, desc=d1, startingBid=sB, category=cate, image=img, owner=request.user)
            final.save()
            return redirect('/')
        else:
            return render(request, "auctions/create.html", {
                "error": "Something went wrong: one or multiple fields were not inputed correctly.",
                "form": form
            })
            
    return render(request, "auctions/create.html", {
        "form": form
    })

def product(request, id):
    form = EnterBid(request.POST)
    hasBids = Bids.objects.filter(product=id).order_by('-bid').first()
    AllComments = Comments.objects.filter(product=id).order_by('-time')
    return render(request, "auctions/product.html", {
        "info": Product.objects.get(id=id),
        "watchlisted": Product.objects.filter(id=id, watchlist=request.user),
        "form": form,
        "bids": hasBids,
        "comment": Comment(request.POST),
        "AllComments": AllComments
    })

@login_required
def AddWatchlist(request):
    if request.method == "POST":
        product = request.POST['product']
        user = request.user
        prod = Product.objects.get(id=product)
        prod.watchlist.add(user)
        return redirect("/watchlist")
    return redirect('/')

def watchlist(request):
    user = request.user
    return render(request, "auctions/watchlist.html", {
        "list": Product.objects.filter(watchlist=user)
    })

def RemoveWatchlist(request):
    if request.method == "POST":
        user = request.user
        product = request.POST['product']
        prod = Product.objects.get(id=product)
        prod.watchlist.remove(user)
        return HttpResponseRedirect(reverse("product", args=(prod.id,)))
    
def addBid(request):
    if request.method == "POST":
        user = request.user
        product = request.POST['product']
        prod = Product.objects.get(id=product)
        value = request.POST['value']
        alreadyHasBids = Bids.objects.filter(product=prod.id)
        if alreadyHasBids:
            hasBids = Bids.objects.filter(product=prod).order_by('-bid').first()
            if float(value) > float(hasBids.bid):
                bid = Bids(product=prod, bidder=user, bid=value)
                bid.save()
                return HttpResponseRedirect(reverse("product", args=(prod.id, )))
            else:
                return render(request, "auctions/error.html", {
                    "error": "Bid must be HIGHER than the highest bid."
                })
        else:
            if float(value) > float(prod.startingBid):
                bid = Bids(product=prod, bidder=user, bid=value)
                bid.save()
                return HttpResponseRedirect(reverse("product", args=(prod.id, )))
            else:
                return render(request, "auctions/error.html", {
                    "error": "Bid must be HIGHER than the Starting bid."
                })
            
def close(request):
    if request.method == "POST":
        product = request.POST['product']
        prod = Product.objects.get(pk=product)
        prod.active = False
        prod.save()
        return HttpResponseRedirect(reverse("product", args=(product, )))
    
def comment(request):
    form = Comment(request.POST)
    if request.method == "POST":
        product = request.POST['product']
        prod = Product.objects.get(pk=product)
        user = request.user
        comment = form.data['comments']
        f = Comments(product=prod, commenter=user, comment=comment)
        f.save()
        return HttpResponseRedirect(reverse("product", args=(product,)))
    
def categories(request):
    if request.method == "POST":
        cg = request.POST['category']
        cate = Categories.objects.get(pk=cg)
        items = Product.objects.all()
        categories = Categories.objects.all()
        listingss = Product.objects.filter(active=True) 
        return render(request, "auctions/category.html", {
            "cate": cate,
            "listings": listingss,
            "categories": categories
        })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
