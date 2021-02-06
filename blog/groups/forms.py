from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
#from models import Tag


class GroupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    icon = FileField('Select post image', validators=[FileAllowed(['gif']), DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    category = SelectField('Category', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Post')


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Post')











