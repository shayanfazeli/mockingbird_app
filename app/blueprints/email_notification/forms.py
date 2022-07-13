from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import Email, Optional


class EmailNotificationForm(FlaskForm):
    email = StringField("Email", validators=[Optional(), Email()])
    submit = SubmitField("Notify me when it is done")
