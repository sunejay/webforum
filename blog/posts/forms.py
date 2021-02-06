from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from blog.models import Group, Tag


'''class GroupField(SelectField):
    def iter_choices(self):
        groups = [(g.id, g.name) for g in Group.query.all()]
        for value, label in groups:
            yield (value, label, self.coerce(value) == self.data)

    def pre_validate(self, form):
        for v, _ in [(g.id, g.name) for g in Group.query.all()]:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))'''


class TagField(StringField):
    def _value(self):
        if self.data:
            # Display tags as a comma-separated list.
            return ', '.join([tag.name for tag in self.data])
        return ''

    def get_tags_from_string(self, tag_string):
        raw_tags = tag_string.split(',')

        # Filter out any empty tag names.
        tag_names = [name.strip() for name in raw_tags if name.strip()]

        # Query the database and retrieve any tags we have already saved.
        existing_tags = Tag.query.filter(Tag.name.in_(tag_names))

        # Determine which tag names are new.
        new_names = set(tag_names) - set([tag.name for tag in existing_tags])

        # Create a list of unsaved Tag instances for the new tags.
        new_tags = [Tag(name=name) for name in new_names]

        # Return all the existing tags + all the new, unsaved tags.
        return list(existing_tags) + new_tags

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = self.get_tags_from_string(valuelist[0])
        else:
            self.data = []


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    group = SelectField('Community', validators=[DataRequired()], coerce=int)
    tags = TagField('Tags', description='Separate multiple tags with commas.')
    image = FileField('Select post image', validators=[FileAllowed(['jpg', 'png', 'gif'])])
    submit = SubmitField('Post')

    '''def save_tag(self, tag):
        self.populate_obj(tag)
        return tag'''


class CommentForm(FlaskForm):
    content = TextAreaField('React', validators=[DataRequired()])
    submit = SubmitField('Post')











