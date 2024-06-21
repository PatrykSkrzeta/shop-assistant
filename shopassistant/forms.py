from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()], render_kw={"class": "form-control logininput", "placeholder": "Enter email"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"class": "form-control logininput", "placeholder": "Password", "autocomplete": "off"})
    submit = SubmitField('Submit', render_kw={"class": "btn btn-primary"})


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Internet', 'Internet'), ('Hardware', 'Hardware'), ('Coding', 'Coding'), ('Software', 'Software'), ('Gaming', 'Gaming')], validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
    value = IntegerField('Value', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    submit = SubmitField('Add')


class OrderForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    pesel = StringField('PESEL', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    product_name = StringField('Product Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    total = FloatField('Total')
    submit = SubmitField('Add')