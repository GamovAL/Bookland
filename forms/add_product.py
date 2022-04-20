from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, FileField
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    author = StringField('Автор', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    pages = IntegerField('Страниц', validators=[DataRequired()])
    cost = IntegerField('Стоимость', validators=[DataRequired()])
    image = FileField('Фото')
    pdf = FileField('Pdf')

    submit = SubmitField('Добавить')
