import json
import razorpay
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Contact, Order, OrderUpdate
from math import ceil

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.
def index(request):
    allproducts = []
    category_products = Product.objects.values('category', 'id')
    categories = {item['category'] for item in category_products}
    for category in categories:
        products = Product.objects.filter(category=category)
        n = len(products)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        allproducts.append([products, range(1, nslides), nslides])
    p = {'allprods': allproducts}
    return render(request, 'shop/index.html', p)

def search_Match(query,item):
    if query.casefold() in item.product_name.casefold() or query.casefold() in item.category.casefold() or query.casefold() in item.description.casefold():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search',"")
    allproducts = []
    category_products = Product.objects.values('category', 'id')
    categories = {item['category'] for item in category_products}
    for category in categories:
        products_temp = Product.objects.filter(category=category)
        products = [item for item in products_temp if search_Match(query,item)]
        n = len(products)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        if n != 0:
            allproducts.append([products, range(1, nslides), nslides])

    p = {'allprods': allproducts}
    if len(allproducts) == 0 and len(query) > 0:
        p['msg'] = "Oops!No matches found.What you were looking for is not relevant.So please enter something relevant."
    return render(request, 'shop/search.html', p)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    thank = False
    if request.method == "POST":
        name = request.POST.get('name', "")
        email = request.POST.get('email', "")
        phone = request.POST.get('phone', "")
        message = request.POST.get('message', "")

        messages = Contact(name=name, email=email, phone=phone, message=message)
        messages.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id', "")
        email = request.POST.get('email', "")
        try:
            print("hello")
            order = Order.objects.filter(order_id=order_id, email=email)
            if len(order) > 0:
                update = OrderUpdate.objects.filter(order_id=order_id)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                response = json.dumps([updates, order[0].item_json], default=str)
                return HttpResponse(response, content_type="application/json")
            else:
                response = [[], '{} ']
                return HttpResponse(json.dumps(response))
        except Exception as e:
            return HttpResponse(json.dumps([[], '{}']))
    return render(request, 'shop/tracker.html')

def productview(request, myid):
    product = Product.objects.get(id=myid)
    return render(request, 'shop/productView.html', {'product': product})

def checkout(request):
    if request.method == "POST":
        user_data = {
            'item_json': request.POST.get('itemJson', ''),
            'name': request.POST.get('name', ''),
            'email': request.POST.get('email', ''),
            'address': f"{request.POST.get('address', '')} {request.POST.get('address2', '')}",
            'city': request.POST.get('city', ''),
            'state': request.POST.get('state', ''),
            'zip': request.POST.get('zip', ''),
            'phone': request.POST.get('phone', ''),
            'amount': request.POST.get('amount', '0')
        }

        options = {
            "amount": int(user_data['amount']),
            "currency": "INR",
            "receipt": "order_rcpt_inline",
            "notes": {
                "notes_name": user_data['name'],
                "notes_email": user_data['email'],
                "notes_address": user_data['address'],
                "notes_city": user_data['city'],
                "notes_state": user_data['state'],
                "notes_zip": user_data['zip'],
                "notes_phone": user_data['phone'],
                "notes_item_json": user_data['item_json'],
                "notes_amount": user_data['amount']
            }
        }
        razorpay_order = client.order.create(data=options)

        context = {
            'user_data': user_data,
            'razorpay_order_id': razorpay_order['id'],
            'amount_in_paise': options['amount'],
            'key_id': settings.RAZORPAY_KEY_ID
        }
        return render(request, 'shop/checkout_callback.html', context)

    return render(request, 'shop/checkout.html')


@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            razorpay_order = client.order.fetch(order_id)
            notes = razorpay_order.get('notes', {})

            name = notes.get('notes_name', '')
            email = notes.get('notes_email', '')
            address = notes.get('notes_address', '')
            city = notes.get('notes_city', '')
            state = notes.get('notes_state', '')
            zip = notes.get('notes_zip', '')
            phone = notes.get('notes_phone', '')
            item_json = notes.get('notes_item_json', '{}')
            amount = notes.get('notes_amount', 0)

            # Save the order
            order = Order(
                item_json=item_json, name=name, email=email, address=address,
                city=city, state=state, zip=zip, phone=phone, amount=amount
            )
            order.save()
            update = OrderUpdate(order_id=order.order_id,update_desc="The order has been placed.")
            update.save()

            return render(request, 'shop/checkout.html', {'thank': True, 'id': order.order_id})

        except razorpay.errors.SignatureVerificationError:
            return HttpResponse("Payment Validation Hash Failed.")
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}")

    return HttpResponse("Invalid request.")