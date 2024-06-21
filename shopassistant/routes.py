from flask import render_template, redirect, url_for, request, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import app, login_manager
from models import User, Product, Order
from forms import LoginForm, ProductForm, OrderForm
from datetime import *
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os


@login_manager.user_loader
def load_user(user_id):
    return User.objects(email=user_id).first()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('User has login succesfully ','info')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('User logout successfully','info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/customers', methods=['GET'])
@login_required
def customers():
    search_query = request.args.get('search', '').strip()

    if search_query:
        filtered_orders = Order.objects(last_name__icontains=search_query)
    else:
        filtered_orders = Order.objects()

    total_orders = filtered_orders.count()

    return render_template('customers.html', orders=filtered_orders, total_orders=total_orders)


@app.route('/customers/delete/<order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.objects.get(id=order_id)
    order.delete()
    flash('Order deleted successfully','info')
    return redirect(url_for('customers'))

@app.route('/magazine', methods=['GET', 'POST'])
@login_required
def magazine():
    search_query = request.args.get('search', '').strip()

    if search_query:
        filtered_products = Product.objects(name__icontains=search_query)
    else:
        filtered_products = Product.objects()

    total_products = filtered_products.count()

    return render_template('magazine.html', products=filtered_products, total_products=total_products)


@app.route('/delete_product/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    flash('Product deleted successfully','info')
    return redirect(url_for('magazine'))

@app.route('/addproduct', methods=['GET', 'POST'])
@login_required
def addproduct():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            category=form.category.data,
            type=form.type.data,
            value=form.value.data,
            price=form.price.data,
            date_added=datetime.now(timezone.utc)
        )
        new_product.save()
        flash('Product added successfully')
        return redirect(url_for('addproduct'))
    return render_template('add_product.html', form=form)

@app.route('/customers/<order_id>')
@login_required
def order_details(order_id):
    try:
        order = Order.objects(id=order_id).first()
        if not order:
            flash('Order not found')
            return redirect(url_for('customers'))  

        return render_template('customers-details.html', order=order)
    except Exception as e:
        flash(f'An error occurred: {e}')
        return redirect(url_for('customers'))
    
@app.route('/addorder', methods=['GET', 'POST'])
@login_required 
def addorder():
    form = OrderForm()
    order_success = False
    order = None 
    if form.validate_on_submit():
        try:
            product = Product.objects(name=form.product_name.data).first()
            if not product:
                flash('Product not found')
                return render_template('add_order.html', form=form)

            if form.quantity.data > product.value:
                flash('Product not available in the requested quantity')
                return render_template('add_order.html', form=form)

            total_amount = product.price * form.quantity.data
            discount = 0

            if total_amount >= 500:
                discount = 0.07 * total_amount
                total_amount -= discount
                flash('Discount has been set successfully', 'info')

            product.value -= form.quantity.data

            new_order = Order(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                address=form.address.data,
                pesel=form.pesel.data,
                contact=form.contact.data,
                product_name=form.product_name.data,
                quantity=form.quantity.data,
                total=total_amount,
                discount=discount,  
                date_added=datetime.now(timezone.utc)
            )
            new_order.save()

            product.save()

            order_success = True
            order = new_order
            flash('Order added successfully','info')
            return render_template('add_order.html', form=form, order_success=order_success, order=order) 
        except Exception as e:
            flash(f'An error occurred: {e}')
    return render_template('add_order.html', form=form, order_success=order_success)

@app.route('/download_pdf/<order_id>')
def download_pdf(order_id):
    order = Order.objects(id=order_id).first()
    if not order:
        return 'Order not found', 404

    pdf_dir = 'shopassistant/pdf'
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"order_{order_id}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "Receipt")

    c.setFont("Helvetica", 12)
    y = 750
    c.drawString(50, y, f"Date: {order.date_added.strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(50, y-20, f"Customer: {order.first_name} {order.last_name}")
    c.drawString(50, y-40, f"Address: {order.address}")
    c.drawString(50, y-60, f"PESEL: {order.pesel}")
    c.drawString(50, y-80, f"Contact: {order.contact}")
    c.drawString(50, y-100, "-"*60)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y-120, "Product Name")
    c.drawString(250, y-120, "Quantity")
    c.drawString(350, y-120, "Price")

    c.setFont("Helvetica", 12)
    c.drawString(50, y-140, f"{order.product_name}")
    c.drawString(250, y-140, f"{order.quantity}")
    c.drawString(350, y-140, f"{order.total + order.discount:.2f} $")

    c.drawString(50, y-160, "-"*60)

    if order.discount > 0:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(250, y-180, "Discount:")
        c.setFont("Helvetica", 12)
        c.drawString(350, y-180, f"-{order.discount:.2f} $")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(250, y-200, "Total:")
    c.setFont("Helvetica", 14)
    c.drawString(350, y-200, f"{order.total:.2f} $")

    c.showPage()
    c.save()
    flash('PDF installed successfully', 'info')
    return send_file(pdf_path, as_attachment=True, download_name=f"order_{order_id}.pdf", mimetype='application/pdf')
    


if __name__ == '__main__':
    app.run(debug=True)
