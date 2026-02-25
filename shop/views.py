from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Transaction, ProductTransaction
from django.contrib.auth.decorators import user_passes_test

def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
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
        
    return render(request, 'product_detail.html', {'product': product})

def payment(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Giỏ hàng trống.")
        return redirect('index')

    cart_items = []
    total_price = 0
    
    # Retrieve product details for items in cart
    products = Product.objects.filter(pk__in=[int(k) for k in cart.keys()])
    product_map = {str(p.id): p for p in products}

    for p_id, quantity in cart.items():
        if p_id in product_map:
            product = product_map[p_id]
            total = product.price * quantity
            total_price += total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': total
            })

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if phone_number:
            # Create Transaction
            transaction = Transaction.objects.create(phone_number=phone_number)
            
            # Create Product_Transaction records
            for item in cart_items:
                ProductTransaction.objects.create(
                    transaction=transaction,
                    product=item['product'].product_name,
                    product_count=item['quantity']
                )
            
            # Clear cart
            del request.session['cart']
            messages.success(request, "Thanh toán thành công! Đang chờ admin xác nhận.")
            return redirect('index')

    return render(request, 'payment.html', {
        'cart_items': cart_items,
        'total_price': total_price
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
    
    transactions = Transaction.objects.all().order_by('-created_at')
    return render(request, 'admin_transactions.html', {'transactions': transactions})

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng.")
    return redirect('payment')
