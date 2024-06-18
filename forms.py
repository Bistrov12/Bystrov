from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, FileField, SubmitField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    short_description = StringField('Краткое описание', validators=[DataRequired()])
    long_description = TextAreaField('Длинное описание', validators=[DataRequired()])
    price = DecimalField('Цена', validators=[DataRequired()])
    image = FileField('Изображение', validators=[DataRequired()])
    submit = SubmitField('Добавить товар')
