from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField, SelectMultipleField, StringField
from wtforms.fields import DateField
from wtforms.validators import DataRequired
from datetime import date


class TopicModelingForm(FlaskForm):
    support_institutions = SelectMultipleField(
        "Refrerence Institutions",
        default=[],
        choices=[
            ('civil rights organization', 'Civil Rights Organization'),
            ('ethnic media', 'Ethnic Media'),
            ('executive branch', 'Executive Branch'),
            ('executive branch; immigration', 'Executive Branch - Immigration-related'),
            ('federal health agency', 'Federal Health Agency'),
            ('local health department', 'Local Health Department'),
            ('local police department', 'Local Police Department'),
            ('pharmaceutical company', 'Pharmaceutical Company'),
            ('professional organization', 'Professional Organization'),
            ('school of public health', 'School of Public Health'),
            ('state health department', 'State Health Department'),
            ('television broadcast network', 'Television Broadcast Network'),
        ],
        validators=[DataRequired()]
    )

    query_institutions = SelectMultipleField(
        "Query Institutions",
        default=[],
        choices=[
            ('civil rights organization', 'Civil Rights Organization'),
            ('ethnic media', 'Ethnic Media'),
            ('executive branch', 'Executive Branch'),
            ('executive branch; immigration', 'Executive Branch - Immigration-related'),
            ('federal health agency', 'Federal Health Agency'),
            ('local health department', 'Local Health Department'),
            ('local police department', 'Local Police Department'),
            ('pharmaceutical company', 'Pharmaceutical Company'),
            ('professional organization', 'Professional Organization'),
            ('school of public health', 'School of Public Health'),
            ('state health department', 'State Health Department'),
            ('television broadcast network', 'Television Broadcast Network'),
        ],
        validators=[DataRequired()]
    )

    support_min_date = DateField("Start Date", validators=[DataRequired()])
    support_max_date = DateField("End Date", validators=[DataRequired()])

    query_min_date = DateField("Start Date", validators=[DataRequired()])
    query_max_date = DateField("End Date", validators=[DataRequired()])

    query_step_in_days = StringField("Step in Days", validators=[DataRequired()])
    topic_counts = StringField("Number of Topics", validators=[DataRequired()])

    submit = SubmitField("Track Topics")

    def validate(self):
        if not super(TopicModelingForm, self).validate():
            return False

        def turn_to_date(x: str) -> date:
            tmp = str(x)
            date_parts = [int(e) for e in tmp.split('-')]
            return date(date_parts[0], date_parts[1], date_parts[2])

        start_date = turn_to_date(self.support_min_date.data)
        end_date = turn_to_date(self.support_max_date.data)
        date_delta = end_date - start_date
        if date_delta.days < 0:
            msg = "Please check the specified dates again."
            self.support_min_date.errors.append(msg)
            self.support_max_date.errors.append(msg)
            return False

        start_date = turn_to_date(self.query_min_date.data)
        end_date = turn_to_date(self.query_max_date.data)
        date_delta = end_date - start_date
        if date_delta.days < 0:
            msg = "Please check the specified dates again."
            self.query_min_date.errors.append(msg)
            self.query_max_date.errors.append(msg)
            return False

        try:
            step_in_days = int(self.query_step_in_days.data)
        except Exception as e:
            self.query_step_in_days.errors.append("Please enter an integer.")
            return False
        if step_in_days < 1:
            self.query_step_in_days.errors.append("Please enter an integer greater than 0.")
            return False

        try:
            topic_counts = int(self.topic_counts.data)
        except Exception as e:
            self.topic_counts.errors.append("Please enter an integer.")
            return False
        if topic_counts < 1:
            self.topic_counts.errors.append("Please enter an integer greater than 0.")
            return False

        return True
