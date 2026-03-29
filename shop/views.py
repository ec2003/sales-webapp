from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import Product, Transaction, ProductTransaction
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone

def about(request):
    transaction_count = Transaction.objects.count()
    # show_promo_popup = False
    show_promo_popup = transaction_count <= 100
    # if transaction_count <= 100 and not request.session.get('promo_popup_shown'):
        # show_promo_popup = True
        # request.session['promo_popup_shown'] = True
    return render(request, 'about.html', {'show_promo_popup': show_promo_popup})

def index(request):
    products = Product.objects.all()
    transaction_count = Transaction.objects.count()
    show_promo_popup = False
    # show_promo_popup = transaction_count <= 100
    # if transaction_count <= 100 and not request.session.get('promo_popup_shown'):
        # show_promo_popup = True
        # request.session['promo_popup_shown'] = True

    show_promo = transaction_count <= 100
    products_with_discount = []
    if show_promo:
        for product in products:
            products_with_discount.append({
                'product': product,
                'discounted_price': product.price * 0.7
            })
    else:
        for product in products:
            products_with_discount.append({
                'product': product,
                'discounted_price': None
            })

    return render(request, 'index.html', {
        'products_with_discount': products_with_discount, 
        'show_promo_popup': show_promo_popup,
        'show_promo': show_promo
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    transaction_count = Transaction.objects.count()
    show_promo = transaction_count <= 100
    
    discounted_price = None
    if show_promo:
        discounted_price = product.price * 0.7

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        product_id = str(pk)
        
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
        
        request.session['cart'] = cart
        messages.success(request, f"Đã thêm {quantity} {product.product_name} vào giỏ hàng.")
        return redirect('index')
        
    return render(request, 'product_detail.html', {
        'product': product,
        'show_promo': show_promo,
        'discounted_price': discounted_price
    })

def payment(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Giỏ hàng trống.")
        return redirect('index')

    cart_items = []
    total_price = 0
    total_discounted_price = 0
    
    transaction_count = Transaction.objects.count()
    show_promo = transaction_count <= 100

    products = Product.objects.filter(pk__in=[int(k) for k in cart.keys()])
    product_map = {str(p.id): p for p in products}

    for p_id, quantity in cart.items():
        if p_id in product_map:
            product = product_map[p_id]
            total = product.price * quantity
            total_price += total
            
            item = {
                'product': product,
                'quantity': quantity,
                'total': total,
                'discounted_total': None
            }
            
            if show_promo:
                discounted_total = total * 0.7
                item['discounted_total'] = discounted_total
                total_discounted_price += discounted_total
            
            cart_items.append(item)

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if phone_number:
            transaction = Transaction.objects.create(phone_number=phone_number)
            
            for item in cart_items:
                ProductTransaction.objects.create(
                    transaction=transaction,
                    product=item['product'].product_name,
                    product_count=item['quantity']
                )
            
            del request.session['cart']
            messages.success(request, "Thanh toán thành công! Đang chờ admin xác nhận.")
            return redirect('index')

    return render(request, 'payment.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discounted_price': total_discounted_price if show_promo else None,
        'show_promo': show_promo
    })

from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def admin_transactions(request):
    # Simple admin view to confirm transactions
    
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            transaction.is_confirmed = True
            transaction.save()
            messages.success(request, "Đã xác nhận đơn hàng.")
        except Transaction.DoesNotExist:
            pass
    
    transactions = Transaction.objects.all()
    period = request.GET.get('period')
    now = timezone.now()

    if period == 'day':
        transactions = transactions.filter(created_at__date=now.date())
    elif period == 'month':
        transactions = transactions.filter(created_at__year=now.year, created_at__month=now.month)
    elif period == 'year':
        transactions = transactions.filter(created_at__year=now.year)
    
    transactions = transactions.order_by('-created_at')

    # Calculate total revenue from confirmed transactions
    total_revenue = 0
    confirmed_transactions = transactions.filter(is_confirmed=True)

    # Inefficient, but required by current model structure
    product_prices = {p.product_name: p.price for p in Product.objects.all()}

    for trans in confirmed_transactions:
        for pt in trans.producttransaction_set.all():
            # if pt.product in product_prices:
            #     total_revenue += product_prices[pt.product] * pt.product_count
            if trans not in Transaction.objects.order_by('-created_at')[:100]:
                total_revenue += product_prices.get(pt.product, 0) * pt.product_count
            else:
                total_revenue += product_prices.get(pt.product, 0) * pt.product_count * 0.7
    
    return render(request, 'admin_transactions.html', {
        'transactions': transactions,
        'total_revenue': total_revenue,
        'current_period': period
        })

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def revert_transaction(request, transaction_id):
    if request.method == 'POST':
        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction.is_confirmed = False
        transaction.save()
        messages.success(request, "Đã hoàn tác xác nhận đơn hàng.")
    return redirect('admin_transactions')

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def delete_transaction(request, transaction_id):
    if request.method == 'POST':
        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction.delete()
        messages.success(request, "Đã xóa đơn hàng.")
    return redirect('admin_transactions')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect('payment')

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def add_product(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if product_name and price:
            Product.objects.create(
                product_name=product_name,
                price=price,
                description=description,
                image=image
            )
            messages.success(request, "Thêm sản phẩm thành công!")
            return redirect('admin_products')

    return render(request, 'add_product.html')

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        product.save()
        messages.success(request, "Cập nhật sản phẩm thành công!")
        return redirect('admin_products')

    return render(request, 'edit_product.html', {'product': product})

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def admin_products(request):
    products = Product.objects.all()
    return render(request, 'admin_products.html', {'products': products})

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Xóa sản phẩm thành công!")
        return redirect('admin_products')
    # Redirect to product list if not a POST request
    return redirect('admin_products')
